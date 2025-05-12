#!/bin/bash

source ~/.bashrc 2>/dev/null || source ~/.bash_profile 2>/dev/null || source ~/.zshrc 2>/dev/null || {
    echo "No profile found. Please check your shell configuration."
    exit 1
}

# Check if the virtual environment already exists
if [ -d "tools" ]; then
    echo "Virtual environment already exists. Skipping creation."
else
    # Create a virtual environment if it doesn't exist
    echo "Creating tools dir..."
    mkdir -p tools
fi

# Go into the tools directory
cd tools

# github links
GITHUB_LINKS=(
    "https://github.com/the-ride-never-ends/run_tests_and_save_their_results"
    "https://github.com/the-ride-never-ends/codebase_search"
    "https://github.com/the-ride-never-ends/documentation_generator"
    "https://github.com/the-ride-never-ends/lint_a_python_codebase"
    "https://github.com/the-ride-never-ends/test_generator"
)

# Loop through the links and clone each repository
for link in "${GITHUB_LINKS[@]}"; do
    repo_name=$(basename "$link" .git)
    if [ -d "$repo_name" ]; then
        echo "Repository $repo_name already exists. Skipping clone."
    else
        echo "Cloning $link..."
        git clone "$link"
    fi
done

# Install dependencies for each repository
for repo in "${GITHUB_LINKS[@]}"; do
    repo_name=$(basename "$repo" .git)
    if [ -d "$repo_name" ]; then
        echo "Installing dependencies for $repo_name..."
        cd "$repo_name"
        if [ -f "requirements.txt" ]; then
            pip install -r requirements.txt
        fi
        cd ..
    fi
done