#!/bin/bash

# Exit on error
set -e

# Define paths
VENV_PATH="venv"
TESTS_DIR="app/tests"
LOG_FILE="test_results.log"

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo "Error: Virtual environment not found at $VENV_PATH"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_PATH/bin/activate"

# Check if tests directory exists
if [ ! -d "$TESTS_DIR" ]; then
    echo "Error: Tests directory not found at $TESTS_DIR"
    exit 1
fi

# Run the tests and save output to file while also displaying on console
echo "Running tests..."
echo "Test run started at $(date)" | tee "$LOG_FILE"
python -m unittest discover -s "$TESTS_DIR" 2>&1 | tee -a "$LOG_FILE"
TEST_EXIT_CODE=${PIPESTATUS[0]}  # Capture the exit code of the python command

# Deactivate virtual environment
deactivate

echo "Test run complete." | tee -a "$LOG_FILE"
echo "Results saved to $LOG_FILE"

# Exit with the same code as the test command
exit $TEST_EXIT_CODE
