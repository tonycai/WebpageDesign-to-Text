import pytest
import os
from unittest.mock import patch, MagicMock
from PIL import Image
import numpy as np
from src.components.gui_analyzer import GUIAnalyzer

# Mock image data for testing
@pytest.fixture
def mock_image():
    # Create a simple 100x100 test image
    img = Image.new('RGB', (100, 100), color='white')
    return img

@pytest.fixture
def mock_image_path(tmp_path, mock_image):
    # Save the mock image to a temporary path
    image_path = os.path.join(tmp_path, "test_screenshot.png")
    mock_image.save(image_path)
    return image_path

def test_gui_analyzer_init():
    analyzer = GUIAnalyzer()
    assert hasattr(analyzer, 'ui_element_types')
    assert isinstance(analyzer.ui_element_types, list)
    assert len(analyzer.ui_element_types) > 0
    
def test_extract_color_palette(mock_image):
    analyzer = GUIAnalyzer()
    palette = analyzer._extract_color_palette(mock_image, num_colors=3)
    
    assert isinstance(palette, list)
    assert len(palette) <= 3  # May be fewer if image has fewer unique colors
    
    # Check the structure of a color entry
    if palette:
        color = palette[0]
        assert 'hex' in color
        assert 'rgb' in color
        assert 'percentage' in color
        assert isinstance(color['hex'], str)
        assert isinstance(color['rgb'], tuple)
        assert isinstance(color['percentage'], float)
        
def test_is_similar_color():
    analyzer = GUIAnalyzer()
    
    # Test identical colors
    assert analyzer._is_similar_color((255, 255, 255), (255, 255, 255)) == True
    
    # Test similar colors
    assert analyzer._is_similar_color((255, 255, 255), (250, 250, 250)) == True
    
    # Test different colors
    assert analyzer._is_similar_color((255, 255, 255), (0, 0, 0)) == False

def test_simulate_ui_elements(mock_image):
    analyzer = GUIAnalyzer()
    elements = analyzer._simulate_ui_elements(mock_image)
    
    assert isinstance(elements, list)
    assert len(elements) > 0
    
    # Check structure of an element
    element = elements[0]
    assert 'type' in element
    assert 'bounding_box' in element
    assert 'confidence' in element
    
    # Check types
    assert isinstance(element['type'], str)
    assert isinstance(element['bounding_box'], list)
    assert isinstance(element['confidence'], float)
    
    # Check bounding box format
    assert len(element['bounding_box']) == 4  # Four corners
    
def test_infer_layout_pattern():
    analyzer = GUIAnalyzer()
    
    # Test with elements aligned in a column
    elements = [
        {'type': 'header', 'bounding_box': [(0, 0), (100, 50), (100, 50), (0, 0)]},
        {'type': 'text', 'bounding_box': [(0, 60), (100, 100), (100, 100), (0, 60)]},
        {'type': 'button', 'bounding_box': [(0, 110), (100, 150), (100, 150), (0, 110)]},
        {'type': 'footer', 'bounding_box': [(0, 160), (100, 200), (100, 200), (0, 160)]}
    ]
    pattern = analyzer._infer_layout_pattern(elements)
    assert isinstance(pattern, str)
    assert pattern in ['single-column', 'multi-column', 'standard-layout', 'complex-layout']
    
def test_analyze_screenshot(mock_image_path):
    analyzer = GUIAnalyzer()
    results = analyzer.analyze_screenshot(mock_image_path)
    
    assert isinstance(results, dict)
    assert 'ui_elements' in results
    assert 'color_palette' in results
    assert 'layout_pattern' in results
    assert 'image_dimensions' in results
    
    assert isinstance(results['ui_elements'], list)
    assert isinstance(results['color_palette'], list)
    assert isinstance(results['layout_pattern'], str)
    assert isinstance(results['image_dimensions'], dict)
    
    dimensions = results['image_dimensions']
    assert 'width' in dimensions
    assert 'height' in dimensions
    assert dimensions['width'] == 100
    assert dimensions['height'] == 100