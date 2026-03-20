"""Tests for OpenAI-compatible LLM client (mocked requests)."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from humanql.llm import OpenAIClient


def test_generate_returns_trimmed_content() -> None:
    """On 200 response, client returns trimmed assistant content."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [
            {"message": {"content": "  SELECT 1;  "}}
        ]
    }
    with patch("humanql.llm.requests.post", return_value=mock_response):
        client = OpenAIClient(base_url="https://api.example.com", api_key="sk-x", model="gpt-4")
        result = client.generate("You are a SQL generator.", "List all users")
    assert result == "SELECT 1;"
    mock_response.json.assert_called_once()


def test_generate_non_200_raises() -> None:
    """On non-200 status, client raises with status and body."""
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"
    mock_response.raise_for_status.side_effect = requests.HTTPError("401")
    with patch("humanql.llm.requests.post", return_value=mock_response):
        client = OpenAIClient(base_url="https://api.example.com", api_key="sk-x", model="gpt-4")
        with pytest.raises(Exception) as exc_info:
            client.generate("system", "user")
    assert "401" in str(exc_info.value) or "Unauthorized" in str(exc_info.value)


def test_generate_empty_choices_raises() -> None:
    """When response has no choices, client raises."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"choices": []}
    with patch("humanql.llm.requests.post", return_value=mock_response):
        client = OpenAIClient(base_url="https://api.example.com", api_key="sk-x", model="gpt-4")
        with pytest.raises(ValueError) as exc_info:
            client.generate("system", "user")
    assert "choices" in str(exc_info.value).lower() or "no" in str(exc_info.value).lower()


def test_generate_sends_correct_request() -> None:
    """Request has correct URL, Authorization header, and body (model, messages)."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"choices": [{"message": {"content": "ok"}}]}
    with patch("humanql.llm.requests.post", return_value=mock_response) as mock_post:
        client = OpenAIClient(
            base_url="https://api.example.com/v1",
            api_key="sk-secret",
            model="gpt-4o",
        )
        client.generate("system prompt", "user prompt")
    mock_post.assert_called_once()
    call_kwargs = mock_post.call_args
    assert call_kwargs[0][0] == "https://api.example.com/v1/chat/completions"
    assert call_kwargs[1]["headers"]["Authorization"] == "Bearer sk-secret"
    assert call_kwargs[1]["headers"]["Content-Type"] == "application/json"
    body = call_kwargs[1]["json"]
    assert body["model"] == "gpt-4o"
    assert body["messages"] == [
        {"role": "system", "content": "system prompt"},
        {"role": "user", "content": "user prompt"},
    ]
