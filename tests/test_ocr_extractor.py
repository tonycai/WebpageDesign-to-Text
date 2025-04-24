import pytest
from unittest.mock import patch, MagicMock
import io
from src.components.ocr_extractor import OCRExtractor

@pytest.fixture
def mock_vision_client():
    """Create a mock Google Cloud Vision client."""
    with patch('google.cloud.vision.ImageAnnotatorClient') as mock_client:
        # Create a mock text detection response
        mock_response = MagicMock()
        mock_response.error = MagicMock()
        mock_response.error.message = ""
        
        # Create mock text annotations
        mock_full_text = MagicMock()
        mock_full_text.description = "This is the full extracted text."
        
        mock_text1 = MagicMock()
        mock_text1.description = "This is"
        mock_vertex1 = MagicMock()
        mock_vertex1.x, mock_vertex1.y = 10, 10
        mock_vertex2 = MagicMock()
        mock_vertex2.x, mock_vertex2.y = 50, 10
        mock_vertex3 = MagicMock()
        mock_vertex3.x, mock_vertex3.y = 50, 30
        mock_vertex4 = MagicMock()
        mock_vertex4.x, mock_vertex4.y = 10, 30
        mock_text1.bounding_poly.vertices = [mock_vertex1, mock_vertex2, mock_vertex3, mock_vertex4]
        
        mock_text2 = MagicMock()
        mock_text2.description = "the full"
        mock_text2.bounding_poly.vertices = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        for i, vertex in enumerate(mock_text2.bounding_poly.vertices):
            vertex.x, vertex.y = (60 + i*10, 10 + i*5)
        
        mock_response.text_annotations = [mock_full_text, mock_text1, mock_text2]
        
        # Create mock label annotations
        mock_label1 = MagicMock()
        mock_label1.description = "Screenshot"
        mock_label2 = MagicMock()
        mock_label2.description = "Text"
        mock_response.label_annotations = [mock_label1, mock_label2]
        
        # Configure the mock client methods
        mock_client.return_value.text_detection = MagicMock(return_value=mock_response)
        mock_client.return_value.label_detection = MagicMock(return_value=mock_response)
        
        yield mock_client

def test_ocr_extractor_init_with_credentials():
    # Test initialization with credentials path
    with patch('google.cloud.vision.ImageAnnotatorClient.from_service_account_json') as mock_from_json:
        credentials_path = "/path/to/credentials.json"
        extractor = OCRExtractor(credentials_path=credentials_path)
        
        mock_from_json.assert_called_once_with(credentials_path)
        assert extractor.client == mock_from_json.return_value

def test_ocr_extractor_init_without_credentials():
    # Test initialization without credentials (uses default client)
    with patch('google.cloud.vision.ImageAnnotatorClient') as mock_client:
        extractor = OCRExtractor()
        
        mock_client.assert_called_once()
        assert extractor.client == mock_client.return_value

@patch('io.open')
def test_extract_text(mock_open, mock_vision_client):
    # Test the extract_text method
    mock_file = MagicMock(spec=io.BufferedReader)
    mock_file.read.return_value = b"fake image data"
    mock_open.return_value.__enter__.return_value = mock_file
    
    extractor = OCRExtractor()
    result = extractor.extract_text("/path/to/image.png")
    
    # Verify file was opened and read
    mock_open.assert_called_once_with("/path/to/image.png", 'rb')
    mock_file.read.assert_called_once()
    
    # Verify vision client was called with correct image
    client = mock_vision_client.return_value
    vision_call_args = client.text_detection.call_args[1]
    assert 'image' in vision_call_args
    
    # Verify result structure
    assert 'full_text' in result
    assert 'text_blocks' in result
    
    assert result['full_text'] == "This is the full extracted text."
    assert len(result['text_blocks']) == 2
    
    # Verify text block structure
    text_block = result['text_blocks'][0]
    assert 'text' in text_block
    assert 'bounding_box' in text_block
    assert text_block['text'] == "This is"
    assert isinstance(text_block['bounding_box'], list)
    assert len(text_block['bounding_box']) == 4  # Four vertices

@patch('io.open')
def test_extract_text_error_handling(mock_open, mock_vision_client):
    # Test error handling in extract_text
    mock_file = MagicMock(spec=io.BufferedReader)
    mock_file.read.return_value = b"fake image data"
    mock_open.return_value.__enter__.return_value = mock_file
    
    # Set up the response to have an error
    client = mock_vision_client.return_value
    mock_response = client.text_detection.return_value
    mock_response.error.message = "API Error"
    
    extractor = OCRExtractor()
    
    # The method should raise an exception
    with pytest.raises(Exception) as excinfo:
        extractor.extract_text("/path/to/image.png")
    
    # Verify the error message
    assert "Error in OCR text extraction: API Error" in str(excinfo.value)

@patch('io.open')
def test_detect_labels(mock_open, mock_vision_client):
    # Test the detect_labels method
    mock_file = MagicMock(spec=io.BufferedReader)
    mock_file.read.return_value = b"fake image data"
    mock_open.return_value.__enter__.return_value = mock_file
    
    extractor = OCRExtractor()
    result = extractor.detect_labels("/path/to/image.png")
    
    # Verify file was opened and read
    mock_open.assert_called_once_with("/path/to/image.png", 'rb')
    mock_file.read.assert_called_once()
    
    # Verify vision client was called with correct image
    client = mock_vision_client.return_value
    vision_call_args = client.label_detection.call_args[1]
    assert 'image' in vision_call_args
    
    # Verify result
    assert isinstance(result, list)
    assert len(result) == 2
    assert "Screenshot" in result
    assert "Text" in result

@patch('io.open')
def test_detect_labels_error_handling(mock_open, mock_vision_client):
    # Test error handling in detect_labels
    mock_file = MagicMock(spec=io.BufferedReader)
    mock_file.read.return_value = b"fake image data"
    mock_open.return_value.__enter__.return_value = mock_file
    
    # Set up the response to have an error
    client = mock_vision_client.return_value
    mock_response = client.label_detection.return_value
    mock_response.error.message = "API Error"
    
    extractor = OCRExtractor()
    
    # The method should raise an exception
    with pytest.raises(Exception) as excinfo:
        extractor.detect_labels("/path/to/image.png")
    
    # Verify the error message
    assert "Error in label detection: API Error" in str(excinfo.value)