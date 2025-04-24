import pytest
from unittest.mock import patch, MagicMock
from src.components.llm_integration import LLMIntegration

@pytest.fixture
def mock_anthropic_client():
    """Create a mock Anthropic client for testing."""
    with patch('anthropic.Client') as mock_client:
        # Mock the messages.create method to return a response
        mock_create = MagicMock()
        mock_response = MagicMock()
        mock_content = MagicMock()
        mock_content.text = "This is a mock analysis response"
        mock_response.content = [mock_content]
        mock_create.return_value = mock_response
        mock_client.return_value.messages.create = mock_create
        
        yield mock_client

def test_llm_integration_init():
    # Test initialization with API key
    api_key = "test_api_key"
    with patch('anthropic.Client') as mock_client:
        integration = LLMIntegration(api_key=api_key)
        mock_client.assert_called_once_with(api_key=api_key)
        assert integration.client == mock_client.return_value

def test_analyze_webpage_description(mock_anthropic_client):
    # Test analyze_webpage_description method
    integration = LLMIntegration(api_key="test_api_key")
    
    textual_description = "# Test Website\n\nThis is a test description."
    analysis_type = "ux"
    
    result = integration.analyze_webpage_description(
        textual_description=textual_description,
        analysis_type=analysis_type
    )
    
    # Check that the client was called with the correct prompt
    client = mock_anthropic_client.return_value
    call_args = client.messages.create.call_args[1]
    
    assert call_args['model'] == "claude-3-sonnet-20240229"
    assert call_args['max_tokens'] == 4000
    
    # Check that the messages contain our prompt and description
    messages = call_args['messages']
    assert len(messages) == 1
    assert messages[0]['role'] == 'user'
    assert textual_description in messages[0]['content']
    assert "UX perspective" in messages[0]['content']
    
    # Check the result structure
    assert result['analysis_type'] == analysis_type
    assert 'prompt' in result
    assert 'response' in result
    assert result['response'] == "This is a mock analysis response"

def test_analyze_webpage_description_custom_prompt(mock_anthropic_client):
    # Test with a custom prompt
    integration = LLMIntegration(api_key="test_api_key")
    
    textual_description = "# Test Website\n\nThis is a test description."
    custom_prompt = "Analyze this for technical SEO issues"
    
    result = integration.analyze_webpage_description(
        textual_description=textual_description,
        custom_prompt=custom_prompt
    )
    
    # Check that the custom prompt was used
    client = mock_anthropic_client.return_value
    call_args = client.messages.create.call_args[1]
    messages = call_args['messages']
    
    assert custom_prompt in messages[0]['content']
    assert result['prompt'] == custom_prompt

def test_analyze_webpage_description_error_handling():
    # Test error handling
    integration = LLMIntegration(api_key="test_api_key")
    
    # Mock the client to raise an exception
    with patch.object(integration.client.messages, 'create', side_effect=Exception("API Error")):
        result = integration.analyze_webpage_description(
            textual_description="Test",
            analysis_type="general"
        )
        
        # Check that the error is captured in the result
        assert 'error' in result
        assert 'API Error' in result['error']
        assert result['analysis_type'] == 'general'

def test_get_analysis_prompt():
    integration = LLMIntegration(api_key="test_api_key")
    
    # Test each analysis type
    general_prompt = integration._get_analysis_prompt("general")
    assert "Overall structure and layout" in general_prompt
    
    ux_prompt = integration._get_analysis_prompt("ux")
    assert "UX perspective" in ux_prompt
    
    accessibility_prompt = integration._get_analysis_prompt("accessibility")
    assert "accessibility perspective" in accessibility_prompt
    
    structure_prompt = integration._get_analysis_prompt("structure")
    assert "structure" in structure_prompt
    
    # Test fallback to general for unknown type
    unknown_prompt = integration._get_analysis_prompt("unknown_type")
    assert unknown_prompt == general_prompt