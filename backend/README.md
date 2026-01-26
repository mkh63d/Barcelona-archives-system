# Barcelona Archives System - Backend

FastAPI backend application with environment variable support.

## Setup

1. Create virtual environment:
```bash
python -m venv venv
```

2. Activate virtual environment:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
```

5. Run the development server:
```bash
python main.py
```

Or use uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000

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

## Development

The current implementation uses mock data. To integrate with a real database:
1. Install database driver (e.g., `psycopg2` for PostgreSQL)
2. Add database URL to `.env`
3. Replace mock data in routes with actual database queries
4. Add database service to docker-compose.yml
