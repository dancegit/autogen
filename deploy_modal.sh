#!/bin/bash

# Check if Modal CLI is installed
if ! command -v modal &> /dev/null
then
    echo "Modal CLI is not installed. Please install it first."
    echo "You can install it using: pip install modal"
    exit 1
fi

# Change to the python directory
cd python

# Run the setup commands
echo "Setting up the environment..."
uv sync --all-extras
source .venv/bin/activate
cd packages/autogen-magentic-one
pip install -e .

# Set the path to the deployment file
DEPLOYMENT_FILE="modal_deployment.py"

# Check if the deployment file exists
if [ ! -f "$DEPLOYMENT_FILE" ]; then
    echo "$DEPLOYMENT_FILE not found."
    exit 1
fi

# Deploy to Modal
echo "Deploying autogen-magentic-one to Modal..."
modal deploy "$DEPLOYMENT_FILE"

echo "Deployment completed successfully!"
