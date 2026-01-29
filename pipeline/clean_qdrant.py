"""
Script to clean Qdrant database by deleting the collection
"""

import os
from qdrant_client import QdrantClient
from dotenv import load_dotenv

load_dotenv()

def main():
    qdrant_host = os.getenv("QDRANT_HOST", "localhost")
    qdrant_port = int(os.getenv("QDRANT_PORT", 6333))
    collection_name = "barcelona_archives"
    
    print(f"Connecting to Qdrant at {qdrant_host}:{qdrant_port}")
    client = QdrantClient(host=qdrant_host, port=qdrant_port)
    
    try:
        # Check if collection exists
        collections = client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if collection_name in collection_names:
            print(f"Deleting collection '{collection_name}'...")
            client.delete_collection(collection_name=collection_name)
            print(f"✅ Collection '{collection_name}' deleted successfully")
        else:
            print(f"Collection '{collection_name}' does not exist")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
