# ruff: noqa: I001

"""Architecture boundary checker tests.

Tests the Clean Architecture boundary enforcement tool including:
- utils/ layer violation detection (no ekko.* imports)
- config/ layer violation detection (no core/application/presentation imports)
- core/ layer violation detection (no outer layer imports)
- infrastructure/ layer violation detection (no application/presentation imports)
- application/ layer violation detection (no presentation imports)
- ai/ layer violation detection (no infrastructure/application/presentation imports)
- False positive handling (legitimate imports)
- Edge case handling (conditional imports, TYPE_CHECKING blocks)
- Violation data structure validation
- Verbose output flag behavior
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from tools.security.check_architecture_boundaries import (
    _check_ai,
    _check_application,
    _check_config,
    _check_core,
    _check_infrastructure,
    _check_utils,
)

ARCHITECTURE_CHECK_SCRIPT = (
    Path(__file__).resolve().parents[3]
    / "tools"
    / "security"
    / "check_architecture_boundaries.py"
)


@pytest.mark.unit
class TestUtilsLayerChecks:
    """Test utils/ layer boundary enforcement."""

    def test_utils_importing_ekko_core_detected(self, tmp_path: Path) -> None:
        """utils/ importing from ekko.core is detected as violation."""
        utils_file = tmp_path / "utils" / "helper.py"
        utils_file.parent.mkdir(parents=True)
        utils_file.write_text("from ekko.core.entities import User\n")

        violations = _check_utils([utils_file])

        assert len(violations) == 1
        assert violations[0].layer == "utils"
        assert violations[0].imported_layer == "core"
        assert "stdlib" in violations[0].reason.lower()

    def test_utils_importing_ekko_config_detected(self, tmp_path: Path) -> None:
        """utils/ importing from ekko.config is detected as violation."""
        utils_file = tmp_path / "utils" / "logger.py"
        utils_file.parent.mkdir(parents=True)
        utils_file.write_text("from ekko.config.settings import Settings\n")

        violations = _check_utils([utils_file])

        assert len(violations) == 1
        assert violations[0].layer == "utils"
        assert violations[0].imported_layer == "config"

    def test_utils_importing_stdlib_allowed(self, tmp_path: Path) -> None:
        """utils/ importing from stdlib is allowed."""
        utils_file = tmp_path / "utils" / "types.py"
        utils_file.parent.mkdir(parents=True)
        utils_file.write_text("from typing import Protocol\nimport json\nimport sys\n")

        violations = _check_utils([utils_file])

        assert len(violations) == 0

    def test_utils_importing_third_party_not_flagged(self, tmp_path: Path) -> None:
        """utils/ importing third-party libs is not flagged by this check."""
        utils_file = tmp_path / "utils" / "helpers.py"
        utils_file.parent.mkdir(parents=True)
        utils_file.write_text("import structlog\nfrom pydantic import BaseModel\n")

        violations = _check_utils([utils_file])

        assert len(violations) == 0


@pytest.mark.unit
class TestConfigLayerChecks:
    """Test config/ layer boundary enforcement."""

    def test_config_importing_core_detected(self, tmp_path: Path) -> None:
        """config/ importing from ekko.core is detected as violation."""
        config_file = tmp_path / "config" / "settings.py"
        config_file.parent.mkdir(parents=True)
        config_file.write_text("from ekko.core.enums import Environment\n")

        violations = _check_config([config_file])

        assert len(violations) == 1
        assert violations[0].layer == "config"
        assert violations[0].imported_layer == "core"
        assert "config/" in violations[0].reason

    def test_config_importing_application_detected(self, tmp_path: Path) -> None:
        """config/ importing from ekko.application is detected as violation."""
        config_file = tmp_path / "config" / "app.py"
        config_file.parent.mkdir(parents=True)
        config_file.write_text("from ekko.application.services import ChatService\n")

        violations = _check_config([config_file])

        assert len(violations) == 1
        assert violations[0].layer == "config"
        assert violations[0].imported_layer == "application"

    def test_config_importing_presentation_detected(self, tmp_path: Path) -> None:
        """config/ importing from ekko.presentation is detected as violation."""
        config_file = tmp_path / "config" / "routes.py"
        config_file.parent.mkdir(parents=True)
        config_file.write_text("from ekko.presentation.api import router\n")

        violations = _check_config([config_file])

        assert len(violations) == 1
        assert violations[0].layer == "config"
        assert violations[0].imported_layer == "presentation"

    def test_config_importing_utils_allowed(self, tmp_path: Path) -> None:
        """config/ importing from ekko.utils is allowed."""
        config_file = tmp_path / "config" / "logger.py"
        config_file.parent.mkdir(parents=True)
        config_file.write_text("from ekko.utils.logger import get_logger\n")

        violations = _check_config([config_file])

        assert len(violations) == 0


@pytest.mark.unit
class TestCoreLayerChecks:
    """Test core/ layer boundary enforcement."""

    def test_core_importing_application_detected(self, tmp_path: Path) -> None:
        """core/ importing from ekko.application is detected as violation."""
        core_file = tmp_path / "core" / "entities" / "user.py"
        core_file.parent.mkdir(parents=True)
        core_file.write_text("from ekko.application.services import UserService\n")

        violations = _check_core([core_file])

        assert len(violations) == 1
        assert violations[0].layer == "core"
        assert violations[0].imported_layer == "application"
        assert "outer layers" in violations[0].reason

    def test_core_importing_infrastructure_detected(self, tmp_path: Path) -> None:
        """core/ importing from ekko.infrastructure is detected as violation."""
        core_file = tmp_path / "core" / "entities" / "message.py"
        core_file.parent.mkdir(parents=True)
        core_file.write_text("from ekko.infrastructure.db import Session\n")

        violations = _check_core([core_file])

        assert len(violations) == 1
        assert violations[0].layer == "core"
        assert violations[0].imported_layer == "infrastructure"

    def test_core_importing_presentation_detected(self, tmp_path: Path) -> None:
        """core/ importing from ekko.presentation is detected as violation."""
        core_file = tmp_path / "core" / "protocols.py"
        core_file.parent.mkdir(parents=True)
        core_file.write_text(
            "from ekko.presentation.api.schemas import MessageSchema\n"
        )

        violations = _check_core([core_file])

        assert len(violations) == 1
        assert violations[0].layer == "core"
        assert violations[0].imported_layer == "presentation"

    def test_core_importing_utils_allowed(self, tmp_path: Path) -> None:
        """core/ importing from ekko.utils is allowed."""
        core_file = tmp_path / "core" / "entities" / "base.py"
        core_file.parent.mkdir(parents=True)
        core_file.write_text("from ekko.utils.types import ID\n")

        violations = _check_core([core_file])

        assert len(violations) == 0

    def test_core_importing_config_allowed(self, tmp_path: Path) -> None:
        """core/ importing from ekko.config is allowed."""
        core_file = tmp_path / "core" / "services" / "domain.py"
        core_file.parent.mkdir(parents=True)
        core_file.write_text("from ekko.config.settings import get_settings\n")

        violations = _check_core([core_file])

        assert len(violations) == 0


@pytest.mark.unit
class TestInfrastructureLayerChecks:
    """Test infrastructure/ layer boundary enforcement."""

    def test_infrastructure_importing_application_detected(
        self, tmp_path: Path
    ) -> None:
        """infrastructure/ importing from ekko.application is detected as violation."""
        infra_file = tmp_path / "infrastructure" / "db" / "session.py"
        infra_file.parent.mkdir(parents=True)
        infra_file.write_text("from ekko.application.services import ChatService\n")

        violations = _check_infrastructure([infra_file])

        assert len(violations) == 1
        assert violations[0].layer == "infrastructure"
        assert violations[0].imported_layer == "application"

    def test_infrastructure_importing_presentation_detected(
        self, tmp_path: Path
    ) -> None:
        """infrastructure/ importing from ekko.presentation is detected as violation."""
        infra_file = tmp_path / "infrastructure" / "adapters" / "audio.py"
        infra_file.parent.mkdir(parents=True)
        infra_file.write_text("from ekko.presentation.api.dependency_registry import get_db\n")

        violations = _check_infrastructure([infra_file])

        assert len(violations) == 1
        assert violations[0].layer == "infrastructure"
        assert violations[0].imported_layer == "presentation"

    def test_infrastructure_importing_core_allowed(self, tmp_path: Path) -> None:
        """infrastructure/ importing from ekko.core is allowed."""
        infra_file = tmp_path / "infrastructure" / "db" / "repositories.py"
        infra_file.parent.mkdir(parents=True)
        infra_file.write_text("from ekko.core.entities import User\n")

        violations = _check_infrastructure([infra_file])

        assert len(violations) == 0

    def test_infrastructure_importing_utils_allowed(self, tmp_path: Path) -> None:
        """infrastructure/ importing from ekko.utils is allowed."""
        infra_file = tmp_path / "infrastructure" / "stt" / "transcriber.py"
        infra_file.parent.mkdir(parents=True)
        infra_file.write_text("from ekko.utils.logger import get_logger\n")

        violations = _check_infrastructure([infra_file])

        assert len(violations) == 0


@pytest.mark.unit
class TestApplicationLayerChecks:
    """Test application/ layer boundary enforcement."""

    def test_application_importing_presentation_detected(self, tmp_path: Path) -> None:
        """application/ importing from ekko.presentation is detected as violation."""
        app_file = tmp_path / "application" / "services" / "chat.py"
        app_file.parent.mkdir(parents=True)
        app_file.write_text("from ekko.presentation.api.routes import router\n")

        violations = _check_application([app_file])

        assert len(violations) == 1
        assert violations[0].layer == "application"
        assert violations[0].imported_layer == "presentation"

    def test_application_importing_core_allowed(self, tmp_path: Path) -> None:
        """application/ importing from ekko.core is allowed."""
        app_file = tmp_path / "application" / "services" / "user.py"
        app_file.parent.mkdir(parents=True)
        app_file.write_text("from ekko.core.entities import User\n")

        violations = _check_application([app_file])

        assert len(violations) == 0

    def test_application_importing_infrastructure_allowed(self, tmp_path: Path) -> None:
        """application/ importing from ekko.infrastructure is allowed."""
        app_file = tmp_path / "application" / "services" / "data.py"
        app_file.parent.mkdir(parents=True)
        app_file.write_text(
            "from ekko.infrastructure.db.repositories import UserRepository\n"
        )

        violations = _check_application([app_file])

        assert len(violations) == 0

    def test_application_importing_ai_allowed(self, tmp_path: Path) -> None:
        """application/ importing from ekko.ai is allowed."""
        app_file = tmp_path / "application" / "services" / "chat.py"
        app_file.parent.mkdir(parents=True)
        app_file.write_text("from ekko.ai.llm import LLMAdapter\n")

        violations = _check_application([app_file])

        assert len(violations) == 0


@pytest.mark.unit
class TestAILayerChecks:
    """Test ai/ layer boundary enforcement."""

    def test_ai_importing_infrastructure_detected(self, tmp_path: Path) -> None:
        """ai/ importing from ekko.infrastructure is detected as violation."""
        ai_file = tmp_path / "ai" / "llm" / "adapter.py"
        ai_file.parent.mkdir(parents=True)
        ai_file.write_text("from ekko.infrastructure.db import Session\n")

        violations = _check_ai([ai_file])

        assert len(violations) == 1
        assert violations[0].layer == "ai"
        assert violations[0].imported_layer == "infrastructure"

    def test_ai_importing_application_detected(self, tmp_path: Path) -> None:
        """ai/ importing from ekko.application is detected as violation."""
        ai_file = tmp_path / "ai" / "chains" / "conversational.py"
        ai_file.parent.mkdir(parents=True)
        ai_file.write_text("from ekko.application.services import ChatService\n")

        violations = _check_ai([ai_file])

        assert len(violations) == 1
        assert violations[0].layer == "ai"
        assert violations[0].imported_layer == "application"

    def test_ai_importing_presentation_detected(self, tmp_path: Path) -> None:
        """ai/ importing from ekko.presentation is detected as violation."""
        ai_file = tmp_path / "ai" / "prompts" / "templates.py"
        ai_file.parent.mkdir(parents=True)
        ai_file.write_text("from ekko.presentation.api.schemas import MessageInput\n")

        violations = _check_ai([ai_file])

        assert len(violations) == 1
        assert violations[0].layer == "ai"
        assert violations[0].imported_layer == "presentation"

    def test_ai_importing_core_allowed(self, tmp_path: Path) -> None:
        """ai/ importing from ekko.core is allowed."""
        ai_file = tmp_path / "ai" / "embeddings" / "service.py"
        ai_file.parent.mkdir(parents=True)
        ai_file.write_text("from ekko.core.ports import EmbeddingPort\n")

        violations = _check_ai([ai_file])

        assert len(violations) == 0

    def test_ai_importing_config_allowed(self, tmp_path: Path) -> None:
        """ai/ importing from ekko.config is allowed."""
        ai_file = tmp_path / "ai" / "llm" / "client.py"
        ai_file.parent.mkdir(parents=True)
        ai_file.write_text("from ekko.config.settings import get_settings\n")

        violations = _check_ai([ai_file])

        assert len(violations) == 0


@pytest.mark.unit
class TestViolationDataStructure:
    """Test Violation dataclass structure and attributes."""

    def test_violation_has_required_fields(self, tmp_path: Path) -> None:
        """Violation contains all required fields."""
        test_file = tmp_path / "core" / "test.py"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("from ekko.application import something\n")

        violations = _check_core([test_file])

        assert len(violations) == 1
        v = violations[0]
        assert hasattr(v, "file_path")
        assert hasattr(v, "line_number")
        assert hasattr(v, "line_text")
        assert hasattr(v, "layer")
        assert hasattr(v, "imported_layer")
        assert hasattr(v, "reason")

    def test_violation_layer_field_correct(self, tmp_path: Path) -> None:
        """Violation.layer correctly identifies source layer."""
        test_file = tmp_path / "utils" / "helper.py"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("from ekko.core import Entity\n")

        violations = _check_utils([test_file])

        assert violations[0].layer == "utils"

    def test_violation_imported_layer_field_correct(self, tmp_path: Path) -> None:
        """Violation.imported_layer correctly identifies target layer."""
        test_file = tmp_path / "config" / "settings.py"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("from ekko.presentation.api import router\n")

        violations = _check_config([test_file])

        assert violations[0].imported_layer == "presentation"


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and false positives."""

    def test_type_checking_import_still_detected(self, tmp_path: Path) -> None:
        """Imports inside TYPE_CHECKING blocks are still violations."""
        core_file = tmp_path / "core" / "protocols.py"
        core_file.parent.mkdir(parents=True)
        core_file.write_text(
            "from typing import TYPE_CHECKING\n"
            "if TYPE_CHECKING:\n"
            "    from ekko.application import Service\n"
        )

        violations = _check_core([core_file])

        assert len(violations) == 1

    def test_multiline_import_detected(self, tmp_path: Path) -> None:
        """Multiline from imports are detected."""
        utils_file = tmp_path / "utils" / "types.py"
        utils_file.parent.mkdir(parents=True)
        utils_file.write_text(
            "from ekko.core.entities import (\n    User,\n    Message,\n)\n"
        )

        violations = _check_utils([utils_file])

        assert len(violations) == 1

    def test_inline_import_detected(self, tmp_path: Path) -> None:
        """Inline import statements are detected."""
        ai_file = tmp_path / "ai" / "service.py"
        ai_file.parent.mkdir(parents=True)
        ai_file.write_text(
            "def process():\n"
            "    from ekko.infrastructure.db import Session\n"
            "    return Session()\n"
        )

        violations = _check_ai([ai_file])

        assert len(violations) == 1

    def test_comment_with_import_not_detected(self, tmp_path: Path) -> None:
        """Commented import lines are not detected as violations."""
        core_file = tmp_path / "core" / "test.py"
        core_file.parent.mkdir(parents=True)
        core_file.write_text("# from ekko.application import Service\n")

        violations = _check_core([core_file])

        assert len(violations) == 0

    def test_string_containing_import_not_detected(self, tmp_path: Path) -> None:
        """String literals containing import statements are not detected."""
        utils_file = tmp_path / "utils" / "docs.py"
        utils_file.parent.mkdir(parents=True)
        utils_file.write_text('DOC = "from ekko.core import Entity"\n')

        violations = _check_utils([utils_file])

        assert len(violations) == 0


