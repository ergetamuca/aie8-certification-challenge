#!/bin/bash

echo "🔨 Building React frontend..."

# Build React app
cd frontend
npm run build

echo "✅ Frontend built successfully!"

# Start production server
cd ../backend
source venv/bin/activate
python simple_server.py