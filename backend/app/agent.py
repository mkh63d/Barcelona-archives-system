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


def process_query(query: str) -> dict:
    """Process a user query and generate a response using LangChain."""
    try:
        llm = get_llm()
        
        # Create prompt for Barcelona Archives assistant
        system_prompt = """You are a helpful AI assistant for the Barcelona Archives System. 
Your role is to help users with questions about historical archives, provide information, 
and assist with general queries. Be concise, informative, and friendly."""
        
        user_message = f"User query: {query}\n\nProvide a helpful response to the user."
        
        messages = [
            HumanMessage(content=f"{system_prompt}\n\n{user_message}")
        ]
        
        response = llm.invoke(messages)
        
        return {
            "response": response.content,
            "query": query
        }
        
    except Exception as e:
        # Fallback response if LLM fails
        return {
            "response": f"I apologize, but I'm having trouble processing your request. Error: {str(e)}",
            "query": query
        }
