"""Tests for core enums."""

import pytest

from ekko.config.enums import Environment, LLMProvider
from ekko.core.enums import (
    AudioFormat,
    DeploymentTarget,
    FeatureFlag,
    MessageRole,
    QueueName,
    RecognitionMode,
    STTProvider,
    TranscriptStatus,
    enum_values,
)


class TestEnvironmentEnum:
    def test_members_exist(self):
        assert Environment.LOCAL
        assert Environment.TEST
        assert Environment.DEV
        assert Environment.PROD

    def test_values_are_lowercase(self):
        for member in Environment:
            assert member.value == member.name.lower()

    def test_string_coercion(self):
        assert str(Environment.LOCAL) == "local"
        assert str(Environment.TEST) == "test"
        assert str(Environment.DEV) == "dev"
        assert str(Environment.PROD) == "prod"


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
        assert "dev" in result
        assert "prod" in result

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


@pytest.mark.unit
class TestParseableEnumFromStr:
    """Test ParseableEnum.from_str() for case-insensitive parsing and error handling."""

    def test_from_str_valid_value(self):
        # Arrange / Act
        result = STTProvider.from_str("azure_speech")

        # Assert
        assert result == STTProvider.AZURE_SPEECH

    def test_from_str_case_insensitive(self):
        # Arrange / Act
        result_upper = STTProvider.from_str("AZURE_SPEECH")
        result_mixed = QueueName.from_str("TrAnScRiPtS")

        # Assert
        assert result_upper == STTProvider.AZURE_SPEECH
        assert result_mixed == QueueName.TRANSCRIPTS

    def test_from_str_with_whitespace(self):
        # Arrange / Act
        result = STTProvider.from_str("  azure_speech  ")

        # Assert
        assert result == STTProvider.AZURE_SPEECH

    def test_from_str_invalid_value_raises_value_error(self):
        # Arrange / Act / Assert
        with pytest.raises(ValueError, match="'invalid' is not a valid STTProvider"):
            STTProvider.from_str("invalid")

    def test_from_str_empty_string_raises_value_error(self):
        # Arrange / Act / Assert
        with pytest.raises(ValueError, match="'' is not a valid STTProvider"):
            STTProvider.from_str("")


@pytest.mark.unit
class TestRecognitionModeFromStreamType:
    """Test RecognitionMode.from_stream_type() mapping and error handling."""

    def test_from_stream_type_sys_maps_to_customer(self):
        # Arrange / Act
        result = RecognitionMode.from_stream_type("sys")

        # Assert
        assert result == RecognitionMode.CUSTOMER

    def test_from_stream_type_mic_maps_to_advisor(self):
        # Arrange / Act
        result = RecognitionMode.from_stream_type("mic")

        # Assert
        assert result == RecognitionMode.ADVISOR

    def test_from_stream_type_invalid_raises_value_error(self):
        # Arrange / Act / Assert
        with pytest.raises(ValueError, match="Invalid stream type: 'unknown'"):
            RecognitionMode.from_stream_type("unknown")

    def test_from_stream_type_empty_raises_value_error(self):
        # Arrange / Act / Assert
        with pytest.raises(ValueError, match="Invalid stream type: ''"):
            RecognitionMode.from_stream_type("")
