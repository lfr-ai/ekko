"""Property-based tests for settings invariants."""

from hypothesis import given, settings
from hypothesis import strategies as st

from ekko.config.enums import Environment
from ekko.config.settings.local import LocalConfig
from ekko.config.settings.test_env import TestingConfig

ALL_CONFIG_CLASSES = [LocalConfig, TestingConfig]


class TestSettingsInvariants:
    @given(st.sampled_from(ALL_CONFIG_CLASSES))
    @settings(max_examples=10)
    def test_all_configs_have_valid_environment(self, config_cls):
        cfg = config_cls()
        assert cfg.environment in Environment

    @given(st.sampled_from(ALL_CONFIG_CLASSES))
    @settings(max_examples=10)
    def test_all_configs_have_valid_port(self, config_cls):
        cfg = config_cls()
        assert 0 < cfg.port < 65536

    @given(st.sampled_from(ALL_CONFIG_CLASSES))
    @settings(max_examples=10)
    def test_all_configs_are_frozen(self, config_cls):
        cfg = config_cls()
        assert cfg.model_config.get("frozen") is True


class TestEnumProperties:
    @given(st.sampled_from(list(Environment)))
    def test_environment_roundtrip(self, env):
        """Environment value can be used to reconstruct the member."""
        assert Environment(env.value) is env

    @given(st.sampled_from(list(Environment)))
    def test_environment_is_str(self, env):
        assert isinstance(env, str)
        assert isinstance(env.value, str)
