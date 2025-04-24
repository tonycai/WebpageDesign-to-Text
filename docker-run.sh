#!/bin/bash

# Build the Docker image
docker build -t webpage-design-to-text .

# Check if URL argument is provided
if [ -z "$1" ]; then
  echo "Error: Please provide a URL to analyze"
  echo "Usage: ./docker-run.sh https://example.com [additional flags]"
  exit 1
fi

URL=$1
shift  # Remove the URL from arguments

# Run the container with the provided URL and any additional arguments
docker run --rm -v "$(pwd)/output:/app/output" \
                -v "$(pwd)/screenshot:/app/screenshot" \
                -v "$(pwd)/config.yaml:/app/config.yaml" \
                webpage-design-to-text "$URL" "$@"

echo "Processing complete. Results have been saved to the output directory."