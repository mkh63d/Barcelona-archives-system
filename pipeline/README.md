# Pipeline Service

Document processing and vector database ingestion service for Barcelona Archives System.

## Purpose

The pipeline service:
1. Monitors the `/app/data` directory for document files
2. Encodes documents using multilingual CLIP text embeddings
3. Stores embeddings in Qdrant vector database for RAG (Retrieval Augmented Generation)

## Supported File Types

- Text files (.txt)

## How It Works

1. **Encoding**: Uses SentenceTransformer model to generate semantic embeddings
2. **Storage**: Uploads embeddings to Qdrant with full document content as payload
3. **Monitoring**: Continuously monitors for new files (checks every minute)

## Environment Variables

- `QDRANT_HOST`: Qdrant server hostname (default: localhost)
- `QDRANT_PORT`: Qdrant server port (default: 6333)

## Usage

### With Docker Compose

```bash
docker compose up pipeline
```

### Manual Run

```bash
cd pipeline
pip install -r requirements.txt
python main.py
```

## Adding Documents

Place document files in the `data/` directory. The pipeline will automatically process them on the next scan cycle.

## Sample Documents

The service creates 5 sample archive documents covering scripts of Radio de Barcelona.


