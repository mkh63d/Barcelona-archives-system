# Pipeline Service

Document processing and vector database ingestion service for Barcelona Archives System.

## Versions

### Pipeline V1 (`main.py`)
Original pipeline that processes documents from scratch and stores them in Qdrant.

### Pipeline V2 (`pipeline_v2.py`) - **Current**
Migrates pre-processed documents from Chroma DB to Qdrant, preserving existing embeddings and metadata.

## Purpose

The pipeline service migrates documents from Chroma vector database to Qdrant:
1. Loads the Chroma database from `/db/data_chroma` directory
2. Extracts documents with their pre-computed embeddings
3. Migrates all documents to Qdrant vector database with full metadata
4. Maintains document metadata including source, page numbers, web URLs, and watermark information

## Features

- **Batch Processing**: Migrates documents in configurable batches (default: 100 documents per batch)
- **Pre-computed Embeddings**: Uses existing embeddings from Chroma (no re-encoding needed)
- **Metadata Preservation**: Maintains all document metadata from the source database
- **Clean Migration**: Automatically deletes and recreates the Qdrant collection for a fresh start

## How It Works

1. **Database Loading**: Connects to Chroma DB and loads the persisted vector store
2. **Collection Reset**: Deletes existing Qdrant collection and creates a new one
3. **Batch Migration**: Extracts documents with embeddings and metadata from Chroma in batches
4. **Upload**: Uploads each batch to Qdrant with complete document content and metadata

## Environment Variables

- `QDRANT_HOST`: Qdrant server hostname (default: localhost)
- `QDRANT_PORT`: Qdrant server port (default: 6333)
- `CHROMA_PERSIST_DIR`: Chroma database directory (default: ../db/data_chroma)
- `CHROMA_COLLECTION_NAME`: Chroma collection name (default: data_collection)
- `CHROMA_EMBEDDING_MODEL`: Embedding model name (default: paraphrase-multilingual-MiniLM-L12-v2)

## Usage

### With Docker Compose (Recommended)

```bash
# Build and run the pipeline
docker compose up pipeline --build
```

The pipeline will automatically:
1. Extract the Chroma database from `db/db_data_chroma.zip` if needed
2. Clean the existing Qdrant collection
3. Migrate all documents from Chroma to Qdrant
4. Exit after successful migration

### Manual Run

```bash
cd pipeline
pip install -r requirements.txt

# Ensure the Chroma database exists at ../db/data_chroma
python pipeline_v2.py
```

## Database Setup

The Chroma database should be located at `db/data_chroma`. If you have a zip file:

```bash
cd db
unzip db_data_chroma.zip
```

## Document Structure

Migrated documents include the following metadata:
- `content`: Full document text
- `source`: Original filename
- `page_number`: Page number within the document
- `web_url`: URL to the original document page
- `has_watermark`: Boolean indicating watermark presence
- `chroma_id`: Original Chroma document ID

## Sample Data

The service migrates archive documents from Radio de Barcelona (1945), which were pre-processed and stored in Chroma DB.


