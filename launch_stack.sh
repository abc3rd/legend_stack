#!/bin/bash
echo "🔁 Activating virtual environment..."
source venv/bin/activate || python3 -m venv venv && source venv/bin/activate

echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "🔐 Loading environment variables..."
export $(grep -v '^#' .env | xargs)

echo "🚀 Launching FastAPI app on Uvicorn..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
