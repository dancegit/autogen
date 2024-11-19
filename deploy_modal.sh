#!/bin/bash

# Check if Modal CLI is installed
if ! command -v modal &> /dev/null
then
    echo "Modal CLI is not installed. Please install it first."
    echo "You can install it using: pip install modal"
    exit 1
fi

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Check if the deployment file exists
if [ ! -f "$SCRIPT_DIR/python/modal_deployment.py" ]; then
    echo "python/modal_deployment.py not found."
    exit 1
fi

# Change to the root autogen directory
cd "$SCRIPT_DIR"

# Find the correct pyproject.toml file
PYPROJECT_PATH=$(find . -name pyproject.toml | grep "packages/autogen-magentic-one/pyproject.toml")

if [ -z "$PYPROJECT_PATH" ]; then
    echo "Could not find pyproject.toml for autogen-magentic-one"
    exit 1
fi

# Change to the directory containing pyproject.toml
PACKAGE_DIR=$(dirname "$PYPROJECT_PATH")
echo "Changing to directory: $PACKAGE_DIR"
cd "$PACKAGE_DIR" || { echo "Failed to change directory to $PACKAGE_DIR"; exit 1; }

# Verify we're in the correct directory
if [ ! -f "pyproject.toml" ]; then
    echo "pyproject.toml not found in current directory. Current directory: $(pwd)"
    exit 1
fi

# Change to the autogen-magentic-one package directory
MAGENTIC_ONE_DIR="$SCRIPT_DIR/python/packages/autogen-magentic-one"
echo "Changing to: $MAGENTIC_ONE_DIR"
cd "$MAGENTIC_ONE_DIR" || { echo "Failed to change directory to $MAGENTIC_ONE_DIR"; exit 1; }

# Verify we're in the correct directory
if [ ! -f "pyproject.toml" ]; then
    echo "pyproject.toml not found in current directory. Current directory: $(pwd)"
    exit 1
fi

# Print current directory and list files
echo "Current directory: $(pwd)"
echo "Files in current directory:"
ls -la

# Install dependencies
echo "Installing dependencies..."
uv pip install -e .

# Deploy to Modal
echo "Deploying autogen-magentic-one to Modal..."
modal deploy "$SCRIPT_DIR/python/modal_deployment.py"

# Check if the deployment was successful
if [ $? -eq 0 ]; then
    echo "Deployment completed successfully!"
else
    echo "Deployment failed. Please check the error messages above."
    exit 1
fi
