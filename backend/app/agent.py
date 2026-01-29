from typing import Optional, List, Dict
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
import os
import logging

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


def process_query(query: str) -> dict:
    """
    Process a user query using RAG (Retrieval Augmented Generation) with LangChain.
    
    Flow:
    1. Retrieve relevant documents from Qdrant using CLIP embeddings
    2. Build context from retrieved documents
    3. Generate response using LLM with context
    
    Args:
        query: User's question
        
    Returns:
        Dict containing response, query, sources, and metadata
    """
    try:
        llm = get_llm()
        
        # Step 1: Retrieve relevant context from vector database
        logger.info(f"🔍 Processing query with RAG: {query[:100]}...")
        context, source_documents = retrieve_context(query, top_k=3)
        
        # Step 2: Create RAG prompt with retrieved context
        system_prompt = """You are the Expert Archivist for the Radio Barcelona Historical Archives.
Your mission is to assist users in exploring historical documents from various eras.

OPERATING GUIDELINES:

1.  **HANDLING VAGUE, SHORT, OR CHIT-CHAT INPUTS (PRIORITY):**
    * If the user input is a greeting ("Hi", "Hello"), a single random word (e.g., "Tree", "Car"), or a personal question ("How are you?", "How old are you?"), DO NOT search the archives.
    * **ACTION:** Ignore the retrieved documents. Respond politely as the Archivist and ASK FOR CLARIFICATION.
    * *Example:* User says "Tree". You say: "I am an archivist. Are you looking for a specific broadcast about nature, or a family tree mentioned in a document? Please specify."

2.  **STRICT SOURCE GROUNDING:**
    * Answer ONLY based on the "RETRIEVED ARCHIVE DOCUMENTS" provided below.
    * If the answer is not in the documents, state clearly: "I cannot find information about this in the available archives." Do not invent facts.

3.  **HISTORICAL CONTEXT & NEUTRALITY:**
    * You are analyzing historical documents that may contain propaganda, censorship, or biased language from their respective eras.
    * **CRITICAL:** Do not treat political statements in the text as absolute facts. Use phrases like "The document states...", "According to the broadcast...", or "The censorship log notes...".
    * If censorship markings (e.g., crossed-out text) are visible/mentioned, point them out.

4.  **MANDATORY CITATIONS:**
    * Every fact must be backed by a source.
    * Format: (Source: [filename]) -> "Quote/Paraphrase"

5.  **LANGUAGE MIRRORING:**
    * Always answer in the same language as the USER QUESTION (e.g., Polish for Polish queries).

6.  **UNCERTAINTY:**
    * If a document is illegible or the query is ambiguous based on the available files, ask the user to narrow down their search.
"""

        user_prompt = f"""Based on the following retrieved documents, answer the user's question following the Operating Guidelines.

RETRIEVED ARCHIVE DOCUMENTS:
{context}

USER QUESTION: {query}

Provide a comprehensive response."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        # Step 3: Generate response using LLM
        logger.info("💬 Generating response with LLM...")
        response = llm.invoke(messages)
        
        logger.info("✅ Query processed successfully with RAG")
        
        return {
            "response": response.content,
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
