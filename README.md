# Barcelona Archives System

AI-powered historical archives assistant using **RAG (Retrieval Augmented Generation)** with Vue.js frontend, Python FastAPI backend, and Qdrant vector database.

## 🎯 Overview

This system provides an intelligent chat interface to explore Barcelona's historical archives. It uses advanced AI techniques to retrieve relevant historical documents and generate contextually accurate responses.

## 🏗️ Architecture

```
User Query → Frontend (Vue.js)
    ↓
Backend (FastAPI)
    ↓
[RAG Pipeline]
    ├─→ CLIP Text Encoder
    ├─→ Qdrant Vector Search
    ├─→ Context Retrieval
    └─→ LLM (OpenAI/Anthropic/Gemini)
    ↓
Response + Source Citations
```

## 📁 Project Structure

```
Barcelona-archives-system/
├── frontend/              # Vue.js + TailwindCSS frontend
│   ├── src/
│   │   ├── views/
│   │   │   ├── Home.vue      # Chat interface with NotebookLM-style citations
│   │   │   └── Settings.vue  # AI model configuration
│   │   ├── App.vue           # Main app layout with sidebar
│   │   └── main.js           # Entry point
│   └── package.json
│
├── backend/               # Python FastAPI backend with RAG
│   ├── app/
│   │   ├── routes/
│   │   │   ├── chat.py       # Chat endpoint with RAG
│   │   │   └── admin.py      # RAG status monitoring
│   │   ├── agent.py          # RAG orchestration with LangChain
│   │   ├── rag_retriever.py  # Qdrant retriever
│   │   ├── clip_handler.py   # Text embedding model
│   │   └── vector_store.py   # Vector database interface
│   ├── main.py               # FastAPI application
│   └── requirements.txt
│
├── pipeline/              # Document processing service
│   ├── main.py            # Document encoding & Qdrant ingestion
│   ├── requirements.txt
│   └── data/              # Document files directory
│
├── docker-compose.yml     # Multi-service orchestration
└── .env                   # Environment configuration
```

## 🚀 Key Features

### AI & RAG
- ✅ **Retrieval Augmented Generation (RAG)** - Context-aware responses based on actual documents
- ✅ **Vector Search** - Semantic search using CLIP multilingual embeddings
- ✅ **Multiple AI Providers** - OpenAI, Anthropic Claude, Google Gemini support
- ✅ **Source Citations** - NotebookLM-style source references with relevance scores
- ✅ **LangChain Integration** - Structured prompt engineering and context management

### Frontend
- ✅ **Modern Chat UI** - Claude/ChatGPT-inspired interface
- ✅ **Source Cards** - Expandable document citations with previews
- ✅ **Relevance Indicators** - Visual progress bars showing match quality
- ✅ **Dark Theme** - Monochromatic design with #009639 primary green
- ✅ **Responsive Design** - Mobile-friendly layout

### Backend
- ✅ **FastAPI** - High-performance async API
- ✅ **Qdrant Vector DB** - Efficient similarity search
- ✅ **Document Pipeline** - Automated encoding and ingestion
- ✅ **Admin Endpoints** - RAG system monitoring
- ✅ **CORS Configured** - Secure cross-origin requests

### DevOps
- ✅ **Docker Compose** - Single-command deployment
- ✅ **Environment Variables** - Centralized configuration
- ✅ **Persistent Storage** - Qdrant data volumes
- ✅ **Hot Reload** - Development mode support

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose (recommended)
- OR: Node.js 20+, Python 3.11+, and Qdrant running locally

### Option 1: Docker (Recommended)

**1. Configure environment variables:**
```bash
# Edit .env file and add your AI API key
GOOGLE_API_KEY=your-key-here
# or
OPENAI_API_KEY=your-key-here
# or
ANTHROPIC_API_KEY=your-key-here
```

**2. Start all services:** (Development)

**1. Start Qdrant:**
```bash
docker run -p 6333:6333 -v qdrant_data:/qdrant/storage qdrant/qdrant
```

**2. Start Pipeline Service:**
```bash
cd pipeline
pip install -r requirements.txt
python main.py
```
This creates sample documents and encodes them into Qdrant.

**3. Start Backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows: venv\Scripts\activate | Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
python main.py
```
Backend runs at: http://localhost:8000
🔧 Configuration

### Environment Variables (.env)

```bash
# AI Model Configuration
MODEL_PROVIDER=gemini              # Options: gemini, openai, anthropic
MODEL_NAME=gemini-2.5-flash        # Model variant
MODEL_TEMPERATURE=0.7              # Response creativity (0-1)

# API Keys (add at least one)
GOOGLE_API_KEY=your-key-here
OPENAI_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here

