#!/bin/bash

# Check if Modal CLI is installed
if ! command -v modal &> /dev/null
then
    echo "Modal CLI is not installed. Please install it first."
    echo "You can install it using: pip install modal"
    exit 1
fi

# Check if the deployment file exists
if [ ! -f "modal_deployment.py" ]; then
    echo "modal_deployment.py not found in the current directory."
    exit 1
fi

# Deploy to Modal
echo "Deploying autogen-magentic-one to Modal..."
modal deploy modal_deployment.py

echo "Deployment completed successfully!"
