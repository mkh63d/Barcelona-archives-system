# Barcelona Archives System

Full-stack application for managing Barcelona historical archives with Vue.js frontend and Python FastAPI backend.

## Project Structure

```
Barcelona-archives-system/
├── frontend/          # Vue.js + TailwindCSS frontend
│   ├── src/
│   │   ├── views/    # Page components
│   │   ├── App.vue   # Main app component
│   │   └── main.js   # Entry point
│   ├── .env          # Frontend environment variables
│   └── package.json
│
└── backend/           # Python FastAPI backend
    ├── app/
    │   ├── routes/   # API routes
    │   └── models.py # Data models
    ├── .env          # Backend environment variables
    ├── main.py       # FastAPI application
    └── requirements.txt
```

## Design

- **Color Palette**: Monochromatic dark theme with #009639 primary green
- **Frontend**: Vue.js 3 with Vite, TailwindCSS, Vue Router
- **Backend**: FastAPI with environment-based configuration

## Quick Start

### Option 1: Docker (Recommended)

The easiest way to run the entire application:

```bash
docker-compose up --build
```

- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

To stop:
```bash
docker-compose down
```

### Option 2: Manual Setup

#### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python main.py
```

Backend runs at: http://localhost:8000

#### Frontend Setup

```bash
cd frontend
npm install
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
