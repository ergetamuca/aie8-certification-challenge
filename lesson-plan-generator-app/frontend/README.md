# Lesson Plan Generator

AI-powered lesson plan generator for educators.

## Quick Start

### Development Mode
```bash
# Start both frontend and backend
cd lesson-plan-generator-app/backend/scripts
chmod +x start_dev.sh
./start_dev.sh
```

### Production Mode
```bash
# Build and run production server
cd lesson-plan-generator-app/backend/scripts
chmod +x build_and_run.sh
./build_and_run.sh
```

## Access the App
- **Frontend**: http://localhost:5173 (dev) or http://localhost:8001 (production)
- **Backend API**: http://localhost:8001

## Requirements
- Node.js 18+
- Python 3.11+
- OpenAI API key (set in backend/.env)

## Manual Setup
1. **Backend**: `cd backend && source venv/bin/activate && python simple_server.py`
2. **Frontend**: `cd frontend && npm install && npm run dev`