# Vector Database
QDRANT_HOST=qdrant                 # Docker: qdrant | Local: localhost
QDRANT_PORT=6333

# Application
APP_NAME=Barcelona Archives System
DEBUG=True
ALLOWED_ORIGINS=http://localhost,http://localhost:80,http://localhost:3000,http://localhost:3001
```

### Adding Documents

Place document files in `pipeline/data/` directory:
```bash
pipeline/data/
├── historical_records.txt
├── architectural_plans.txt
└── your_document.txt
```

The pipeline will automatically process and encode them into Qdrant.

## 📊 Sample Archive Documents

The system includes 5 comprehensive sample documents:

1. **Historical Records 1900-1920** - Municipal records from early 20th century
2. **Architectural Plans** - Gothic Quarter buildings (1850-1900)
3. **Civil Registry** - Birth, marriage, death certificates (1920-1950)
4. **Trade Union Records** - Labor movement documentation (1880-1930)
5. **Photography Collection** - Historical photographs (1920-1960)

## 🔍 How RAG Works

1. **User asks a question** → "What architectural plans are available?"
2. **Query encoding** → CLIP model converts question to vector
3. **Vector search** → Qdrant finds top 3 similar documents
4. **Context building** → Retrieved documents assembled as context
5. **LLM generation** → AI generates response using retrieved context
6. **Response with sources** → Answer + citations with relevance scores

## 📡 API Endpoints

### Chat Endpoints
- `POST /api/chat` - Send message, receive RAG response with sources
- `GET /api/model/config` - Get current AI model configuration
- `POST /api/model/config` - Update AI model settings
- `GET /api/model/providers` - List available AI providers

### Admin Endpoints
- `GET /api/admin/rag-status` - Check Qdrant connection and vector counts
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation

## 🛠️ Technology Stack

**Frontend:**
- Vue.js 3 (Composition API)
- Vite 6
- TailwindCSS 3
- Axios
- Vue Router

**Backend:**
- FastAPI 0.115
- LangChain 0.3
- Qdrant Client 1.12
- SentenceTransformers (CLIP)
- PyTorch
- Uvicorn

**AI/ML:**
- LangChain (RAG orchestration)
- CLIP ViT-B-32 Multilingual (embeddings)
- OpenAI / Anthropic / Google Gemini (LLMs)
- Qdrant (vector database)

**DevOps:**
- Docker & Docker Compose
- Nginx (production frontend)
- Python 3.11
- Node.js 20

## 📈 Monitoring

**Check RAG system status:**
```bash
curl http://localhost:8000/api/admin/rag-status
```

**Access Qdrant dashboard:**
```
http://localhost:6333/dashboard
```

**View collection info:**
- Collection name: `barcelona_archives`
- Vector dimension: 512
- Distance metric: Cosine similarity

## 🎨 Design System

- **Primary Color**: #009639 (Barcelona green)
- **Background**: Monochromatic dark (#000000 to #1a1a1a)
- **Typography**: System fonts for readability
- **Layout**: Sidebar navigation with chat-style interface
- **Citations**: NotebookLM-inspired source cards

## 📝 Development Notes

- Frontend uses Vite proxy for API calls in development
- Backend includes CORS middleware for cross-origin requests
- Pipeline service runs continuously, monitoring for new documents
- Qdrant data persists in Docker volumes
- All services communicate via Docker network

## 🚧 Future Enhancements

- [ ] PDF and DOCX document support in pipeline
- [ ] Multi-language query support
- [ ] Document upload via web interface
- [ ] Authentication and user management
- [ ] Conversation history persistence
- [ ] Advanced filtering and search options
- [ ] Export conversations and citations
- [ ] Analytics dashboard

## 📄 License

MIT License - See individual component licenses for details.
npm run dev
```

Frontend runs at: http://localhost:3000

## Features

- ✅ Vue.js 3 with Composition API
- ✅ TailwindCSS with custom dark theme
- ✅ FastAPI backend with RESTful API
- ✅ Environment variable support (.env files)
- ✅ Docker & Docker Compose support
- ✅ CORS configuration
- ✅ Mock data for development
- ✅ Responsive design
- ✅ API documentation at /docs
- ✅ Production-ready Nginx configuration

## Environment Configuration

Both frontend and backend include `.env` and `.env.example` files for easy configuration. See individual README files in each directory for details.

## API Documentation

Interactive API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Next Steps

1. Install dependencies in both frontend and backend
2. Start both servers
3. Access the application at http://localhost:3000
4. Integrate with a real database (PostgreSQL, MongoDB, etc.)
5. Add authentication and authorization
6. Implement file upload for archive documents
