#!/bin/bash

# Create test reports directory if it doesn't exist
mkdir -p test_reports

# Build the Docker test image
docker build -t webpage-design-to-text-test -f Dockerfile.test .

# Base command with volume mount for test reports
DOCKER_CMD="docker run --rm -v $(pwd)/test_reports:/app/test_reports webpage-design-to-text-test"

# Check if any arguments are provided (specific test paths)
if [ $# -eq 0 ]; then
    # No arguments, run all tests with coverage and generate reports
    $DOCKER_CMD pytest -v \
        --cov=src \
        --cov-report=html:/app/test_reports/coverage \
        --cov-report=xml:/app/test_reports/coverage.xml \
        --html=/app/test_reports/test_report.html \
        --junitxml=/app/test_reports/junit.xml
    
    echo "Test reports have been saved to the test_reports directory:"
    echo "- HTML Test Report: test_reports/test_report.html"
    echo "- HTML Coverage Report: test_reports/coverage/index.html"
    echo "- XML Coverage Report: test_reports/coverage.xml"
    echo "- JUnit XML Report: test_reports/junit.xml"
else
    # Run specific tests with the given arguments
    $DOCKER_CMD pytest -v \
        --cov=src \
        --cov-report=html:/app/test_reports/coverage \
        --html=/app/test_reports/test_report.html \
        "$@"
    
    echo "Test reports have been saved to the test_reports directory:"
    echo "- HTML Test Report: test_reports/test_report.html"
    echo "- HTML Coverage Report: test_reports/coverage/index.html"
fi