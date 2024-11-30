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
#setup venv
#source ./venv/bin/activate
# Print current directory and list files
echo "Current directory: $(pwd)"
echo "Files in current directory:"
ls -la

# Install dependencies
#echo "Installing dependencies..."
#uv pip install -e ./python

# Generate WebSocket API documentation
echo "Generating WebSocket API documentation..."
if "$SCRIPT_DIR/venv/bin/python" "$SCRIPT_DIR/python/packages/autogen-magentic-one/src/autogen_magentic_one/generate_ws_api_docs.py"; then
    echo "WebSocket API documentation generated successfully."
    # Copy the generated markdown file to the current directory
    cp "$SCRIPT_DIR/python/packages/autogen-magentic-one/src/autogen_magentic_one/ws_api_docs.md" ./
    echo "WebSocket API documentation copied to the current directory."
else
    echo "Error: Failed to generate WebSocket API documentation."
    exit 1
fi

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
