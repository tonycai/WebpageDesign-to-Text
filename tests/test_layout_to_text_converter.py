import pytest
from src.components.layout_to_text_converter import LayoutToTextConverter

@pytest.fixture
def sample_ui_analysis():
    """Sample UI analysis for testing."""
    return {
        'ui_elements': [
            {
                'type': 'header',
                'bounding_box': [(0, 0), (1000, 100), (1000, 100), (0, 0)],
                'confidence': 0.95
            },
            {
                'type': 'button',
                'bounding_box': [(500, 200), (700, 250), (700, 250), (500, 200)],
                'confidence': 0.92
            }
        ],
        'color_palette': [
            {'hex': '#ffffff', 'rgb': (255, 255, 255), 'percentage': 60.5},
            {'hex': '#0066cc', 'rgb': (0, 102, 204), 'percentage': 25.3}
        ],
        'layout_pattern': 'standard-layout',
        'image_dimensions': {'width': 1000, 'height': 800}
    }

@pytest.fixture
def sample_ocr_results():
    """Sample OCR results for testing."""
    return {
        'full_text': 'Example Website\nWelcome to our site\nClick here',
        'text_blocks': [
            {
                'text': 'Example Website',
                'bounding_box': [(10, 10), (200, 10), (200, 50), (10, 50)]
            },
            {
                'text': 'Welcome to our site',
                'bounding_box': [(10, 60), (300, 60), (300, 100), (10, 100)]
            },
            {
                'text': 'Click here',
                'bounding_box': [(550, 210), (650, 210), (650, 240), (550, 240)]
            }
        ]
    }

@pytest.fixture
def sample_page_info():
    """Sample page info for testing."""
    return {
        'page_title': 'Example Website',
        'page_metadata': {
            'description': 'This is an example website for testing',
            'keywords': 'example, test, website'
        },
        'page_dimensions': {'width': 1000, 'height': 800}
    }

def test_layout_to_text_converter_init():
    converter = LayoutToTextConverter()
    assert isinstance(converter, LayoutToTextConverter)

def test_describe_color_palette():
    converter = LayoutToTextConverter()
    
    # Test with empty palette
    empty_result = converter._describe_color_palette([])
    assert isinstance(empty_result, dict)
    assert 'description' in empty_result
    assert 'No color information' in empty_result['description']
    
    # Test with populated palette
    palette = [
        {'hex': '#ffffff', 'rgb': (255, 255, 255), 'percentage': 60.5},
        {'hex': '#0066cc', 'rgb': (0, 102, 204), 'percentage': 25.3}
    ]
    result = converter._describe_color_palette(palette)
    assert isinstance(result, dict)
    assert 'primary_colors' in result
    assert 'description' in result
    assert len(result['primary_colors']) == 2
    assert '#ffffff' in result['description']
    assert '#0066cc' in result['description']

def test_get_position_description():
    converter = LayoutToTextConverter()
    
    # Test top left
    pos = converter._get_position_description(0.1, 0.1, 0.3, 0.3)
    assert pos['horizontal'] == 'left'
    assert pos['vertical'] == 'top'
    assert pos['description'] == 'top left'
    
    # Test middle center
    pos = converter._get_position_description(0.4, 0.4, 0.6, 0.6)
    assert pos['horizontal'] == 'center'
    assert pos['vertical'] == 'middle'
    assert pos['description'] == 'middle center'
    
    # Test bottom right
    pos = converter._get_position_description(0.7, 0.7, 0.9, 0.9)
    assert pos['horizontal'] == 'right'
    assert pos['vertical'] == 'bottom'
    assert pos['description'] == 'bottom right'

def test_describe_metadata():
    converter = LayoutToTextConverter()
    
    # Test with empty metadata
    empty_result = converter._describe_metadata({})
    assert 'description' in empty_result
    assert 'No relevant metadata' in empty_result['description']
    
    # Test with populated metadata
    metadata = {
        'description': 'This is a test',
        'keywords': 'test, example',
        'author': 'Test Author',
        'irrelevant': 'This should be ignored'
    }
    result = converter._describe_metadata(metadata)
    assert 'tags' in result
    assert 'description' in result
    assert len(result['tags']) == 3  # Only relevant tags
    assert 'irrelevant' not in result['tags']
    assert 'description' in result['tags']

def test_find_text_in_element():
    converter = LayoutToTextConverter()
    
    element_bbox = [(0, 0), (100, 0), (100, 100), (0, 100)]
    text_blocks = [
        {'text': 'Inside Element', 'bounding_box': [(10, 10), (90, 10), (90, 90), (10, 90)]},
        {'text': 'Outside Element', 'bounding_box': [(110, 10), (200, 10), (200, 90), (110, 90)]}
    ]
    
    result = converter._find_text_in_element(element_bbox, text_blocks)
    assert 'Inside Element' in result
    assert 'Outside Element' not in result

def test_convert_to_text(sample_ui_analysis, sample_ocr_results, sample_page_info):
    converter = LayoutToTextConverter()
    
    results = converter.convert_to_text(
        ui_analysis=sample_ui_analysis,
        ocr_results=sample_ocr_results,
        page_info=sample_page_info
    )
    
    # Check return structure
    assert 'structured_description' in results
    assert 'textual_description' in results
    assert 'json_output' in results
    
    # Check structured description
    structured = results['structured_description']
    assert structured['page_title'] == 'Example Website'
    assert structured['layout_pattern'] == 'standard-layout'
    assert 'color_palette' in structured
    assert 'ui_elements' in structured
    
    # Check textual description
    text_desc = results['textual_description']
    assert 'Example Website' in text_desc
    assert 'standard-layout' in text_desc
    assert 'UI Elements' in text_desc
    
    # Check JSON output
    assert isinstance(results['json_output'], str)
    assert 'Example Website' in results['json_output']