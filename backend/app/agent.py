from typing import Optional, List, Dict
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
import os
import logging
import json
import re

logger = logging.getLogger(__name__)

# Lazy import for RAG retriever
_rag_retriever = None


def get_rag_retriever():
    """Lazy initialization of RAG retriever"""
    global _rag_retriever
    if _rag_retriever is None:
        from app.rag_retriever import RAGRetriever
        _rag_retriever = RAGRetriever()
    return _rag_retriever


def get_llm():
    """Get the appropriate LLM based on environment configuration."""
    provider = os.getenv("MODEL_PROVIDER", "gemini").lower()
    model_name = os.getenv("MODEL_NAME", "gemini-2.5-flash")
    temperature = float(os.getenv("MODEL_TEMPERATURE", "0.7"))
    
    if provider == "openai":
        from langchain_openai import ChatOpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")
        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=api_key
        )
    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set in environment")
        return ChatAnthropic(
            model=model_name,
            temperature=temperature,
            api_key=api_key
        )
    elif provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not set in environment")
        return ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            google_api_key=api_key
        )
    else:
        raise ValueError(f"Unsupported model provider: {provider}")


def route_query(query: str, history: Optional[List[Dict]] = None) -> Dict:
    """
    Router prompt to classify user intent and determine appropriate action.
    
    Args:
        query: User's input message
        history: Previous conversation messages
        
    Returns:
        Dict with route classification and metadata
    """
    try:
        llm = get_llm()
        
        # Build context from history if available
        history_context = ""
        if history and len(history) > 0:
            history_context = "\n\nPrevious conversation context:\n"
            for msg in history[-4:]:  # Last 4 messages for context
                history_context += f"{msg['role'].upper()}: {msg['content'][:100]}...\n"
        
        router_prompt = f"""You are a query router for the Barcelona Historical Archives Assistant. 
Your job is to classify the user's intent into ONE of these categories:

1. CASUAL - Greetings, personal questions, casual conversation, random words with no archive context
   Examples: "Hi", "Hello", "How are you?", "What's your name?", "Tree", "Car", "Tell me a joke"

2. ARCHIVE_QUERY - Legitimate questions about historical archives, documents, broadcasts, events, dates
   Examples: "What happened in 1945?", "Find documents about Radio Barcelona", "censored broadcasts"
   NOTE: Follow-up questions like "tell me more", "what else?", "can you elaborate?" are ARCHIVE_QUERY if there's conversation history.

3. CLARIFICATION - Ambiguous or vague input that needs clarification
   Examples: "that thing", "the other one", single ambiguous words in archive context{history_context}

Respond ONLY with a JSON object in this exact format:
{{"route": "CASUAL", "confidence": 0.95, "reasoning": "brief explanation"}}

User input: {query}"""

        messages = [
            HumanMessage(content=router_prompt)
        ]
        
        response = llm.invoke(messages)
        
        # Parse the JSON response
        try:
            # Extract content from response
            content = response.content if isinstance(response.content, str) else str(response.content)
            content = content.strip()
            
            # Remove markdown code blocks if present
            if "```" in content:
                # Extract content between code blocks
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
                if json_match:
                    content = json_match.group(1)
                else:
                    # Try to find JSON without code blocks
                    json_match = re.search(r'\{.*?\}', content, re.DOTALL)
                    if json_match:
                        content = json_match.group(0)
            
            result = json.loads(content.strip())
            
            # Validate the route is one of the expected values
            valid_routes = ["CASUAL", "ARCHIVE_QUERY", "CLARIFICATION"]
            if result.get("route") not in valid_routes:
                logger.warning(f"Invalid route '{result.get('route')}', defaulting to ARCHIVE_QUERY")
                result["route"] = "ARCHIVE_QUERY"
            
            logger.info(f"🔀 Router classified query as: {result['route']} (confidence: {result.get('confidence', 0.5)})")
            return result
            
        except (json.JSONDecodeError, KeyError, AttributeError) as e:
            # Fallback: assume it's an archive query if parsing fails
            logger.warning(f"Failed to parse router response: {e}, defaulting to ARCHIVE_QUERY")
            return {
                "route": "ARCHIVE_QUERY",
                "confidence": 0.5,
                "reasoning": "Parser fallback"
            }
            
    except Exception as e:
        logger.error(f"❌ Error in query router: {e}")
        # Safe fallback
        return {
            "route": "ARCHIVE_QUERY",
            "confidence": 0.5,
            "reasoning": f"Router error: {str(e)}"
        }


