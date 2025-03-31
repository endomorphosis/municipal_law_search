#!/bin/bash

echo "Setting up the environment..."

# Check if Python 3.12 is installed
if ! command -v python3.12 &> /dev/null
then
    echo "Python 3.12 is not installed. Please install Python 3.12 and add it to your PATH."
    exit 1
fi

# Check Python version if python3 exists
if command -v python3 &> /dev/null
then
    python_version=$(python3 --version | awk '{print $2}')
    if [[ ! "$python_version" == 3.12* ]]; then
        echo "Python 3.12 is required but found $python_version. Please install Python 3.12."
        exit 1
    fi
fi

# Check if the virtual environment already exists
if [ -d "venv" ]; then
    echo "Virtual environment already exists. Skipping creation."
else
    # Create a virtual environment if it doesn't exist
    echo "Creating a virtual environment..."
    python3 -m venv venv
fi

# Activate the virtual environment
echo "Activating the virtual environment 'venv'..."
source venv/bin/activate


# Install required packages from requirements.txt
if [[ -f "requirements.txt" ]]; then
    echo "Installing required packages..."
    pip install -r requirements.txt
else
    echo "requirements.txt not found. Skipping package installation."
fi

echo "Setup complete!"
