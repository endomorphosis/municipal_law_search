#!/bin/bash
# Script to run the American Law application from a Docker container

# Check if port is provided
PORT=${1:-8000}

# Print banner
echo "=================================================="
echo "  American Law Search"
echo "  Starting on port $PORT"
echo "=================================================="

# Start the FastAPI application with Uvicorn
python -m uvicorn app:app --host 0.0.0.0 --port $PORT --reload 