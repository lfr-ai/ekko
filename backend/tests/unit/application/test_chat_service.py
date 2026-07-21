import pytest

from ekko.application.services.chat_service import ChatService


class DummyGateway:
    def chat(self, *, system_prompt, user_prompt, model, temperature, max_completion_tokens):
        return f"echo:{user_prompt}"


@pytest.mark.unit
def test_chat_service_basic():
    svc = ChatService(gateway=DummyGateway())
    resp = svc.chat(system_prompt="sys", user_prompt="hello", model="m", temperature=0.1, max_completion_tokens=10)
    assert resp == "echo:hello"


@pytest.mark.unit
def test_chat_service_empty_user_prompt_raises_value_error():
    # Arrange
    svc = ChatService(gateway=DummyGateway())

    # Act / Assert
    with pytest.raises(ValueError, match="user_prompt must not be empty"):
        svc.chat(system_prompt="sys", user_prompt="", model="m", temperature=0.0, max_completion_tokens=10)
