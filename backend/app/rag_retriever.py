"""
RAG Retriever Module
Handles document retrieval from Qdrant vector database
"""

import os
import logging
from typing import List, Dict, Optional
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import numpy as np

logger = logging.getLogger(__name__)


class RAGRetriever:
    """Retriever for RAG system using Qdrant vector database"""
    
    def __init__(self):
        self.qdrant_host = os.getenv("QDRANT_HOST", "localhost")
        self.qdrant_port = int(os.getenv("QDRANT_PORT", 6333))
        self.collection_name = "barcelona_archives"
        
        # Initialize Qdrant client
        logger.info(f"Connecting to Qdrant at {self.qdrant_host}:{self.qdrant_port}")
        self.client = QdrantClient(host=self.qdrant_host, port=self.qdrant_port)
        
        # Initialize embedding model (same as pipeline)
        logger.info("Loading embedding model for RAG...")
        self.model = SentenceTransformer("sentence-transformers/clip-ViT-B-32-multilingual-v1")
        logger.info("✅ RAG retriever initialized")
    
    def retrieve_context(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Retrieve relevant documents from Qdrant based on query
        
        Args:
            query: User's question
            top_k: Number of top documents to retrieve
            
        Returns:
            List of relevant documents with metadata
        """
        try:
            # Encode query using same model as pipeline
            logger.info(f"Encoding query: {query[:50]}...")
            query_embedding = self.model.encode(query, convert_to_numpy=True)
            
            # Search Qdrant
            logger.info(f"Searching Qdrant collection '{self.collection_name}'...")
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding.tolist(),
                limit=top_k,
                with_payload=True,
                with_vectors=False
            )
            
            # Format results
            documents = []
            for result in search_results:
                doc = {
                    "id": result.id,
                    "score": float(result.score),
                    "filename": result.payload.get("filename", "Unknown"),
                    "content": result.payload.get("full_content", ""),
                    "file_type": result.payload.get("file_type", "text")
                }
                documents.append(doc)
                logger.info(f"  ✓ Retrieved: {doc['filename']} (score: {doc['score']:.3f})")
            
            logger.info(f"✅ Retrieved {len(documents)} documents")
            return documents
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []
    
    def check_collection_status(self) -> Dict:
        """Check status of Qdrant collection"""
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                "exists": True,
                "vectors_count": collection_info.vectors_count,
                "points_count": collection_info.points_count,
                "status": "ready"
            }
        except Exception as e:
            logger.error(f"Collection status check failed: {e}")
            return {
                "exists": False,
                "error": str(e),
                "status": "unavailable"
            }
