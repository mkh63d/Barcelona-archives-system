# Barcelona Archives System

An intelligent RAG-powered application for querying and exploring Barcelona's historical archives using advanced AI and vector search technology.

## Overview

The Barcelona Archives System is a full-stack application that combines document processing, vector search, and conversational AI to make historical archives accessible and searchable. The system uses Retrieval Augmented Generation (RAG) to provide accurate, source-cited responses to user queries about Barcelona's historical documents.

## Key Features

- **Intelligent Search**: RAG-powered semantic search across historical documents
- **Multi-AI Support**: Compatible with OpenAI, Anthropic Claude, and Google Gemini
- **Source Citations**: Every response includes references to original documents
- **Document Processing**: Automated pipeline for cleaning and ingesting archival materials
- **Vector Search**: Fast similarity search using Qdrant vector database
- **Modern UI**: Clean, responsive interface with dark theme

## Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Frontend  │ ──────> │   Backend    │ ──────> │   Qdrant    │
│   (Vue.js)  │         │  (FastAPI)   │         │  (Vectors)  │
└─────────────┘         └──────────────┘         └─────────────┘
                              │
                              │
                        ┌─────▼─────┐
                        │  AI Model │
                        │ (GPT/Claude│
                        │  /Gemini)  │
                        └───────────┘
```

### Components

1. **Frontend** - Vue.js application with TailwindCSS
2. **Backend** - FastAPI with LangChain RAG integration
3. **Data Processing** - Document ingestion and migration pipeline
4. **Preprocessing** - PDF cleaning and enhancement tools
5. **Vector Database** - Qdrant for semantic search

## Technology Stack

### Frontend
- Vue.js 3
- TailwindCSS
- Vite
- Axios

### Backend
- FastAPI
- LangChain
- Python 3.11+
- CLIP embeddings

### Database & AI
- Qdrant (vector database)
- OpenAI GPT-4
- Anthropic Claude 3
- Google Gemini
- ChromaDB (legacy support)

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- AI API key (OpenAI, Anthropic, or Google)

### Using Docker Compose (Recommended)

1. **Clone the repository**
```bash
git clone <repository-url>
cd Barcelona-archives-system
```

2. **Configure environment variables**
```bash
# Create .env file in root directory
cp .env.example .env

# Add your AI API keys
OPENAI_API_KEY=your_key_here
# or
ANTHROPIC_API_KEY=your_key_here
# or
GOOGLE_API_KEY=your_key_here
```

3. **Start all services**
```bash
docker-compose up --build
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Qdrant Dashboard: http://localhost:6333/dashboard

### Manual Setup

See individual README files in each component directory:
- [Backend Setup](backend/README.md)
- [Frontend Setup](frontend/README.MD)
- [Data Processing](data_processing/README.md)
- [Preprocessing](preprocessing/README.md)

## Project Structure

```
Barcelona-archives-system/
├── backend/              # FastAPI backend with RAG
│   ├── app/
│   │   ├── agent.py     # LangChain RAG orchestration
│   │   ├── rag_retriever.py  # Vector search
│   │   ├── clip_handler.py   # Embeddings
│   │   └── routes/      # API endpoints
│   ├── main.py
│   └── requirements.txt
│
├── frontend/            # Vue.js frontend
│   ├── src/
│   │   ├── views/      # Page components
│   │   ├── components/ # Reusable components
│   │   └── App.vue
│   └── package.json
│
├── data_processing/     # Document ingestion pipeline
│   ├── pipeline_v2.py  # Chroma to Qdrant migration
│   └── main.py         # Original pipeline
│
├── preprocessing/       # PDF cleaning tools
│   └── cleaner.ipynb   # Document enhancement
│
├── docker-compose.yml   # Multi-service orchestration
└── README.md           # This file
```

## Usage

### Querying Documents

1. Open the application in your browser
2. Navigate to the Archives view
3. Type your question about Barcelona's historical archives
4. View the AI-generated response with source citations
5. Click on sources to view full document content

### Processing New Documents

1. Place documents in `data_processing/exampleFile/`
2. Run the data processing pipeline:
```bash
docker-compose up pipeline --build
```

### Cleaning Scanned PDFs

1. Open the preprocessing notebook
2. Configure input/output paths
3. Run all cells to clean and enhance documents

## Configuration

### Model Selection

Configure AI model in the Settings view or via environment variables:

```bash
MODEL_PROVIDER=gemini  # Options: openai, anthropic, gemini
MODEL_NAME=gemini-2.5-flash
MODEL_TEMPERATURE=0.7
```

### Vector Database

Qdrant configuration:
```bash
QDRANT_HOST=localhost
QDRANT_PORT=6333
COLLECTION_NAME=barcelona_archives
```

## API Endpoints

### Chat API
- `POST /api/chat` - Send query and receive RAG response with sources

### Model Management
- `GET /api/model/config` - Get current model configuration
- `POST /api/model/config` - Update model settings
- `GET /api/model/providers` - List available AI providers

### Document Retrieval
- `GET /api/document/{filename}` - Retrieve full document content

### Admin
- `GET /api/admin/rag-status` - Check RAG system status

See full API documentation at http://localhost:8000/docs

## Development

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Development Mode
```bash
# Backend with hot reload
cd backend
uvicorn main:app --reload

# Frontend with hot reload
cd frontend
npm run dev
```

## Credits

### Frontend Development
- [Michał Hołyński](https://github.com/mkh63d)

### Backend Development
- [Michał Hołyński](https://github.com/mkh63d)

### Data Processing Pipeline
- [Michał Hołyński](https://github.com/mkh63d)

### Preprocessing Pipeline
- [Wasay Rizwani](https://github.com/WasayRizwani)
- [Sri Rama Saketh](https://github.com/sri16irgp)
- [Venkata Sai Saketh Goda](https://github.com/gvsaisaketh)
- [Subhajit Nandi](https://github.com/subhajitnandi-github)
- [Bhoomika Nandihalli](https://github.com/23bhoomi)
- [Andrzej Martinez](https://github.com/andrzejmartinez)

### Prompt Engineering
- [Cezary Kruczek](https://github.com/czarekkru)
- [Subhajit Nandi](https://github.com/subhajitnandi-github)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues, questions, or contributions, please refer to the individual component READMEs or open an issue in the project repository.

## Acknowledgments

This project is part of the AI Barcelona initiative to digitize and make accessible Barcelona's historical archives.
