# Barcelona Archives System - Frontend

Vue.js + TailwindCSS frontend application with monochromatic dark theme and #009639 primary color.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure environment variables:
```bash
cp .env.example .env
```

3. Start development server:
```bash
npm run dev
```

The application will be available at http://localhost:3000

## Environment Variables

- `VITE_API_URL`: Backend API URL (default: http://localhost:8000)
- `VITE_APP_NAME`: Application name

## Build

```bash
npm run build
```

## Preview Production Build

```bash
npm run preview
```

## Docker

### Build and run with Docker:

```bash
docker build -t barcelona-frontend .
docker run -p 80:80 barcelona-frontend
```

### Or use Docker Compose from root directory:

```bash
cd ..
docker-compose up frontend
```

## Color Palette

- Primary: #009639 (Green)
- Background: Monochromatic dark shades (#1a1a1a to #000000)
