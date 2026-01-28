# Barcelona Archives System - Backend

FastAPI backend with **RAG (Retrieval Augmented Generation)** system powered by LangChain, Qdrant vector database, and multi-provider AI models.

## 🎯 Overview

The backend provides an intelligent API for querying Barcelona's historical archives using:
- **RAG Architecture** - Context-aware responses from actual documents
- **Vector Search** - Qdrant database with CLIP embeddings
- **Multi-AI Support** - OpenAI, Anthropic, Google Gemini
- **LangChain Integration** - Structured prompt engineering

## 🏗️ Architecture

```
API Request → FastAPI
    ↓
RAG Retriever
    ├─→ Encode query (CLIP)
    ├─→ Search Qdrant (vector similarity)
    └─→ Retrieve top 3 documents
    ↓
LangChain Agent
    ├─→ Build context from documents
    └─→ Generate response with LLM
    ↓
Response + Source Citations
```

## 📁 Key Components

- **`app/agent.py`** - RAG orchestration and LLM integration
- **`app/rag_retriever.py`** - Qdrant vector search and retrieval
- **`app/clip_handler.py`** - Text embedding generation (CLIP)
- **`app/routes/chat.py`** - Chat API with source citations
- **`app/routes/admin.py`** - RAG status monitoring
- **`main.py`** - FastAPI application entry point

## 🚀 Setup

### Prerequisites

- Python 3.11+
- Qdrant running (via Docker or standalone)
- At least one AI API key (OpenAI, Anthropic, or Google)

### Option 1: Poetry (Recommended for Development)

1. **Install Poetry:**
```bash
# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# Linux/Mac
curl -sSL https://install.python-poetry.org | python3 -
```

2. **Install dependencies:**
```bash
poetry install
```

3. **Configure environment:**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

4. **Start Qdrant (if not using Docker Compose):**
```bash
docker run -p 6333:6333 -v qdrant_data:/qdrant/storage qdrant/qdrant
```

5. **Run development server:**
```bash
poetry run python main.py
# Or with hot reload:
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Option 2: pip (Alternative)

1. **Create virtual environment:**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

4. **Start Qdrant:**
```bash
docker run -p 6333:6333 -v qdrant_data:/qdrant/storage qdrant/qdrant
```

5. 🔧 Environment Variables

### Required Configuration (.env)

```bash
# AI Model Provider (choose one or configure all)
MODEL_PROVIDER=gemini              # Options: gemini, openai, anthropic
MODEL_NAME=gemini-2.5-flash        # Model variant
MODEL_TEMPERATURE=0.7              # Response creativity (0-1)

# API Keys (add at least one)
GOOGLE_API_KEY=your-google-api-key
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# V📡 API Endpoints

### Chat & RAG

**POST `/api/chat`** - Process user query with RAG
```json
Request:
{
  "message": "What architectural plans are available?",
  "conversation_id": "optional-uuid"
}

Response:
{
  "response": "Based on the archives...",
  "🐳 Docker

### Build and run with Docker:

```bash
docker build -t barcelona-backend .
docker run -p 8000:8000 --env-file .env barcelona-backend
```

### Or use Docker Compose from root directory:

```bash
cd ..
docker compose up backend
```

This automatically:
- Connects to Qdrant service
- Loads environment variables
- Starts on port 8000

## 🛠️ Technology Stack

**Framework & API:**
- FastAPI 0.115.12
- Uvicorn (ASGI server)
- Pydantic (data validation)

**AI & Machine Learning:**
- LangChain 0.3.17 (RAG orchestration)
- LangChain integrations (OpenAI, Anthropic, Gemini)
- SentenceTransformers 3.3.1 (CLIP embeddings)
- PyTorch (ML backend)

**Vector Database:**
- Qdrant Client 1.12.1
- Collection: `barcelona_archives`
- Distance: Cosine similarity
- Vector dimension: 512

**Development:**
- Poetry (dependency management)
- Python 3.11+
- python-dotenv (environment config)

## 🔍 How RAG Works

1. **User Query** → User asks: "What trade union records exist?"
2. **Encode Query** → CLIP model converts to 512-dim vector
3. **Vector Search** → Qdrant finds top 3 similar documents
4. **Context Building** → Retrieved documents formatted as context
5. **LLM Generation** → AI generates response using context
6. **Return with Sources** → Response + citations with relevance scores

## 📊 Monitoring

**Check RAG status:**
```bash
curl http://localhost:8000/api/admin/rag-status
```

**View API metrics:**
```bash
curl http://localhost:8000/health
```

**Access Qdrant dashboard:**
```
http://localhost:6333/dashboard
```

## 🧪 Development

**Run tests:**
```bash
poetry run pytest
```

**Code formatting:**
```bash
poetry run black .
```

**Linting:**
```bash
poetry run ruff check .
```

## 🚧 Notes

- Backend requires Qdrant to be running for RAG functionality
- Documents are processed by the pipeline service
- API keys can be updated via `/api/model/config` endpoint
- CORS is configured for frontend origins in `.env`
- All document data persists in Qdrant vector database

## 📚 Related Services

- **Pipeline Service** - Encodes documents into Qdrant (`../pipeline/`)
- **Frontend** - Vue.js chat interface (`../frontend/`)
- **Qdrant** - Vector database (Docker service)

See main README.md for complete system architecture.
**GET `/api/model/config`** - Get current AI model settings
```json
{
  "provider": "gemini",
  "model_name": "gemini-2.5-flash",
  "temperature": 0.7,
  "api_key_set": true
}
```

**POST `/api/model/config`** - Update AI model settings
```json
{
  "provider": "openai",
  "model_name": "gpt-4o-mini",
  "temperature": 0.8,
  "openai_api_key": "sk-..."
}
```

**GET `/api/model/providers`** - List available providers and models

### Admin & Monitoring

**GET `/api/admin/rag-status`** - Check RAG system health
```json
{
  "qdrant_connected": true,
  "collection_exists": true,
  "vectors_count": 5,
  "points_count": 5,
  "status": "ready"
}
```

**GET `/health`** - Health check endpoint

**GET `/docs`** - Interactive Swagger UI documentation

**GET `/redoc`** - ReDoc API documentation
**Google Gemini:**
- `gemini-2.5-flash` (recommended)
- `gemini-1.5-pro`
- `gemini-1.0-pro`

**OpenAI:**
- `gpt-4o`
- `gpt-4o-mini` (cost-effective)
- `gpt-4-turbo`

**Anthropic:**
- `claude-3-5-sonnet-20241022` (recommended)
- `claude-3-5-haiku-20241022`
- `claude-3-opus-20240229`
## Environment Variables

- `APP_NAME`: Application name
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `DEBUG`: Enable debug mode (default: True)
- `ALLOWED_ORIGINS`: CORS allowed origins (comma-separated)

## API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints

- `GET /api/archives` - Get all archives (with optional search and filter)
- `GET /api/archives/{id}` - Get specific archive
- `POST /api/archives` - Create new archive
- `PUT /api/archives/{id}` - Update archive
- `DELETE /api/archives/{id}` - Delete archive
- `GET /api/categories` - Get all categories

## Docker

### Build and run with Docker:

```bash
docker build -t barcelona-backend .
docker run -p 8000:8000 barcelona-backend
```

### Or use Docker Compose from root directory:

```bash
cd ..
docker-compose up backend
```