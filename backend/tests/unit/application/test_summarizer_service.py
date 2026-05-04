from pathlib import Path
from unittest.mock import Mock

import pytest

from ekko.application.services.summarizer_service import SummarizerService


class DummyGateway:
    def chat(self, *, system_prompt, user_prompt, model, temperature, max_completion_tokens):
        return "summary:" + user_prompt[:20]


@pytest.mark.unit
def test_summarizer_basic():
    svc = SummarizerService(gateway=DummyGateway())
    chunks = ["This is a first chunk.", "Second chunk with more details."]
    s = svc.summarize(chunks)
    assert s.startswith("summary:")


@pytest.mark.unit
def test_summarizer_file_not_found_uses_fallback():
    # Arrange
    gateway = DummyGateway()
    # Create a mock settings object with a nonexistent prompt path
    settings = Mock()
    settings.prompt_dir_path = Path("/nonexistent/path")
    settings.rag_llm_model = "test-model"

    svc = SummarizerService(gateway=gateway, settings=settings)
    chunks = ["Test chunk"]

    # Act
    result = svc.summarize(chunks)

    # Assert
    # Should use fallback template and still return a result
    assert result.startswith("summary:")
