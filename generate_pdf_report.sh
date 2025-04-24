#!/bin/bash

# This script generates a PDF report from the HTML test reports
# It requires wkhtmltopdf to be installed

# Check if wkhtmltopdf is installed
if ! command -v wkhtmltopdf &> /dev/null
then
    echo "Error: wkhtmltopdf is not installed. Please install it first:"
    echo "  - For Ubuntu/Debian: sudo apt-get install wkhtmltopdf"
    echo "  - For macOS: brew install wkhtmltopdf"
    exit 1
fi

# Check if the test report exists
if [ ! -f "test_reports/test_report.html" ]; then
    echo "Error: Test report not found. Please run tests first."
    exit 1
fi

# Generate the PDF report
echo "Generating PDF test report..."
wkhtmltopdf \
    --enable-local-file-access \
    --footer-center "WebpageDesign-to-Text Test Report - [date] [time]" \
    --footer-font-size 9 \
    --margin-bottom 20 \
    test_reports/test_report.html \
    test_reports/test_report.pdf

# Check if the coverage report exists
if [ -f "test_reports/coverage/index.html" ]; then
    echo "Generating PDF coverage report..."
    wkhtmltopdf \
        --enable-local-file-access \
        --footer-center "WebpageDesign-to-Text Coverage Report - [date] [time]" \
        --footer-font-size 9 \
        --margin-bottom 20 \
        test_reports/coverage/index.html \
        test_reports/coverage_report.pdf
fi

echo "PDF reports generated:"
echo "- Test Report: test_reports/test_report.pdf"
if [ -f "test_reports/coverage_report.pdf" ]; then
    echo "- Coverage Report: test_reports/coverage_report.pdf"
fi