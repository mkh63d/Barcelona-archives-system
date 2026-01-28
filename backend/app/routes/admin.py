"""
Admin routes for system monitoring and RAG status
"""

from fastapi import APIRouter
from pydantic import BaseModel
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


class VectorDBStatus(BaseModel):
    qdrant_connected: bool
    collection_exists: bool
    vectors_count: int
    points_count: int
    status: str


@router.get("/admin/rag-status", response_model=VectorDBStatus)
async def get_rag_status():
    """
    Get RAG system status including Qdrant connection and collection info
    """
    try:
        from app.rag_retriever import RAGRetriever
        
        retriever = RAGRetriever()
        collection_status = retriever.check_collection_status()
        
        return VectorDBStatus(
            qdrant_connected=True,
            collection_exists=collection_status.get("exists", False),
            vectors_count=collection_status.get("vectors_count", 0),
            points_count=collection_status.get("points_count", 0),
            status=collection_status.get("status", "unknown")
        )
    except Exception as e:
        logger.error(f"Error checking RAG status: {e}")
        return VectorDBStatus(
            qdrant_connected=False,
            collection_exists=False,
            vectors_count=0,
            points_count=0,
            status=f"error: {str(e)}"
        )
