#!/bin/bash

# Set the working directory to the root of the project
cd "$(dirname "$0")"

# Build the Docker image
docker build -t autogen_magentic_one -f Dockerfile .

# Check if the build was successful
if [ $? -eq 0 ]; then
    echo "Docker build completed successfully."
else
    echo "Docker build failed."
    exit 1
fi

echo "You can now run the container using:"
echo "docker run -it autogen_magentic_one"
