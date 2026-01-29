"""
Pipeline V2 - Migrate data from Chroma DB to Qdrant
Reads documents with pre-computed embeddings from Chroma and stores them in Qdrant
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Add the parent directory to sys.path to import from db folder
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ChromaToQdrantMigrator:
    """Migrate documents from Chroma DB to Qdrant"""
    
    def __init__(self):
        # Qdrant connection
        self.qdrant_host = os.getenv("QDRANT_HOST", "localhost")
        self.qdrant_port = int(os.getenv("QDRANT_PORT", 6333))
        self.collection_name = "barcelona_archives"
        
        logger.info(f"Connecting to Qdrant at {self.qdrant_host}:{self.qdrant_port}")
        self.qdrant_client = QdrantClient(host=self.qdrant_host, port=self.qdrant_port)
        
        # Chroma configuration
        self.chroma_persist_dir = os.getenv("CHROMA_PERSIST_DIR", "../db/data_chroma")
        self.chroma_collection_name = os.getenv("CHROMA_COLLECTION_NAME", "data_collection")
        self.embedding_model = os.getenv("CHROMA_EMBEDDING_MODEL", "paraphrase-multilingual-MiniLM-L12-v2")
        
        # Initialize embeddings model
        logger.info(f"Loading embedding model: {self.embedding_model}")
        self.embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model)
        
        # Get embedding dimension
        sample_embedding = self.embeddings.embed_query("test")
        self.embedding_dim = len(sample_embedding)
        logger.info(f"✅ Embedding dimension: {self.embedding_dim}")
        
        # Initialize Chroma
        self._init_chroma()
        
        # Clean and initialize Qdrant collection
        self._init_qdrant_collection()
    
    def _init_chroma(self):
        """Initialize Chroma vector store"""
        try:
            # Get the absolute path to the persist directory
            if os.path.isabs(self.chroma_persist_dir):
                absolute_persist_dir = Path(self.chroma_persist_dir)
            else:
                # Resolve relative to the pipeline directory
                pipeline_dir = Path(__file__).parent
                absolute_persist_dir = (pipeline_dir / self.chroma_persist_dir).resolve()
            
            logger.info(f"Loading Chroma DB from: {absolute_persist_dir}")
            
            if not absolute_persist_dir.exists():
                raise FileNotFoundError(f"Chroma DB directory not found: {absolute_persist_dir}")
            
            # Load the persisted Chroma vector store
            self.chroma_vectorstore = Chroma(
                persist_directory=str(absolute_persist_dir),
                embedding_function=self.embeddings,
                collection_name=self.chroma_collection_name,
            )
            
            # Get document count
            doc_count = self.chroma_vectorstore._collection.count()
            logger.info(f"✅ Loaded Chroma DB with {doc_count} documents")
            
        except Exception as e:
            logger.error(f"Error loading Chroma DB: {e}")
            raise
    
    def _init_qdrant_collection(self):
        """Clean and initialize Qdrant collection"""
        try:
            # Check if collection exists and delete it
            collections = self.qdrant_client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.collection_name in collection_names:
                logger.info(f"Deleting existing collection '{self.collection_name}'...")
                self.qdrant_client.delete_collection(collection_name=self.collection_name)
                logger.info(f"✅ Deleted collection '{self.collection_name}'")
                time.sleep(1)  # Wait for deletion to complete
            
            # Create new collection
            logger.info(f"Creating collection '{self.collection_name}'...")
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dim,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"✅ Created collection '{self.collection_name}'")
            
        except Exception as e:
            logger.error(f"Error initializing Qdrant collection: {e}")
            raise
    
    def migrate_documents(self, batch_size: int = 100):
        """Migrate all documents from Chroma to Qdrant"""
        try:
            logger.info("Starting migration from Chroma to Qdrant...")
            
            # Get all documents from Chroma
            # We'll use the get method to retrieve all documents with their embeddings
            chroma_collection = self.chroma_vectorstore._collection
            
            # Get total count
            total_docs = chroma_collection.count()
            logger.info(f"Total documents to migrate: {total_docs}")
            
            if total_docs == 0:
                logger.warning("No documents found in Chroma DB")
                return
            
            # Process documents in batches
            offset = 0
            migrated_count = 0
            
            while offset < total_docs:
                # Get batch of documents with embeddings
                result = chroma_collection.get(
                    limit=batch_size,
                    offset=offset,
                    include=["embeddings", "documents", "metadatas"]
                )
                
                # Create Qdrant points
                points = []
                for i, (doc_id, embedding, document, metadata) in enumerate(zip(
                    result['ids'],
                    result['embeddings'],
                    result['documents'],
                    result['metadatas']
                )):
                    point_id = offset + i
                    
                    # Prepare payload
                    payload = {
                        "content": document,
                        "source": metadata.get("source", ""),
                        "page_number": metadata.get("page_number", 0),
                        "web_url": metadata.get("web_url", ""),
                        "has_watermark": metadata.get("has_watermark", False),
                        "chroma_id": doc_id
                    }
                    
                    point = PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload=payload
                    )
                    points.append(point)
                
                # Upload batch to Qdrant
                if points:
                    self.qdrant_client.upsert(
                        collection_name=self.collection_name,
                        points=points
                    )
                    migrated_count += len(points)
                    logger.info(f"✅ Migrated {migrated_count}/{total_docs} documents")
                
                offset += batch_size
            
            logger.info(f"✅ Migration completed! Total documents migrated: {migrated_count}")
            
            # Verify the migration
            collection_info = self.qdrant_client.get_collection(self.collection_name)
            logger.info(f"✅ Qdrant collection now contains {collection_info.points_count} points")
            
        except Exception as e:
            logger.error(f"Error during migration: {e}")
            raise


def main():
    """Main pipeline execution"""
    logger.info("🚀 Starting Barcelona Archives Pipeline V2 - Chroma to Qdrant Migration")
    
    # Wait for Qdrant to be ready
    logger.info("Waiting for Qdrant to be ready...")
    time.sleep(5)
    
    try:
        migrator = ChromaToQdrantMigrator()
        migrator.migrate_documents(batch_size=100)
        
        logger.info("✅ Pipeline V2 completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Pipeline V2 failed: {e}")
        raise


if __name__ == "__main__":
    main()