def retrieve_context(query: str, top_k: int = 3) -> tuple[str, List[Dict]]:
    """
    Retrieve relevant context from vector database using RAG.
    
    Args:
        query: User's question
        top_k: Number of documents to retrieve
        
    Returns:
        Tuple of (formatted context string, list of source documents)
    """
    try:
        retriever = get_rag_retriever()
        
        # Retrieve relevant documents
        documents = retriever.retrieve_context(query, top_k=top_k)
        
        if not documents:
            return "No relevant documents found in the archives.", []
        
        # Format context from retrieved documents
        context_parts = []
        for idx, doc in enumerate(documents, 1):
            context_parts.append(
                f"[Document {idx}: {doc['filename']} - Relevance: {doc['score']:.2%}]\n"
                f"{doc['content']}\n"
            )
        
        context = "\n" + "="*80 + "\n".join(context_parts)
        logger.info(f"✅ Retrieved {len(documents)} documents for RAG context")
        
        return context, documents
        
    except Exception as e:
        logger.error(f"❌ Error retrieving context: {e}")
        return f"Error accessing archives database: {str(e)}", []


def generate_response_by_route(query: str, route: str, conversation_context: str = "") -> str:
    """
    Generate dynamic response based on route using LLM.
    
    Args:
        query: User's input message
        route: Route classification (CASUAL or CLARIFICATION)
        conversation_context: Previous conversation messages formatted as string
        
    Returns:
        Generated response string
    """
    try:
        llm = get_llm()
        
        if route == "CASUAL":
            system_prompt = """You are a friendly assistant for the Radio Barcelona Historical Archives.

The user is having a casual conversation (greetings, personal questions, general chat).

IMPORTANT RULES:
1. You MUST remember information from the conversation history
2. If the user asks about something they told you (name, preferences, etc.), recall it from the conversation history
3. For greetings, be warm and welcoming
4. For personal questions about the user, use conversation memory
5. For off-topic questions, politely redirect to archive topics while staying friendly
6. Always maintain conversation continuity and remember what was discussed
7. Always respond in a language the user used in their message, unless requested otherwise

Be natural, friendly, and conversational while remembering the context."""

        elif route == "CLARIFICATION":
            system_prompt = """You are a helpful assistant for the Radio Barcelona Historical Archives.

The user's question is unclear or ambiguous.

IMPORTANT RULES:
1. Check conversation history for context that might clarify their question
2. If they're referring to something from previous messages, acknowledge it
3. Ask specific questions to understand what they need
4. Provide examples of what kind of information they might be looking for
5. Be helpful and guide them toward clearer questions
6. Always respond in a language the user used in their message, unless requested otherwise

Be patient and constructive."""

        else:
            # Shouldn't reach here, but fallback
            return "I'm here to help with historical archive research. What would you like to know?"
        
        # Include conversation context in the prompt
        full_prompt = system_prompt
        if conversation_context:
            full_prompt += f"\n\n{conversation_context}"
        
        messages = [
            SystemMessage(content=full_prompt),
            HumanMessage(content=f"User message: {query}\n\nGenerate an appropriate response:")
        ]
        
        response = llm.invoke(messages)
        
        # Handle both string and list responses
        response_text = response.content if isinstance(response.content, str) else str(response.content)
        return response_text
        
    except Exception as e:
        logger.error(f"❌ Error generating response: {e}")
        # Fallback response
        if route == "CASUAL":
            return "Hello! I'm the Barcelona Archives Assistant. How can I help you explore our historical documents today?"
        else:
            return "Could you please provide more details about what you're looking for in the archives?"


