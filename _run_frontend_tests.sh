#!/bin/bash

# Frontend tests runner script for American Law Search
# This script runs all JavaScript tests in the app/tests/frontend directory

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== American Law Search Frontend Tests ===${NC}"

# Change to the project root directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Check if Jest is installed globally
if ! command -v jest &> /dev/null; then
    echo -e "${YELLOW}Jest is not installed globally. Trying npx...${NC}"
    
    # Try to run with npx
    if ! command -v npx &> /dev/null; then
        echo -e "${RED}Error: Neither Jest nor npx found. Please install Jest:${NC}"
        echo "npm install -g jest"
        echo "or"
        echo "npm install --save-dev jest"
        exit 1
    fi
    
    JEST_CMD="npx jest"
else
    JEST_CMD="jest"
fi

# Set up Jest environment - you may need to adjust these options based on your project setup
JEST_OPTIONS="--testEnvironment=jsdom"

# Check if frontend test directory exists
if [ ! -d "app/tests/frontend" ]; then
    echo -e "${RED}Error: Frontend test directory not found!${NC}"
    exit 1
fi

echo -e "${BLUE}Running JavaScript tests...${NC}"

# Count test files
TEST_FILES=$(find app/tests/frontend -name "*.test.js" | wc -l)
echo -e "${YELLOW}Found ${TEST_FILES} test files${NC}"

# Run all tests in the frontend test directory
$JEST_CMD $JEST_OPTIONS app/tests/frontend

# Capture the exit code
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}All frontend tests passed!${NC}"
else
    echo -e "${RED}Some frontend tests failed!${NC}"
fi

exit $EXIT_CODE
