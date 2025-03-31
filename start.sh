#!/bin/bash
# Script to run the American Law application

# Activate the virtual environment
source venv/bin/activate

# Set environment variables
export PYTHONPATH=$PYTHONPATH:$(pwd)/..

# Check if port is provided
PORT=${1:-8000}

# Print banner
echo "=================================================="
echo "  American Law Chatbot"
echo "  Starting on port $PORT"
echo "=================================================="

# Start the FastAPI application with Uvicorn
python -m uvicorn chatbot.main:app --host 0.0.0.0 --port $PORT --reload 