from unittest.mock import MagicMock, patch

import pytest

from apsa.llm_providers import GroqProvider, LLMProviderFactory, MockProvider
from apsa.llm_providers.exceptions import ConfigurationError, RateLimitError


def test_factory_creates_mock_provider():
    provider = LLMProviderFactory.create("mock", "test-mock")
    assert isinstance(provider, MockProvider)
    assert provider.model_name == "test-mock"

def test_factory_unknown_provider():
    with pytest.raises(ConfigurationError):
        LLMProviderFactory.create("unsupported_provider", "some-model")

def test_groq_missing_api_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    with patch("apsa.llm_providers.base.load_env_file"):
        with pytest.raises(ConfigurationError) as exc_info:
            GroqProvider("llama-3.1-8b-instant")
        assert "GROQ_API_KEY" in str(exc_info.value)

def test_groq_successful_generation(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "mock-groq-key")
    provider = GroqProvider("llama-3.1-8b-instant")
    
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [{
            "message": {"content": "Generated from Groq"},
            "finish_reason": "length",
        }],
        "usage": {"prompt_tokens": 5, "completion_tokens": 3}
    }
    
    with patch("requests.post", return_value=mock_resp):
        res = provider.generate("Hello world", {"temperature": 0.0, "max_tokens": 50})
        assert res.output == "Generated from Groq"
        assert res.model_name == "llama-3.1-8b-instant"
        assert res.input_tokens == 5
        assert res.output_tokens == 3
        assert res.finish_reason == "length"


def test_groq_rate_limit_is_not_retried_or_slept_on(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "mock-groq-key")
    provider = GroqProvider("llama-3.1-8b-instant")

    mock_resp = MagicMock()
    mock_resp.status_code = 429
    mock_resp.headers = {"retry-after": "120"}
    mock_resp.text = "rate limit exceeded"

    with (
        patch("requests.post", return_value=mock_resp) as post,
        patch("apsa.llm_providers.groq_provider.time.sleep") as sleep,
        pytest.raises(RateLimitError, match="rate limit"),
    ):
        provider.generate("Hello world", {"temperature": 0.0, "max_tokens": 50})

    assert post.call_count == 1
    sleep.assert_not_called()
