import pytest


@pytest.fixture(autouse=True)
def remove_api_key(monkeypatch):
    """Ensure ANTHROPIC_API_KEY is never set during tests unless explicitly re-added."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
