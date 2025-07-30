import pytest
from unittest.mock import patch, MagicMock
import os
from dacp.llm import call_llm


@patch("dacp.llm.openai")
def test_call_llm_success(mock_openai):
    """Test successful LLM call."""
    # Mock the OpenAI client and response
    mock_client = MagicMock()
    mock_openai.OpenAI.return_value = mock_client

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Hello, world!"
    mock_client.chat.completions.create.return_value = mock_response

    # Test the function
    result = call_llm("Test prompt")

    # Verify the result
    assert result == "Hello, world!"

    # Verify OpenAI was called correctly
    mock_openai.OpenAI.assert_called_once_with(
        api_key=os.getenv("OPENAI_API_KEY"), base_url="https://api.openai.com/v1"
    )
    mock_client.chat.completions.create.assert_called_once_with(
        model="gpt-4",
        messages=[{"role": "user", "content": "Test prompt"}],
        temperature=0.7,
        max_tokens=150,
    )


@patch("dacp.llm.openai")
def test_call_llm_custom_model(mock_openai):
    """Test LLM call with custom model."""
    mock_client = MagicMock()
    mock_openai.OpenAI.return_value = mock_client

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Custom model response"
    mock_client.chat.completions.create.return_value = mock_response

    # Test with custom model
    result = call_llm("Test prompt", model="gpt-3.5-turbo")

    assert result == "Custom model response"

    # Verify custom model was used
    mock_client.chat.completions.create.assert_called_once_with(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Test prompt"}],
        temperature=0.7,
        max_tokens=150,
    )


@patch("dacp.llm.openai")
def test_call_llm_api_error(mock_openai):
    """Test LLM call with API error."""
    mock_client = MagicMock()
    mock_openai.OpenAI.return_value = mock_client

    # Mock an API error
    mock_client.chat.completions.create.side_effect = Exception("API Error")

    # Test that the error is raised
    with pytest.raises(Exception):
        call_llm("Test prompt")


@patch("dacp.llm.openai")
def test_call_llm_environment_variable(mock_openai):
    """Test that the function uses the OPENAI_API_KEY environment variable."""
    # Set a test API key
    test_api_key = "test-api-key-123"
    with patch.dict(os.environ, {"OPENAI_API_KEY": test_api_key}):
        mock_client = MagicMock()
        mock_openai.OpenAI.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_response

        call_llm("Test prompt")

        # Verify the API key was used
        mock_openai.OpenAI.assert_called_once_with(
            api_key=test_api_key, base_url="https://api.openai.com/v1"
        )


@patch("dacp.llm.openai")
def test_call_llm_default_parameters(mock_openai):
    """Test that default parameters are used correctly."""
    mock_client = MagicMock()
    mock_openai.OpenAI.return_value = mock_client

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Default response"
    mock_client.chat.completions.create.return_value = mock_response

    call_llm("Test prompt")

    # Verify default parameters
    call_args = mock_client.chat.completions.create.call_args
    assert call_args[1]["model"] == "gpt-4"
    assert call_args[1]["temperature"] == 0.7
    assert call_args[1]["max_tokens"] == 150
    assert call_args[1]["messages"] == [{"role": "user", "content": "Test prompt"}]
