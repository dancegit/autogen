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
# Setup venv
source ./venv/bin/activate
# Print current directory and list files
echo "Current directory: $(pwd)"
echo "Files in current directory:"
ls -la

# Upgrade pip and install dependencies
echo "Upgrading pip and installing dependencies..."
pip install --upgrade pip
for package in autogen-core autogen-ext autogen-magentic-one autogen-agentchat agbench autogen-studio; do
    if [ -f "./python/packages/$package/pyproject.toml" ]; then
        pip install -e "./python/packages/$package"
    elif [ -f "./python/packages/$package/requirements.txt" ]; then
        pip install -r "./python/packages/$package/requirements.txt"
        pip install -e "./python/packages/$package"
    else
        echo "Warning: No pyproject.toml or requirements.txt found for $package"
    fi
done
pip install PyGithub tenacity

# Generate WebSocket API documentation
echo "Generating WebSocket API documentation..."
if "$SCRIPT_DIR/venv/bin/python" -c "from autogen_magentic_one.web_interface import generate_ws_api_docs; generate_ws_api_docs()"; then
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
DEPLOY_OUTPUT=$(modal deploy "$SCRIPT_DIR/python/modal_deployment.py")

# Check if the deployment was successful
if [ $? -eq 0 ]; then
    echo "Deployment completed successfully!"
    # Extract the URL from the deployment output
    DEPLOY_URL=$(echo "$DEPLOY_OUTPUT" | grep -oP 'https://.*\.modal\.run')
    if [ -n "$DEPLOY_URL" ]; then
        WS_URL=$(echo "$DEPLOY_URL" | sed 's|^https://|wss://|')
        echo "WebSocket URL: ${WS_URL}/ws"
    else
        echo "Warning: Couldn't extract the deployment URL. Please check the Modal dashboard for the correct URL."
    fi
else
    echo "Deployment failed. Please check the error messages above."
    exit 1
fi
