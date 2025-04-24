import pytest
import os
import json
from unittest.mock import patch, MagicMock
from src.components.output_handler import OutputHandler

@pytest.fixture
def sample_results():
    """Sample results for testing."""
    return {
        'url': 'https://example.com',
        'screenshot_path': '/path/to/screenshot.png',
        'textual_description': '# Example Website\n\nThis is a sample description.',
        'structured_description': {
            'page_title': 'Example Website',
            'layout_pattern': 'standard-layout',
            'ui_elements': [
                {'type': 'header', 'position': {'description': 'top center'}}
            ]
        },
        'json_output': '{"page_title": "Example Website"}'
    }

@pytest.fixture
def output_dir(tmp_path):
    """Create a temporary output directory."""
    output_path = tmp_path / "output"
    output_path.mkdir()
    return str(output_path)

def test_output_handler_init():
    # Test default output directory
    handler = OutputHandler()
    assert handler.output_dir.endswith('output')
    
    # Test custom output directory
    custom_dir = '/custom/output'
    handler = OutputHandler(output_dir=custom_dir)
    assert handler.output_dir == custom_dir

def test_url_to_safe_filename():
    handler = OutputHandler()
    
    # Test basic URL conversion
    assert handler._url_to_safe_filename('https://example.com') == 'example.com'
    
    # Test URL with path
    assert handler._url_to_safe_filename('https://example.com/path/to/page') == 'example.com_path_to_page'
    
    # Test URL with query parameters
    safe_name = handler._url_to_safe_filename('https://example.com/search?q=test&page=1')
    assert '?' not in safe_name
    assert '&' not in safe_name
    assert '=' not in safe_name
    
    # Test long URL gets truncated
    long_url = 'https://' + ('a' * 100) + '.com'
    safe_name = handler._url_to_safe_filename(long_url)
    assert len(safe_name) <= 50

def test_save_results(output_dir, sample_results):
    handler = OutputHandler(output_dir=output_dir)
    
    # Test saving results
    saved_files = handler.save_results(
        sample_results, 
        'https://example.com',
        include_timestamp=False  # Disable timestamp for predictable testing
    )
    
    # Verify return value
    assert isinstance(saved_files, dict)
    assert 'textual_description' in saved_files
    assert 'structured_description' in saved_files
    
    # Verify files exist
    assert os.path.exists(saved_files['textual_description'])
    assert os.path.exists(saved_files['structured_description'])
    
    # Verify content
    with open(saved_files['textual_description'], 'r') as f:
        content = f.read()
        assert 'Example Website' in content
    
    with open(saved_files['structured_description'], 'r') as f:
        data = json.load(f)
        assert data['page_title'] == 'Example Website'

def test_save_results_with_llm_analysis(output_dir, sample_results):
    handler = OutputHandler(output_dir=output_dir)
    
    # Add LLM analysis to results
    sample_results['llm_analysis'] = {
        'analysis_type': 'ux',
        'response': 'This is a UX analysis.'
    }
    
    saved_files = handler.save_results(
        sample_results,
        'https://example.com',
        include_timestamp=False
    )
    
    # Verify LLM analysis file was created
    assert 'llm_analysis' in saved_files
    assert os.path.exists(saved_files['llm_analysis'])
    
    # Verify content
    with open(saved_files['llm_analysis'], 'r') as f:
        content = f.read()
        assert 'UX analysis' in content

@patch('builtins.print')
def test_display_results(mock_print, sample_results):
    handler = OutputHandler()
    
    # Add saved files to results
    sample_results['saved_files'] = {
        'textual_description': '/path/to/example.md',
        'structured_description': '/path/to/example.json'
    }
    
    # Test displaying results
    handler.display_results(sample_results)
    
    # Verify print was called
    assert mock_print.call_count > 0