def process_query(query: str, history: Optional[List[Dict]] = None) -> dict:
    """
    Process a user query using RAG (Retrieval Augmented Generation) with LangChain.
    
    Flow:
    1. Route query to determine intent (casual, archive query, clarification)
    2. Handle accordingly:
       - CASUAL: Generate friendly response without RAG
       - ARCHIVE_QUERY: Retrieve documents and generate RAG response with history
       - CLARIFICATION: Ask for more details
    
    Args:
        query: User's question
        history: Previous conversation messages (list of dicts with 'role' and 'content')
        
    Returns:
        Dict containing response, query, sources, and metadata
    """
    try:
        llm = get_llm()
        
        # Ensure history is a list
        if history is None:
            history = []
        
        # Step 1: Route the query to determine intent
        logger.info(f"🔍 Routing query: {query[:100]}... (with {len(history)} previous messages)")
        route_result = route_query(query, history=history)
        route = route_result.get("route", "ARCHIVE_QUERY")
        
        # Step 2: Handle based on route
        if route in ["CASUAL", "CLARIFICATION"]:
            # Build conversation context for casual/clarification
            conversation_context = ""
            if history and len(history) > 0:
                recent_history = history[-6:]  # Last 6 messages for context
                conversation_context = "\n\nCONVERSATION HISTORY:\n"
                for msg in recent_history:
                    role = "User" if msg.get("role") == "user" else "Assistant"
                    conversation_context += f"{role}: {msg.get('content', '')}\n"
            
            # Generate dynamic response with conversation memory
            response_content = generate_response_by_route(query, route, conversation_context)
            
            logger.info(f"✅ Responded to {route} query")
            return {
                "response": response_content,
                "query": query,
                "sources": [],
                "context_used": False,
                "num_sources": 0
            }
        
        # Step 3: ARCHIVE_QUERY - Use full RAG pipeline
        logger.info(f"📚 Processing archive query with RAG...")
        context, source_documents = retrieve_context(query, top_k=3)
        
        # Build conversation history context
        history_text = ""
        if history and len(history) > 0:
            history_text = "\n\nCONVERSATION HISTORY (for context continuity):\n"
            for msg in history[-6:]:  # Last 6 messages for context
                role = "User" if msg.get('role') == 'user' else "Assistant"
                history_text += f"{role}: {msg.get('content', '')}\n"
        
        # Create RAG prompt with retrieved context and conversation history
        system_prompt = f"""You are an Expert Archivist for Radio Barcelona's Historical Archives.

YOUR PRIMARY SOURCES:
{context}

GUIDELINES:
1. ANSWER PRIMARILY from the retrieved archive documents above
2. For ARCHIVE QUESTIONS: Ground your response in the documents, cite sources explicitly
3. For PERSONAL/CONVERSATIONAL QUESTIONS: You may answer from conversation history without requiring archive sources
4. Use conversation history to maintain context and remember user information (names, preferences, previous topics)
5. If asked about previous conversation ("what did I say?", "my name?", etc.), answer from conversation history
6. If archive documents are relevant, prioritize them; if not relevant, use conversation memory
7. Be helpful, accurate, and distinguish between archive knowledge and conversation memory
8. Cite sources when using archive documents: [Source: filename]
9. If archive documents don't contain the answer but it's in conversation history, say so explicitly
10. Always respond in a language the user used in their message, unless requested otherwise or quoting archive content

CONVERSATION CONTINUITY:
- Remember user information shared in this conversation
- Reference previous topics when relevant
- Maintain conversational flow across multiple questions{history_text}

Current user question: {query}

Provide a helpful, accurate response."""

        user_prompt = query
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        # Generate response using LLM
        logger.info("💬 Generating response with LLM...")
        response = llm.invoke(messages)
        
        # Handle both string and list responses
        response_text = response.content if isinstance(response.content, str) else str(response.content)
        
        logger.info("✅ Query processed successfully with RAG")
        
        return {
            "response": response_text,
            "query": query,
            "sources": [
                {
                    "filename": doc.get("source", doc["filename"]),
                    "relevance_score": doc["score"],
                    "preview": doc["content"][:200] + "..." if len(doc["content"]) > 200 else doc["content"],
                    "has_watermark": doc.get("has_watermark", False),
                    "page_number": doc.get("page_number"),
                    "web_url": doc.get("web_url")
                }
                for doc in source_documents
            ],
            "context_used": True,
            "num_sources": len(source_documents)
        }
        
    except Exception as e:
        logger.error(f"❌ Error processing query with RAG: {e}")
        # Fallback response if RAG fails
        return {
            "response": f"I apologize, but I'm having trouble accessing the archives database. Error: {str(e)}",
            "query": query,
            "sources": [],
            "context_used": False,
            "num_sources": 0
        }
