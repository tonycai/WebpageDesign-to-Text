import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import os
import asyncio
from src.components.webpage_renderer import WebpageRenderer

@pytest.fixture
def mock_browser():
    """Create a mock pyppeteer browser"""
    browser_mock = AsyncMock()
    page_mock = AsyncMock()
    
    # Setup page mock methods
    page_mock.goto = AsyncMock()
    page_mock.evaluate = AsyncMock(return_value={'width': 1000, 'height': 800})
    page_mock.setViewport = AsyncMock()
    page_mock.screenshot = AsyncMock()
    page_mock.title = AsyncMock(return_value="Test Page")
    
    # Metadata evaluation mock
    metadata_mock = AsyncMock(return_value={
        'description': 'Test description',
        'keywords': 'test, keywords'
    })
    page_mock.evaluate.side_effect = [
        {'width': 1000, 'height': 800},  # First call for page dimensions
        metadata_mock.return_value       # Second call for metadata
    ]
    
    # Setup browser mock methods
    browser_mock.newPage = AsyncMock(return_value=page_mock)
    browser_mock.close = AsyncMock()
    
    return {
        'browser': browser_mock,
        'page': page_mock
    }

@pytest.fixture
def tmp_output_dir(tmp_path):
    """Create a temporary output directory."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return str(output_dir)

@patch('pyppeteer.launch')
def test_render_webpage(mock_launch, mock_browser, tmp_output_dir):
    # Configure the mock
    mock_launch.return_value = asyncio.Future()
    mock_launch.return_value.set_result(mock_browser['browser'])
    
    # Create a screenshot path in the temporary directory
    screenshot_path = os.path.join(tmp_output_dir, 'screenshot.png')
    
    # Create the renderer
    renderer = WebpageRenderer()
    
    # Run the render_webpage method
    result = renderer.render_webpage('https://example.com', output_path=screenshot_path)
    
    # Verify launch was called
    mock_launch.assert_called_once()
    
    # Verify browser.newPage was called
    mock_browser['browser'].newPage.assert_called_once()
    
    # Verify page.goto was called with the correct URL
    page = mock_browser['page']
    page.goto.assert_called_once_with(
        'https://example.com', 
        {'waitUntil': 'networkidle0', 'timeout': 60000}
    )
    
    # Verify page.evaluate was called to get dimensions
    assert page.evaluate.call_count == 2
    
    # Verify page.setViewport was called with the dimensions
    page.setViewport.assert_called_once_with({
        'width': 1000,
        'height': 800
    })
    
    # Verify page.screenshot was called with the right path and fullPage option
    page.screenshot.assert_called_once_with({'path': screenshot_path, 'fullPage': True})
    
    # Verify browser.close was called
    mock_browser['browser'].close.assert_called_once()
    
    # Verify the result structure
    assert 'screenshot_path' in result
    assert 'page_title' in result
    assert 'page_dimensions' in result
    assert 'page_metadata' in result
    
    assert result['screenshot_path'] == screenshot_path
    assert result['page_title'] == 'Test Page'
    assert result['page_dimensions'] == {'width': 1000, 'height': 800}
    assert result['page_metadata'] == {
        'description': 'Test description',
        'keywords': 'test, keywords'
    }

@patch('asyncio.get_event_loop')
@patch('pyppeteer.launch')
def test_capture_screenshot_exception(mock_launch, mock_get_event_loop, mock_browser):
    # Configure the mocks
    mock_launch.return_value = asyncio.Future()
    mock_launch.return_value.set_result(mock_browser['browser'])
    
    # Make page.goto raise an exception
    page = mock_browser['page']
    page.goto.side_effect = Exception("Connection error")
    
    # Mock get_event_loop to return a mock loop
    mock_loop = MagicMock()
    mock_loop.run_until_complete = MagicMock(side_effect=lambda x: asyncio.run(x))
    mock_get_event_loop.return_value = mock_loop
    
    # Create the renderer
    renderer = WebpageRenderer()
    
    # Run the capture_screenshot method with exception handling in the test
    with pytest.raises(Exception):
        # This should fail because page.goto raises an exception
        renderer.render_webpage('https://example.com')
    
    # Verify browser.close was still called (cleanup)
    mock_browser['browser'].close.assert_called_once()