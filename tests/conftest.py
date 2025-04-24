import pytest
import datetime
import os.path

# Add metadata to reports
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "unit: marks as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: marks as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: marks as a slow test"
    )
    
    # Add metadata to the report
    config._metadata['Project Name'] = 'WebpageDesign-to-Text'
    config._metadata['Test Date'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    config._metadata['Test Type'] = 'Automated Unit Tests'

# HTML report customization
def pytest_html_report_title(report):
    report.title = "WebpageDesign-to-Text Test Report"

# Format of environment info in HTML reports
def pytest_html_environment(config):
    return {
        'Python': pytest.__version__,
        'Platform': pytest.config.getoption('--platform', default='Unknown'),
        'Packages': {
            'pyppeteer': 'installed',
            'google-cloud-vision': 'installed',
            'anthropic': 'installed',
        }
    }

# Function to add extra text to report summary header
def pytest_html_results_summary(prefix, summary, postfix):
    prefix.extend([
        f"<p>WebpageDesign-to-Text Test Suite<br>",
        f"Run on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>",
    ])
    
    # Add coverage information if it exists
    coverage_path = os.path.join('test_reports', 'coverage', 'index.html')
    if os.path.exists(coverage_path):
        coverage_link = f"<a href='{coverage_path}'>View Coverage Report</a>"
        prefix.append(f"<p>{coverage_link}</p>")