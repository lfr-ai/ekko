"""Tests for CrewAI YAML config loader."""

import dataclasses

import pytest

from ekko.ai.crewai.yaml_config import AgentConfig, TaskConfig, YAMLConfigLoader


class TestYAMLConfigLoaderLoadAgents:
    def test_loads_from_config_dir(self, tmp_path):
        agents_yaml = tmp_path / "agents.yaml"
        agents_yaml.write_text(
            """
intent_detector:
  role: Intent Classifier
  goal: Classify user intent
  backstory: Expert at understanding user intent
  verbose: true
  allow_delegation: false
  max_iter: 5
  custom_field: extra_value
"""
        )
        loader = YAMLConfigLoader(config_dir=tmp_path)
        agents = loader.load_agents()

        assert "intent_detector" in agents
        cfg = agents["intent_detector"]
        assert isinstance(cfg, AgentConfig)
        assert cfg.role == "Intent Classifier"
        assert cfg.goal == "Classify user intent"
        assert cfg.backstory == "Expert at understanding user intent"
        assert cfg.verbose is True
        assert cfg.allow_delegation is False
        assert cfg.max_iter == 5
        assert cfg.extra == {"custom_field": "extra_value"}

    def test_defaults_for_optional_fields(self, tmp_path):
        agents_yaml = tmp_path / "agents.yaml"
        agents_yaml.write_text(
            """
basic_agent:
  role: Basic
  goal: Do stuff
  backstory: A basic agent
"""
        )
        loader = YAMLConfigLoader(config_dir=tmp_path)
        agents = loader.load_agents()

        cfg = agents["basic_agent"]
        assert cfg.verbose is False
        assert cfg.allow_delegation is False
        assert cfg.max_iter == 10
        assert cfg.extra == {}

    def test_missing_file_returns_empty(self, tmp_path):
        loader = YAMLConfigLoader(config_dir=tmp_path)
        agents = loader.load_agents()
        assert agents == {}

    def test_invalid_yaml_returns_empty(self, tmp_path):
        agents_yaml = tmp_path / "agents.yaml"
        agents_yaml.write_text("- just\n- a\n- list\n")
        loader = YAMLConfigLoader(config_dir=tmp_path)
        agents = loader.load_agents()
        assert agents == {}


class TestYAMLConfigLoaderLoadTasks:
    def test_loads_tasks(self, tmp_path):
        tasks_yaml = tmp_path / "tasks.yaml"
        tasks_yaml.write_text(
            """
classify_intent:
  description: Classify the user's intent
  expected_output: JSON with intent field
  agent: intent_detector
  extra_key: bonus
"""
        )
        loader = YAMLConfigLoader(config_dir=tmp_path)
        tasks = loader.load_tasks()

        assert "classify_intent" in tasks
        cfg = tasks["classify_intent"]
        assert isinstance(cfg, TaskConfig)
        assert cfg.description == "Classify the user's intent"
        assert cfg.expected_output == "JSON with intent field"
        assert cfg.agent_key == "intent_detector"
        assert cfg.extra == {"extra_key": "bonus"}

    def test_task_defaults(self, tmp_path):
        tasks_yaml = tmp_path / "tasks.yaml"
        tasks_yaml.write_text(
            """
simple:
  description: Do it
  expected_output: Done
"""
        )
        loader = YAMLConfigLoader(config_dir=tmp_path)
        tasks = loader.load_tasks()

        cfg = tasks["simple"]
        assert cfg.agent_key == ""
        assert cfg.extra == {}

    def test_missing_tasks_file(self, tmp_path):
        loader = YAMLConfigLoader(config_dir=tmp_path)
        tasks = loader.load_tasks()
        assert tasks == {}


class TestConfigImmutability:
    def test_agent_config_frozen(self):
        cfg = AgentConfig(role="r", goal="g", backstory="b")
        with pytest.raises(dataclasses.FrozenInstanceError):
            cfg.role = "new"  # type: ignore[misc]

    def test_task_config_frozen(self):
        cfg = TaskConfig(description="d", expected_output="e")
        with pytest.raises(dataclasses.FrozenInstanceError):
            cfg.description = "new"  # type: ignore[misc]
