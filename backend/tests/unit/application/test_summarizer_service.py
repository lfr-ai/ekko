import pytest

from ekko.application.services.summarizer_service import SummarizerService
from ekko.core.ports import PromptProviderError


class DummyGateway:
    def chat(self, *, system_prompt, user_prompt, model, temperature, max_completion_tokens):
        return "summary:" + user_prompt[:20]


class DummyPromptProvider:
    def __init__(self, text: str = "Summarize:\n{content}"):
        self._text = text

    def get_prompt_text(self, prompt_key: str) -> str:
        return self._text


class FailingPromptProvider:
    def get_prompt_text(self, prompt_key: str) -> str:
        raise PromptProviderError("not found")


@pytest.mark.unit
def test_summarizer_basic():
    svc = SummarizerService(gateway=DummyGateway(), prompt_provider=DummyPromptProvider())
    chunks = ["This is a first chunk.", "Second chunk with more details."]
    s = svc.summarize(chunks)
    assert s.startswith("summary:")


@pytest.mark.unit
def test_summarizer_file_not_found_uses_fallback():
    gateway = DummyGateway()
    svc = SummarizerService(gateway=gateway, prompt_provider=FailingPromptProvider())
    chunks = ["Test chunk"]

    result = svc.summarize(chunks)

    # Should use fallback template and still return a result
    assert result.startswith("summary:")
