#!/bin/bash

# Frontend test setup script for American Law Search
# This script installs Jest and other dependencies needed for frontend testing

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== American Law Search Frontend Test Setup ===${NC}"

# Change to the project root directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Create package.json if it doesn't exist
if [ ! -f "package.json" ]; then
    echo -e "${YELLOW}Creating package.json file${NC}"
    cat > package.json << EOL
{
  "name": "american_law_search",
  "version": "1.0.0",
  "description": "American Law Search Frontend",
  "main": "index.js",
  "scripts": {
    "test": "jest --testEnvironment=jsdom"
  },
  "author": "",
  "license": "MIT"
}
EOL
    echo -e "${GREEN}Created package.json${NC}"
fi

# Create jest.config.js if it doesn't exist
if [ ! -f "jest.config.js" ]; then
    echo -e "${YELLOW}Creating jest.config.js file${NC}"
    cat > jest.config.js << EOL
module.exports = {
  testEnvironment: 'jsdom',
  roots: ['<rootDir>/app/tests/frontend'],
  testMatch: ['**/*.test.js'],
  verbose: true,
  collectCoverage: true,
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov'],
  moduleNameMapper: {
    '\\.(css|less|scss|sass)$': '<rootDir>/__mocks__/styleMock.js',
    '\\.(gif|ttf|eot|svg)$': '<rootDir>/__mocks__/fileMock.js'
  },
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js']
};
EOL
    echo -e "${GREEN}Created jest.config.js${NC}"
fi

# Create jest.setup.js if it doesn't exist
if [ ! -f "jest.setup.js" ]; then
    echo -e "${YELLOW}Creating jest.setup.js file${NC}"
    cat > jest.setup.js << EOL
// Mock global console methods to prevent noise in test output
global.console = {
  ...console,
  // Uncomment to suppress console logs during tests
  // log: jest.fn(),
  // info: jest.fn(),
  // warn: jest.fn(),
  // error: jest.fn(),
};

// Add any custom jest matchers or global setup here
EOL
    echo -e "${GREEN}Created jest.setup.js${NC}"
fi

# Create mocks directory and files for handling CSS and other imports
if [ ! -d "__mocks__" ]; then
    echo -e "${YELLOW}Creating __mocks__ directory${NC}"
    mkdir -p __mocks__
    
    echo -e "${YELLOW}Creating style mock${NC}"
    cat > __mocks__/styleMock.js << EOL
module.exports = {};
EOL
    
    echo -e "${YELLOW}Creating file mock${NC}"
    cat > __mocks__/fileMock.js << EOL
module.exports = 'test-file-stub';
EOL
    
    echo -e "${GREEN}Created mock files${NC}"
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}Error: npm not found. Please install Node.js and npm:${NC}"
    echo "https://nodejs.org/en/download/"
    exit 1
fi

# Install Jest and related dependencies
echo -e "${BLUE}Installing Jest and related dependencies...${NC}"
npm install --save-dev jest jest-environment-jsdom @testing-library/jest-dom @testing-library/dom

# Check the installation
if npm list jest --depth=0 &> /dev/null; then
    echo -e "${GREEN}Jest successfully installed!${NC}"
else
    echo -e "${RED}Jest installation failed!${NC}"
    exit 1
fi

echo -e "${GREEN}Frontend test environment setup complete!${NC}"
echo -e "${YELLOW}You can now run frontend tests with:${NC}"
echo -e "${BLUE}./run_frontend_tests.sh${NC}"
echo -e "${YELLOW}Or with npm:${NC}"
echo -e "${BLUE}npm test${NC}"

exit 0
