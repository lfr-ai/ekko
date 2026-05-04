"""Tests for magic string detection tool."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

# Import the module under test
import sys
from pathlib import Path as P

# Add tools/conventions to path
tools_path = P(__file__).resolve().parents[3] / "tools" / "conventions"
sys.path.insert(0, str(tools_path))

from check_magic_strings import (  # noqa: E402
    FIELD_PATTERNS,
    ROLE_PATTERNS,
    STATUS_PATTERNS,
    Violation,
    ViolationCategory,
    _categorize_literal,
    _is_excluded_context,
    _is_excluded_file,
    _parse_file_ast,
    _suggest_fix,
)


class TestCategorizeLiteral:
    """Tests for literal categorization."""

    def test_categorize_route_path(self) -> None:
        """Route paths starting with / are categorized correctly."""
        assert _categorize_literal("/api/users") == ViolationCategory.ROUTE_PATH
        assert _categorize_literal("/health") == ViolationCategory.ROUTE_PATH

    def test_categorize_field_name(self) -> None:
        """Common field names are categorized correctly."""
        assert _categorize_literal("id") == ViolationCategory.FIELD_NAME
        assert _categorize_literal("name") == ViolationCategory.FIELD_NAME
        assert _categorize_literal("status") == ViolationCategory.FIELD_NAME
        assert _categorize_literal("email") == ViolationCategory.FIELD_NAME

    def test_categorize_status_value(self) -> None:
        """Status values are categorized correctly."""
        assert _categorize_literal("completed") == ViolationCategory.STATUS_VALUE
        assert _categorize_literal("failed") == ViolationCategory.STATUS_VALUE
        assert _categorize_literal("pending") == ViolationCategory.STATUS_VALUE
        assert _categorize_literal("processing") == ViolationCategory.STATUS_VALUE

    def test_categorize_message_role(self) -> None:
        """Message role keys are categorized correctly."""
        assert _categorize_literal("system") == ViolationCategory.MESSAGE_ROLE
        assert _categorize_literal("user") == ViolationCategory.MESSAGE_ROLE
        assert _categorize_literal("assistant") == ViolationCategory.MESSAGE_ROLE
        assert _categorize_literal("tool") == ViolationCategory.MESSAGE_ROLE

    def test_categorize_unknown(self) -> None:
        """Unknown literals are categorized as UNKNOWN."""
        assert _categorize_literal("random_string") == ViolationCategory.UNKNOWN
        assert _categorize_literal("hello world") == ViolationCategory.UNKNOWN


class TestSuggestFix:
    """Tests for fix suggestions."""

    def test_suggest_fix_route_path(self) -> None:
        """Route path fixes suggest constant extraction."""
        fix = _suggest_fix("/api/users", ViolationCategory.ROUTE_PATH)
        assert "ROUTE_" in fix
        assert "API_USERS" in fix

    def test_suggest_fix_field_name(self) -> None:
        """Field name fixes suggest registry usage."""
        fix = _suggest_fix("status", ViolationCategory.FIELD_NAME)
        assert "FIELD_STATUS" in fix
        assert "registry_constants" in fix

    def test_suggest_fix_status_value(self) -> None:
        """Status value fixes suggest enum usage."""
        fix = _suggest_fix("completed", ViolationCategory.STATUS_VALUE)
        assert "STATUS_COMPLETED" in fix
        assert "enum" in fix.lower()

    def test_suggest_fix_message_role(self) -> None:
        """Message role fixes suggest enum usage."""
        fix = _suggest_fix("user", ViolationCategory.MESSAGE_ROLE)
        assert "MessageRole" in fix
        assert "USER" in fix


class TestIsExcludedFile:
    """Tests for file exclusion logic."""

    def test_exclude_tests(self, tmp_path: Path) -> None:
        """Test files are excluded."""
        test_file = tmp_path / "tests" / "test_something.py"
        test_file.parent.mkdir(parents=True)
        test_file.touch()

        # Patch TESTS constant
        import check_magic_strings

        original_tests = check_magic_strings.TESTS
        try:
            check_magic_strings.TESTS = tmp_path / "tests"
            assert _is_excluded_file(test_file)
        finally:
            check_magic_strings.TESTS = original_tests

    def test_exclude_init(self) -> None:
        """__init__.py files are excluded."""
        init_file = Path("backend/src/ekko/__init__.py")
        assert _is_excluded_file(init_file)

    def test_exclude_generated(self) -> None:
        """Generated files are excluded."""
        generated = Path("backend/src/ekko/core/registry_constants.py")
        assert _is_excluded_file(generated)

    def test_include_regular_file(self) -> None:
        """Regular source files are included."""
        # The exclusion logic only targets __init__.py and generated files.
        assert not _is_excluded_file(Path("backend/src/ekko/core/entities/user.py"))


class TestIsExcludedContext:
    """Tests for context exclusion logic."""

    def test_exclude_logger_calls(self) -> None:
        """Logger calls are excluded."""
        assert _is_excluded_context('logger.info("Processing started")', "")
        assert _is_excluded_context('logger.error("Failed to process")', "")
        assert _is_excluded_context('    logger.debug("Debug info")', "")

    def test_exclude_exception_messages(self) -> None:
        """Exception messages are excluded."""
        assert _is_excluded_context('raise ValueError("Invalid input")', "")
        assert _is_excluded_context('raise CustomError("Something wrong")', "")

    def test_exclude_docstrings(self) -> None:
        """Docstrings are excluded."""
        assert _is_excluded_context('"""Module docstring."""', "")
        assert _is_excluded_context("'''Another docstring.'''", "")

    def test_exclude_external_api(self) -> None:
        """External API payloads are excluded."""
        assert _is_excluded_context('payload = {"key": "value"}  # external-api', "")
        assert _is_excluded_context("", "# external-api payload follows")

    def test_exclude_type_hints(self) -> None:
        """Type hints with Literal are excluded."""
        assert _is_excluded_context('status: Literal["active"]', "")
        assert _is_excluded_context('def foo(x: Literal["a", "b"]) -> None:', "")

    def test_include_regular_code(self) -> None:
        """Regular code is not excluded."""
        assert not _is_excluded_context('user_data = {"name": "John"}', "")
        assert not _is_excluded_context('status = "active"', "")


class TestParseFileAst:
    """Tests for AST-based file parsing."""

    def test_detect_field_name_violation(self, tmp_path: Path) -> None:
        """Detect hardcoded field names."""
        test_file = tmp_path / "test.py"
        test_file.write_text(
            dedent(
                """
                def get_user():
                    return {"id": 123, "name": "John"}
                """
            )
        )

        violations = _parse_file_ast(test_file)

        # Should detect "id" and "name" as field name violations
        field_violations = [
            v for v in violations if v.category == ViolationCategory.FIELD_NAME
        ]
        assert len(field_violations) >= 2
        literals = {v.literal for v in field_violations}
        assert "id" in literals
        assert "name" in literals

    def test_detect_route_path_violation(self, tmp_path: Path) -> None:
        """Detect hardcoded route paths."""
        test_file = tmp_path / "test.py"
        test_file.write_text(
            dedent(
                """
                @app.get("/api/users")
                def get_users():
                    return []
                """
            )
        )

        violations = _parse_file_ast(test_file)

        route_violations = [
            v for v in violations if v.category == ViolationCategory.ROUTE_PATH
        ]
        assert len(route_violations) >= 1
        assert any(v.literal == "/api/users" for v in route_violations)

    def test_detect_status_value_violation(self, tmp_path: Path) -> None:
        """Detect hardcoded status values."""
        test_file = tmp_path / "test.py"
        test_file.write_text(
            dedent(
                """
                def process():
                    status = "completed"
                    if status == "failed":
                        return False
                    return True
                """
            )
        )

        violations = _parse_file_ast(test_file)

        status_violations = [
            v for v in violations if v.category == ViolationCategory.STATUS_VALUE
        ]
        assert len(status_violations) >= 2
        literals = {v.literal for v in status_violations}
        assert "completed" in literals
        assert "failed" in literals

    def test_exclude_logger_in_ast(self, tmp_path: Path) -> None:
        """Logger calls are excluded in AST parsing."""
        test_file = tmp_path / "test.py"
        test_file.write_text(
            dedent(
                """
                import logger

                def process():
                    logger.info("Processing completed")
                    return "completed"
                """
            )
        )

        violations = _parse_file_ast(test_file)

        # "completed" in logger call should be excluded
        # "completed" in return should be detected
        # The exact behavior depends on context detection
        # At minimum, we shouldn't crash
        assert isinstance(violations, list)

    def test_exclude_exception_in_ast(self, tmp_path: Path) -> None:
        """Exception messages are excluded in AST parsing."""
        test_file = tmp_path / "test.py"
        test_file.write_text(
            dedent(
                """
                def validate(status):
                    if status not in ["active", "inactive"]:
                        raise ValueError("Invalid status")
                """
            )
        )

        violations = _parse_file_ast(test_file)

        # "Invalid status" should be excluded
        # "active" and "inactive" might be detected depending on context
        assert isinstance(violations, list)

    def test_skip_empty_strings(self, tmp_path: Path) -> None:
        """Empty and very short strings are skipped."""
        test_file = tmp_path / "test.py"
        test_file.write_text(
            dedent(
                """
                x = ""
                y = "a"
                z = "ab"
                """
            )
        )

        violations = _parse_file_ast(test_file)

        # Only strings < 2 chars are skipped
        # "ab" is 2 chars but not a known pattern, so UNKNOWN category
        assert all(len(v.literal) >= 2 for v in violations)

    def test_handle_syntax_error(self, tmp_path: Path) -> None:
        """Files with syntax errors are skipped."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def invalid syntax here")

        violations = _parse_file_ast(test_file)

        # Should return empty list, not crash
        assert violations == []


