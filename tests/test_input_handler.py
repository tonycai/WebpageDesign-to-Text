import pytest
from src.components.input_handler import InputHandler

def test_validate_url_valid():
    handler = InputHandler()
    assert handler.validate_url("https://example.com") == True
    assert handler.validate_url("http://example.com") == True
    assert handler.validate_url("https://example.com/path/to/page") == True

def test_validate_url_invalid():
    handler = InputHandler()
    assert handler.validate_url("not a url") == False
    assert handler.validate_url("example.com") == False  # missing scheme
    assert handler.validate_url("https://") == False  # missing netloc

def test_process_url_valid():
    handler = InputHandler()
    url = "https://example.com"
    assert handler.process_url(url) == url

def test_process_url_invalid():
    handler = InputHandler()
    with pytest.raises(ValueError):
        handler.process_url("not a url")