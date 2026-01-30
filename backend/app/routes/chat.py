from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
from pathlib import Path

router = APIRouter()


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    history: Optional[List[ChatMessage]] = []


class SourceDocument(BaseModel):
    filename: str
    relevance_score: float
    preview: str
    has_watermark: bool = False
    page_number: Optional[int] = None
    web_url: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    sources: Optional[list[SourceDocument]] = []
    context_used: bool = False
    num_sources: int = 0


class ModelConfig(BaseModel):
    provider: str
    model_name: str
    temperature: float
    api_key_set: bool


class ModelConfigUpdate(BaseModel):
    provider: Optional[str] = None
    model_name: Optional[str] = None
    temperature: Optional[float] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat message using RAG (Retrieval Augmented Generation)
    
    Flow:
    1. User sends message
    2. System retrieves relevant documents from Qdrant vector database
    3. LangChain generates response based on retrieved context
    4. Returns response with source document citations
    """
    from app.agent import process_query
    import uuid
    
    try:
        # Convert history to dict format for agent
        history = [{'role': msg.role, 'content': msg.content} for msg in (request.history or [])]
        
        # Process the query with RAG and conversation history
        result = process_query(request.message, history=history)
        
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        return ChatResponse(
            response=result["response"],
            conversation_id=conversation_id,
            sources=result.get("sources", []),
            context_used=result.get("context_used", False),
            num_sources=result.get("num_sources", 0)
        )
    except ValueError as e:
        # Handle API key not set error
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )


@router.get("/model/config", response_model=ModelConfig)
async def get_model_config():
    """
    Get current model configuration
    """
    provider = os.getenv("MODEL_PROVIDER", "gemini")
    openai_key = os.getenv("OPENAI_API_KEY", "")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
    google_key = os.getenv("GOOGLE_API_KEY", "")
    
    api_key_set = False
    if provider == "openai" and openai_key:
        api_key_set = True
    elif provider == "anthropic" and anthropic_key:
        api_key_set = True
    elif provider == "gemini" and google_key:
        api_key_set = True
    
    return ModelConfig(
        provider=provider,
        model_name=os.getenv("MODEL_NAME", "gemini-1.5-flash"),
        temperature=float(os.getenv("MODEL_TEMPERATURE", "0.7")),
        api_key_set=api_key_set
    )


@router.post("/model/config")
async def update_model_config(config: ModelConfigUpdate):
    """
    Update model configuration (in-memory only, requires restart to persist)
    Note: In production, this should update a database or config file
    """
    if config.provider:
        os.environ["MODEL_PROVIDER"] = config.provider
    
    if config.model_name:
        os.environ["MODEL_NAME"] = config.model_name
    
    if config.temperature is not None:
        os.environ["MODEL_TEMPERATURE"] = str(config.temperature)
    
    if config.openai_api_key:
        os.environ["OPENAI_API_KEY"] = config.openai_api_key
    
    if config.anthropic_api_key:
        os.environ["ANTHROPIC_API_KEY"] = config.anthropic_api_key
    
    if config.google_api_key:
        os.environ["GOOGLE_API_KEY"] = config.google_api_key
    
    return {"message": "Configuration updated successfully"}


@router.get("/model/providers")
async def get_providers():
    """
    Get available model providers
    """
    return {
        "providers": [
            {
                "id": "gemini",
                "name": "Google Gemini",
                "models": ["gemini-2.5-flash", "gemini-1.5-pro", "gemini-1.0-pro"]
            },
            {
                "id": "openai",
                "name": "OpenAI",
                "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
            },
            {
                "id": "anthropic",
                "name": "Anthropic",
                "models": ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022", "claude-3-opus-20240229"]
            }
        ]
    }


@router.get("/document/{filename}")
async def get_full_document(filename: str):
    """
    Get the full content of a document by filename
    Searches for the document in the pipeline/exampleFile directory
    """
    try:
        # Define the documents directory path
        base_dir = Path(__file__).parent.parent.parent.parent  # Go up to project root
        docs_dir = base_dir / "pipeline" / "exampleFile"
        
        # Security: Prevent directory traversal
        filename = Path(filename).name
        
        # Try to find the file
        file_path = docs_dir / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"Document '{filename}' not found")
        
        # Read the file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # If UTF-8 fails, try other encodings
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
        
        return {
            "filename": filename,
            "content": content,
            "file_type": file_path.suffix[1:] if file_path.suffix else "txt"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading document: {str(e)}"
        )