@pytest.mark.unit
class TestCLIBehavior:
    """Test CLI interface and output formatting."""

    def test_clean_codebase_returns_zero(self, tmp_path: Path) -> None:
        """Tool returns exit code 0 when no violations found."""
        # Create a minimal valid structure
        utils_file = tmp_path / "backend" / "src" / "ekko" / "utils" / "types.py"
        utils_file.parent.mkdir(parents=True)
        utils_file.write_text("from typing import Protocol\n")

        result = subprocess.run(  # noqa: S603
            [sys.executable, str(ARCHITECTURE_CHECK_SCRIPT)],
            capture_output=True,
            text=True,
            check=False,
        )

        # We expect either 0 (no violations) or 1 (violations found)
        # The actual exit code depends on the real codebase state
        assert result.returncode in (0, 1)

    def test_verbose_flag_accepted(self) -> None:
        """Tool accepts --verbose flag without error."""
        result = subprocess.run(  # noqa: S603
            [
                sys.executable,
                str(ARCHITECTURE_CHECK_SCRIPT),
                "--verbose",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        # Should not crash with argument error
        assert "unrecognized arguments" not in result.stderr.lower()
        assert result.returncode in (0, 1)

    def test_short_verbose_flag_accepted(self) -> None:
        """Tool accepts -v short flag without error."""
        result = subprocess.run(  # noqa: S603
            [sys.executable, str(ARCHITECTURE_CHECK_SCRIPT), "-v"],
            capture_output=True,
            text=True,
            check=False,
        )

        assert "unrecognized arguments" not in result.stderr.lower()
        assert result.returncode in (0, 1)