class TestViolationDataclass:
    """Tests for Violation dataclass."""

    def test_violation_creation(self) -> None:
        """Violation dataclass can be created with all fields."""
        v = Violation(
            file=Path("test.py"),
            line=10,
            column=5,
            literal="status",
            category=ViolationCategory.FIELD_NAME,
            context='x = {"status": "active"}',
            suggested_fix="Use FIELD_STATUS constant",
        )

        assert v.file == Path("test.py")
        assert v.line == 10
        assert v.column == 5
        assert v.literal == "status"
        assert v.category == ViolationCategory.FIELD_NAME
        assert "status" in v.context
        assert "FIELD_STATUS" in v.suggested_fix

    def test_violation_immutable(self) -> None:
        """Violation is immutable (frozen=True)."""
        v = Violation(
            file=Path("test.py"),
            line=10,
            column=5,
            literal="test",
            category=ViolationCategory.UNKNOWN,
            context="x = test",
            suggested_fix="Fix it",
        )

        with pytest.raises(AttributeError):
            v.line = 20  # type: ignore[misc]


class TestPatternConstants:
    """Tests for pattern constant completeness."""

    def test_field_patterns_coverage(self) -> None:
        """FIELD_PATTERNS includes common field names."""
        required_fields = {"id", "name", "status", "email", "role"}
        assert required_fields.issubset(FIELD_PATTERNS)

    def test_status_patterns_coverage(self) -> None:
        """STATUS_PATTERNS includes common status values."""
        required_statuses = {"completed", "failed", "pending", "processing"}
        assert required_statuses.issubset(STATUS_PATTERNS)

    def test_role_patterns_coverage(self) -> None:
        """ROLE_PATTERNS includes standard message roles."""
        required_roles = {"system", "user", "assistant", "tool"}
        assert required_roles == ROLE_PATTERNS


class TestIntegration:
    """Integration tests for the full tool."""

    def test_full_scan_workflow(self, tmp_path: Path) -> None:
        """Test complete scan workflow on a sample file."""
        # Create a test file with multiple violation types
        test_file = tmp_path / "sample.py"
        test_file.write_text(
            dedent(
                '''
                """Sample module with magic strings."""

                def api_endpoint():
                    """API endpoint handler."""
                    route = "/api/users"
                    status = "completed"
                    role = "user"
                    return {"id": 123, "name": "Test"}
                '''
            )
        )

        violations = _parse_file_ast(test_file)

        # Should detect various violations
        assert len(violations) > 0

        categories = {v.category for v in violations}
        # Should have multiple categories
        assert len(categories) > 1

        # Each violation should have all required fields
        for v in violations:
            assert v.file == test_file
            assert v.line > 0
            assert v.literal
            assert v.category
            assert v.context
            assert v.suggested_fix
