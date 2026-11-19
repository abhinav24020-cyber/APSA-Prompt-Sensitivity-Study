class LLMProviderError(Exception):
    """Base class for all LLM provider exceptions."""

class ConfigurationError(LLMProviderError):
    """Raised when there is an issue with the provider configuration (e.g., missing API keys)."""

class GenerationError(LLMProviderError):
    """Raised when model generation fails after retries."""


class RateLimitError(GenerationError):
    """Raised when a provider rejects a request because of rate limits."""

    def __init__(
        self,
        message: str,
        retry_after: float | None = None,
        scope: str | None = None,
    ) -> None:
        super().__init__(message)
        self.retry_after = retry_after
        # "minute" for short sliding-window limits (TPM/RPM), "day" for daily quotas,
        # None when the provider response does not say.
        self.scope = scope


def classify_rate_limit_scope(message: str) -> str | None:
    """Classify a provider rate-limit message as a per-minute or per-day limit."""
    text = message.casefold()
    if "per day" in text or "perday" in text or "(tpd)" in text or "(rpd)" in text:
        return "day"
    if "per minute" in text or "perminute" in text or "(tpm)" in text or "(rpm)" in text:
        return "minute"
    return None


def parse_retry_after_text(message: str) -> float | None:
    """Extract a wait such as 'try again in 1m2.5s' or '"retryDelay": "38s"' from text."""
    import re

    match = re.search(r"try again in\s+(?:(\d+)h)?(?:(\d+)m(?!s))?(?:([\d.]+)s)?", message)
    if match and any(match.groups()):
        hours, minutes, seconds = match.groups()
        return int(hours or 0) * 3600 + int(minutes or 0) * 60 + float(seconds or 0)
    match = re.search(r"retryDelay['\"]?\s*[:=]\s*['\"]?([\d.]+)s", message)
    if match:
        return float(match.group(1))
    match = re.search(r"try again in\s+([\d.]+)\s*ms", message)
    if match:
        return float(match.group(1)) / 1000
    return None
