#!/bin/bash

# Check if Modal CLI is installed
if ! command -v modal &> /dev/null
then
    echo "Modal CLI is not installed. Please install it first."
    echo "You can install it using: pip install modal"
    exit 1
fi

# Check if the deployment file exists
if [ ! -f "python/modal_deployment.py" ]; then
    echo "python/modal_deployment.py not found."
    exit 1
fi

# Deploy to Modal
echo "Deploying autogen-magentic-one to Modal..."
python python/modal_deployment.py

echo "Deployment completed successfully!"
