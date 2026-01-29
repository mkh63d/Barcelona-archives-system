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


def route_query(query: str) -> Dict:
    """
    Router prompt to classify user intent and determine appropriate action.
    
    Args:
        query: User's input message
        
    Returns:
        Dict with route classification and metadata
    """
    try:
        llm = get_llm()
        
        router_prompt = f"""You are a query router for the Barcelona Historical Archives Assistant. 
Your job is to classify the user's intent into ONE of these categories:

1. CASUAL - Greetings, personal questions, casual conversation, random words with no archive context
   Examples: "Hi", "Hello", "How are you?", "What's your name?", "Tree", "Car", "Tell me a joke"

2. ARCHIVE_QUERY - Legitimate questions about historical archives, documents, broadcasts, events, dates
   Examples: "What happened in 1945?", "Find documents about Radio Barcelona", "censored broadcasts"

3. CLARIFICATION - Ambiguous or vague input that needs clarification
   Examples: "that thing", "the other one", single ambiguous words in archive context

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


def generate_response_by_route(query: str, route: str) -> str:
    """
    Generate dynamic response based on route using LLM.
    
    Args:
        query: User's input message
        route: Route classification (CASUAL or CLARIFICATION)
        
    Returns:
        Generated response string
    """
    try:
        llm = get_llm()
        
        if route == "CASUAL":
            system_prompt = """You are the Expert Archivist for the Radio Barcelona Historical Archives.
The user has sent a casual message (greeting, personal question, or off-topic comment).

Respond warmly and professionally, then guide them toward using the archives:
- If it's a greeting, welcome them and briefly explain what you can help with
- If it's off-topic, politely acknowledge and redirect to archive research
- Keep it concise (2-3 sentences)
- Invite them to ask about historical documents, broadcasts, or events"""

        elif route == "CLARIFICATION":
            system_prompt = """You are the Expert Archivist for the Radio Barcelona Historical Archives.
The user's query is too vague or ambiguous to search the archives effectively.

Ask for clarification in a helpful way:
- Point out what's unclear about their request
- Give 2-3 specific examples of how they could rephrase
- Suggest types of information they might search for (dates, topics, people, events)
- Keep it helpful and encouraging"""

        else:
            # Shouldn't reach here, but fallback
            return "I'm here to help with historical archive research. What would you like to know?"
        
        messages = [
            SystemMessage(content=system_prompt),
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


def process_query(query: str) -> dict:
    """
    Process a user query using RAG (Retrieval Augmented Generation) with LangChain.
    
    Flow:
    1. Route query to determine intent (casual, archive query, clarification)
    2. Handle accordingly:
       - CASUAL: Generate friendly response without RAG
       - ARCHIVE_QUERY: Retrieve documents and generate RAG response
       - CLARIFICATION: Ask for more details
    
    Args:
        query: User's question
        
    Returns:
        Dict containing response, query, sources, and metadata
    """
    try:
        llm = get_llm()
        
        # Step 1: Route the query to determine intent
        logger.info(f"🔍 Routing query: {query[:100]}...")
        route_result = route_query(query)
        route = route_result.get("route", "ARCHIVE_QUERY")
        
        # Step 2: Handle based on route
        if route in ["CASUAL", "CLARIFICATION"]:
            # Generate dynamic response without RAG
            response_content = generate_response_by_route(query, route)
            
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
        
        # Create RAG prompt with retrieved context
        system_prompt = """You are the Expert Archivist for the Radio Barcelona Historical Archives.
Your mission is to assist users in exploring historical documents from various eras.

OPERATING GUIDELINES:

1.  **STRICT SOURCE GROUNDING:**
    * Answer ONLY based on the "RETRIEVED ARCHIVE DOCUMENTS" provided below.
    * If the answer is not in the documents, state clearly: "I cannot find information about this in the available archives." Do not invent facts.

2.  **HISTORICAL CONTEXT & NEUTRALITY:**
    * You are analyzing historical documents that may contain propaganda, censorship, or biased language from their respective eras.
    * **CRITICAL:** Do not treat political statements in the text as absolute facts. Use phrases like "The document states...", "According to the broadcast...", or "The censorship log notes...".
    * If censorship markings (e.g., crossed-out text) are visible/mentioned, point them out.

3.  **MANDATORY CITATIONS:**
    * Every fact must be backed by a source.
    * Format: (Source: [filename]) -> "Quote/Paraphrase"

4.  **LANGUAGE MIRRORING:**
    * Always answer in the same language as the USER QUESTION (e.g., Polish for Polish queries).

5.  **UNCERTAINTY:**
    * If a document is illegible or the query is ambiguous based on the available files, ask the user to narrow down their search."""

        user_prompt = f"""Based on the following retrieved documents, answer the user's question following the Operating Guidelines.

RETRIEVED ARCHIVE DOCUMENTS:
{context}

USER QUESTION: {query}

Provide a comprehensive response."""
        
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
