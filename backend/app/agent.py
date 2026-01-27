from typing import Optional
from langchain_core.messages import HumanMessage
import os


def get_llm():
    """Get the appropriate LLM based on environment configuration."""
    provider = os.getenv("MODEL_PROVIDER", "gemini").lower()
    model_name = os.getenv("MODEL_NAME", "gemini-1.5-flash")
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


def search_archives(query: str) -> list[dict]:
    """Search for archives based on the query."""
    from app.routes.archives import mock_archives
    
    query_lower = query.lower()
    
    # Search in mock data
    results = [
        archive for archive in mock_archives
        if query_lower in archive["title"].lower() 
        or query_lower in archive["description"].lower()
        or query_lower in archive["category"].lower()
    ]
    
    # If no specific search, return all
    if not results and len(query.split()) < 3:
        results = mock_archives
    
    return results


def process_query(query: str) -> dict:
    """Process a user query and generate a response using LangChain."""
    try:
        llm = get_llm()
        
        # Search archives
        archives = search_archives(query)
        
        # Prepare context
        if archives:
            archives_context = "\n".join([
                f"- {a['title']} ({a['category']}, {a['date']}): {a['description']}"
                for a in archives[:5]  # Limit to top 5 results
            ])
            context = f"Found {len(archives)} archives:\n{archives_context}"
        else:
            context = "No archives found matching the query."
        
        # Create prompt
        system_prompt = """You are a helpful assistant for the Barcelona Archives System. 
Your role is to help users find and understand historical archives.
Be concise, informative, and friendly. Format your response in a clear, readable way.
If archives are found, briefly describe them and suggest how they might be useful.
If no archives are found, suggest alternative search terms or categories."""
        
        user_message = f"User query: {query}\n\nAvailable archives:\n{context}\n\nProvide a helpful response to the user."
        
        messages = [
            HumanMessage(content=f"{system_prompt}\n\n{user_message}")
        ]
        
        response = llm.invoke(messages)
        
        return {
            "response": response.content,
            "archives": archives,
            "query": query
        }
        
    except Exception as e:
        # Fallback response if LLM fails
        archives = search_archives(query)
        if archives:
            response_text = f"I found {len(archives)} archives matching your query:\n\n"
            for i, archive in enumerate(archives[:3], 1):
                response_text += f"{i}. **{archive['title']}**\n"
                response_text += f"   {archive['description']}\n"
                response_text += f"   Category: {archive['category']} | Period: {archive['date']}\n\n"
            if len(archives) > 3:
                response_text += f"...and {len(archives) - 3} more results."
        else:
            response_text = "I couldn't find any archives matching your query. Try searching for categories like Municipal, Architecture, Civil Registry, Labor, or Photography."
        
        print(f"LLM Error: {e}")
        
        return {
            "response": response_text,
            "archives": archives,
            "query": query
        }
