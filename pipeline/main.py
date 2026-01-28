"""
Pipeline Service - Document Processing and Vector Database Ingestion
Encodes documents and stores them in Qdrant vector database
"""

import os
import time
import logging
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import numpy as np

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Process documents and store embeddings in Qdrant"""
    
    def __init__(self):
        self.qdrant_host = os.getenv("QDRANT_HOST", "localhost")
        self.qdrant_port = int(os.getenv("QDRANT_PORT", 6333))
        self.collection_name = "barcelona_archives"
        
        logger.info(f"Connecting to Qdrant at {self.qdrant_host}:{self.qdrant_port}")
        self.client = QdrantClient(host=self.qdrant_host, port=self.qdrant_port)
        
        # Initialize embedding model
        logger.info("Loading embedding model...")
        self.model = SentenceTransformer("sentence-transformers/clip-ViT-B-32-multilingual-v1")
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        logger.info(f"✅ Model loaded. Embedding dimension: {self.embedding_dim}")
        
        self._init_collection()
    
    def _init_collection(self):
        """Initialize or recreate Qdrant collection"""
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.collection_name in collection_names:
                logger.info(f"Collection '{self.collection_name}' already exists")
            else:
                # Create collection
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dim,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"✅ Created collection '{self.collection_name}'")
        except Exception as e:
            logger.error(f"Error initializing collection: {e}")
            raise
    
    def process_text_file(self, file_path: Path) -> Dict:
        """Process a text file and extract content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "filename": file_path.name,
                "content": content,
                "file_type": "text"
            }
        except Exception as e:
            logger.error(f"Error processing text file {file_path}: {e}")
            return None
    
    def encode_and_store(self, documents: List[Dict]):
        """Encode documents and store in Qdrant"""
        if not documents:
            logger.warning("No documents to process")
            return
        
        logger.info(f"Processing {len(documents)} documents...")
        
        points = []
        for idx, doc in enumerate(documents):
            try:
                # Generate embedding
                embedding = self.model.encode(doc["content"], convert_to_numpy=True)
                
                # Create point for Qdrant
                point = PointStruct(
                    id=idx,
                    vector=embedding.tolist(),
                    payload={
                        "filename": doc["filename"],
                        "content": doc["content"][:1000],  # Store first 1000 chars
                        "file_type": doc["file_type"],
                        "full_content": doc["content"]  # Store full content
                    }
                )
                points.append(point)
                logger.info(f"✅ Processed: {doc['filename']}")
                
            except Exception as e:
                logger.error(f"Error encoding document {doc['filename']}: {e}")
        
        # Upload to Qdrant
        if points:
            try:
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=points
                )
                logger.info(f"✅ Uploaded {len(points)} documents to Qdrant")
            except Exception as e:
                logger.error(f"Error uploading to Qdrant: {e}")
    
    def scan_and_process_directory(self, data_dir: Path):
        """Scan data directory and process all files"""
        if not data_dir.exists():
            logger.warning(f"Data directory {data_dir} does not exist. Creating...")
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # Initial migration
            self._init_migration(data_dir)
        
        # Process all text files
        documents = []
        for file_path in data_dir.glob("*.txt"):
            doc = self.process_text_file(file_path)
            if doc:
                documents.append(doc)
        
        if documents:
            self.encode_and_store(documents)
        else:
            logger.info("No documents found to process")

    def _init_migration(self, data_dir: Path):
        

def main():
    """Main pipeline execution"""
    logger.info("🚀 Starting Barcelona Archives Pipeline Service")
    
    # Wait for Qdrant to be ready
    logger.info("Waiting for Qdrant to be ready...")
    time.sleep(5)
    
    try:
        processor = DocumentProcessor()
        
        # Process documents from data directory
        data_dir = Path("/app/data")
        processor.scan_and_process_directory(data_dir)
        
        logger.info("✅ Pipeline completed successfully")
        
        # Keep container running
        logger.info("Pipeline service is running. Monitoring for new files...")
        while True:
            time.sleep(60)  # Check every minute
            
    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}")
        raise


if __name__ == "__main__":
    main()
