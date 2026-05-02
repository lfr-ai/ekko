"""Tests for core enums."""

from ekko.core.enums import (
    AudioFormat,
    DeploymentTarget,
    Environment,
    FeatureFlag,
    LLMProvider,
    MessageRole,
    QueueName,
    STTProvider,
    TranscriptStatus,
    enum_values,
)


class TestEnvironmentEnum:
    def test_members_exist(self):
        assert Environment.LOCAL
        assert Environment.TEST

    def test_values_are_lowercase(self):
        for member in Environment:
            assert member.value == member.name.lower()

    def test_string_coercion(self):
        assert str(Environment.LOCAL) == "local"
        assert str(Environment.TEST) == "test"


class TestLLMProviderEnum:
    def test_all_members(self):
        names = {m.name for m in LLMProvider}
        assert "OPENAI" in names
        assert "AZURE_OPENAI" in names
        assert "ANTHROPIC" in names

    def test_values_are_lowercase(self):
        for member in LLMProvider:
            assert member.value == member.name.lower()


class TestEnumValues:
    def test_enum_values_returns_list(self):
        result = enum_values(Environment)
        assert isinstance(result, list)
        assert "local" in result
        assert "test" in result

    def test_all_str_enums_have_values(self):
        for enum_cls in [
            Environment,
            LLMProvider,
            STTProvider,
            AudioFormat,
            QueueName,
            TranscriptStatus,
            MessageRole,
            DeploymentTarget,
            FeatureFlag,
        ]:
            vals = enum_values(enum_cls)
            assert len(vals) > 0
            assert all(isinstance(v, str) for v in vals)


class TestEnumUniqueness:
    def test_no_duplicate_values(self):
        for enum_cls in [
            Environment,
            LLMProvider,
            STTProvider,
            AudioFormat,
            QueueName,
            TranscriptStatus,
            MessageRole,
            DeploymentTarget,
            FeatureFlag,
        ]:
            values = [m.value for m in enum_cls]
            assert len(values) == len(set(values)), f"Duplicate values in {enum_cls.__name__}"
