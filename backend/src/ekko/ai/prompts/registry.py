"""Prompt registry, versioning, and provisioning utilities.

This module provides a file-backed prompt registry that snapshots prompt sources
into immutable versioned files. Named version sets are closed manifests selected
by application settings; the manifest never selects its own runtime environment.

When ``prompt_version_set`` is ``"experimental"``, the registry bypasses
versioning entirely and always reads directly from the template source files.
This allows rapid iteration during development without creating version
snapshots.
"""

from __future__ import annotations

import json
import os
from contextlib import contextmanager, suppress
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from time import monotonic, sleep, time_ns
from typing import TYPE_CHECKING, Final, Literal, Protocol, TypedDict

from ekko.config.runtime import get_config
from ekko.core.registry_constants import (
    PROMPT_KEY_CONVERSATIONAL_SYSTEM,
    PROMPT_KEY_SUMMARIZER_SYSTEM,
    PROMPT_KEY_SUMMARY_CHUNKS,
)

if TYPE_CHECKING:
    from collections.abc import Iterator

REGISTRY_SCHEMA_VERSION: Final[int] = 1
VERSIONS_DIRECTORY_NAME: Final[str] = "versions"
REGISTRY_DIRECTORY_NAME: Final[str] = "registry"
REGISTRY_FILE_NAME: Final[str] = "prompt_registry.json"
TEMPLATES_DIRECTORY_NAME: Final[str] = "templates"
REGISTRY_LOCK_FILE_NAME: Final[str] = ".registry.lock"
REGISTRY_LOCK_TIMEOUT_SECONDS: Final[float] = 5.0
REGISTRY_LOCK_POLL_INTERVAL_SECONDS: Final[float] = 0.05
ATOMIC_REPLACE_MAX_ATTEMPTS: Final[int] = 5
ATOMIC_REPLACE_BACKOFF_BASE_SECONDS: Final[float] = 0.01
ATOMIC_REPLACE_ATTEMPT_OFFSET: Final[int] = 1
EXPERIMENTAL_VERSION_SET: Final[str] = "experimental"
SUPPORTED_REGISTRY_FIELDS: Final[frozenset[str]] = frozenset(
    {"$schema", "description", "version_sets"},
)


class PromptRegistryError(RuntimeError):
    """Prompt registry operation failure."""


@dataclass(frozen=True, kw_only=True, slots=True)
class PromptVersionInfo:
    """Metadata for a provisioned prompt version."""

    prompt_key: str
    version: str
    checksum: str
    source_name: str
    file_path: Path
    created_at: datetime
    is_new: bool


@dataclass(frozen=True, kw_only=True, slots=True)
class PromptSource:
    """Prompt source descriptor."""

    key: str
    source_kind: Literal["file", "inline"]
    source_name: str
    inline_text: str | None = None


class PromptRegistryDocument(TypedDict):
    """Serialized prompt registry document."""

    version_sets: dict[str, dict[str, str]]


PROMPT_SOURCES: Final[dict[str, PromptSource]] = {
    PROMPT_KEY_SUMMARY_CHUNKS: PromptSource(
        key=PROMPT_KEY_SUMMARY_CHUNKS,
        source_kind="file",
        source_name="templates/summary_chunks.prompt.md",
    ),
    PROMPT_KEY_SUMMARIZER_SYSTEM: PromptSource(
        key=PROMPT_KEY_SUMMARIZER_SYSTEM,
        source_kind="file",
        source_name="templates/summarizer_system.prompt.md",
    ),
    PROMPT_KEY_CONVERSATIONAL_SYSTEM: PromptSource(
        key=PROMPT_KEY_CONVERSATIONAL_SYSTEM,
        source_kind="file",
        source_name="templates/conversational_system.prompt.md",
    ),
}


class _PromptRegistryConfig(Protocol):
    """Configuration fields required by the prompt registry."""

    prompt_dir_path: Path
    prompt_version: str | None
    prompt_version_set: str
    prompt_auto_provision: bool


def get_prompt_text(
    prompt_key: str,
    *,
    settings: _PromptRegistryConfig | None = None,
) -> str:
    """Resolve prompt text for the requested prompt key.

    If ``prompt_version_set`` is ``"experimental"``, the source template is
    returned directly — no versioning or provisioning occurs. Otherwise,
    an explicit version pin or named immutable version set is resolved.

    Args:
        prompt_key (str): Identifier for the prompt template.
        settings (_PromptRegistryConfig | None): Optional settings override.

    Returns:
        str: Resolved prompt template text.

    Raises:
        PromptRegistryError: If the key, version set, or prompt file cannot be resolved.
    """
    config = settings or get_config()
    source = PROMPT_SOURCES.get(prompt_key)
    if source is None:
        msg = f"Unknown prompt key: {prompt_key}"
        raise PromptRegistryError(msg)

    # Experimental mode: always read from template source, bypass versioning.
    if config.prompt_version_set == EXPERIMENTAL_VERSION_SET:
        return _resolve_source_text(source=source, prompt_dir=Path(config.prompt_dir_path))

    resolved_version = _resolve_version_from_settings(
        prompt_key=prompt_key,
        settings=config,
    )
    if resolved_version is None:
        msg = f"Configure a prompt version, a named version set, or the reserved '{EXPERIMENTAL_VERSION_SET}' set."
        raise PromptRegistryError(
            msg,
        )

    version_info = _get_prompt_version(prompt_key=prompt_key, version=resolved_version, settings=config)
    if version_info is None:
        msg = f"Prompt version '{resolved_version}' not found for key '{prompt_key}'."
        raise PromptRegistryError(
            msg,
        )
    return _read_text(version_info.file_path)


def get_prompt_versions(
    prompt_key: str,
    *,
    settings: _PromptRegistryConfig | None = None,
) -> list[PromptVersionInfo]:
    """List all provisioned versions for a prompt key."""
    config = settings or get_config()
    if prompt_key not in PROMPT_SOURCES:
        msg = f"Unknown prompt key: {prompt_key}"
        raise PromptRegistryError(msg)

    prompt_dir = Path(config.prompt_dir_path)
    prompt_versions_directory = _versions_directory(prompt_dir=prompt_dir) / prompt_key
    if not prompt_versions_directory.is_dir():
        return []

    versions = (
        path.name
        for path in prompt_versions_directory.iterdir()
        if path.is_dir() and _normalize_prompt_version(path.name) is not None
    )
    return [
        info
        for version in sorted(versions, key=_version_sort_key)
        if (info := _get_prompt_version(prompt_key=prompt_key, version=version, settings=config)) is not None
    ]


def get_prompt_version_info(
    prompt_key: str,
    version: str,
    *,
    settings: _PromptRegistryConfig | None = None,
) -> PromptVersionInfo | None:
    """Resolve metadata for a specific prompt key/version pair."""
    config = settings or get_config()
    if prompt_key not in PROMPT_SOURCES:
        msg = f"Unknown prompt key: {prompt_key}"
        raise PromptRegistryError(msg)

    normalized_version = _normalize_prompt_version(version)
    if normalized_version is None:
        return None

    return _get_prompt_version(
        prompt_key=prompt_key,
        version=normalized_version,
        settings=config,
    )


def get_active_prompt_version(
    prompt_key: str,
    *,
    settings: _PromptRegistryConfig | None = None,
) -> PromptVersionInfo:
    """Resolve active prompt metadata for a single prompt key."""
    config = settings or get_config()
    source = PROMPT_SOURCES.get(prompt_key)
    if source is None:
        msg = f"Unknown prompt key: {prompt_key}"
        raise PromptRegistryError(msg)

    # Experimental mode: return pseudo-info from source, no provisioning.
    if config.prompt_version_set == EXPERIMENTAL_VERSION_SET:
        prompt_dir = Path(config.prompt_dir_path)
        source_text = _resolve_source_text(source=source, prompt_dir=prompt_dir)
        return _provision_disabled_info(
            prompt_key=prompt_key,
            source=source,
            source_text=source_text,
            prompt_dir=prompt_dir,
        )

    resolved_version = _resolve_version_from_settings(
        prompt_key=prompt_key,
        settings=config,
    )
    if resolved_version is not None:
        selected_info = _get_prompt_version(
            prompt_key=prompt_key,
            version=resolved_version,
            settings=config,
        )
        if selected_info is None:
            msg = f"Prompt version '{resolved_version}' not found for key '{prompt_key}'."
            raise PromptRegistryError(
                msg,
            )
        return selected_info

    msg = f"Configure a prompt version, a named version set, or the reserved '{EXPERIMENTAL_VERSION_SET}' set."
    raise PromptRegistryError(
        msg,
    )


def get_active_prompt_versions(
    *,
    settings: _PromptRegistryConfig | None = None,
) -> dict[str, PromptVersionInfo]:
    """Collect active prompt metadata for all known prompt keys."""
    config = settings or get_config()
    return {
        prompt_key: get_active_prompt_version(prompt_key=prompt_key, settings=config) for prompt_key in PROMPT_SOURCES
    }


def _write_text_atomic(*, file_path: Path, content: str) -> None:
    temp_file_path = file_path.with_name(f"{file_path.name}.tmp-{os.getpid()}-{time_ns()}")
    temp_file_path.write_text(content, encoding="utf-8")
    for attempt in range(ATOMIC_REPLACE_MAX_ATTEMPTS):
        try:
            temp_file_path.replace(file_path)
        except PermissionError:
            if attempt == ATOMIC_REPLACE_MAX_ATTEMPTS - 1:
                break
            sleep(ATOMIC_REPLACE_BACKOFF_BASE_SECONDS * (attempt + ATOMIC_REPLACE_ATTEMPT_OFFSET))
        else:
            return

    # Windows fallback: if replace remains blocked by transient file locks,
    # write directly to target to preserve correctness.
    file_path.write_text(content, encoding="utf-8")
    with suppress(OSError):
        temp_file_path.unlink(missing_ok=True)


def _write_text(*, file_path: Path, content: str) -> None:
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        _write_text_atomic(file_path=file_path, content=content)
    except OSError as exc:
        msg = f"Unable to write prompt version file '{file_path}'."
        raise PromptRegistryError(msg) from exc


@contextmanager
def _prompt_registry_lock(*, prompt_dir: Path) -> Iterator[None]:
    lock_path = _versions_directory(prompt_dir=prompt_dir) / REGISTRY_LOCK_FILE_NAME
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    deadline = monotonic() + REGISTRY_LOCK_TIMEOUT_SECONDS
    lock_fd: int | None = None

    while lock_fd is None:
        try:
            lock_fd = os.open(
                str(lock_path),
                os.O_CREAT | os.O_EXCL | os.O_WRONLY,
            )
        except FileExistsError:
            if monotonic() >= deadline:
                msg = f"Timed out waiting for prompt registry lock '{lock_path}'."
                raise PromptRegistryError(msg) from None
            sleep(REGISTRY_LOCK_POLL_INTERVAL_SECONDS)
        except OSError as exc:
            msg = f"Unable to create prompt registry lock file '{lock_path}'."
            raise PromptRegistryError(msg) from exc

    try:
        os.write(lock_fd, f"pid={os.getpid()}".encode())
        yield
    finally:
        with suppress(OSError):
            os.close(lock_fd)
        with suppress(OSError):
            lock_path.unlink(missing_ok=True)


def _next_version(*, existing_versions: list[PromptVersionInfo]) -> str:
    if not existing_versions:
        return "v1.0"
    major, minor = _version_sort_key(existing_versions[-1].version)
    return f"v{major}.{minor + 1}"


def provision_prompt(
    *,
    prompt_key: str,
    settings: _PromptRegistryConfig | None = None,
) -> PromptVersionInfo:
    """Provision one prompt and return active version metadata."""
    config = settings or get_config()
    source = PROMPT_SOURCES.get(prompt_key)
    if source is None:
        msg = f"Unknown prompt key: {prompt_key}"
        raise PromptRegistryError(msg)

    prompt_dir = Path(config.prompt_dir_path)
    source_text = _resolve_source_text(source=source, prompt_dir=prompt_dir)

    if not config.prompt_auto_provision:
        return _provision_disabled_info(
            prompt_key=prompt_key,
            source=source,
            source_text=source_text,
            prompt_dir=prompt_dir,
        )

    with _prompt_registry_lock(prompt_dir=prompt_dir):
        checksum = _calculate_checksum(source_text)
        existing_versions = get_prompt_versions(prompt_key=prompt_key, settings=config)
        if existing_versions and existing_versions[-1].checksum == checksum:
            return existing_versions[-1]

        version_value = _next_version(existing_versions=existing_versions)
        file_path = _snapshot_path(
            prompt_dir=prompt_dir,
            prompt_key=prompt_key,
            version=version_value,
        )
        _write_text(file_path=file_path, content=source_text)
        return _snapshot_to_info(
            prompt_key=prompt_key,
            version=version_value,
            source=source,
            file_path=file_path,
            is_new=True,
        )


def provision_all_prompts(*, settings: _PromptRegistryConfig | None = None) -> list[PromptVersionInfo]:
    """Provision all known prompts and return their active version metadata."""
    config = settings or get_config()
    return [provision_prompt(prompt_key=prompt_key, settings=config) for prompt_key in PROMPT_SOURCES]


def _get_prompt_version(
    *,
    prompt_key: str,
    version: str,
    settings: _PromptRegistryConfig,
) -> PromptVersionInfo | None:
    normalized_version = _normalize_prompt_version(version)
    if normalized_version is None:
        return None

    source = PROMPT_SOURCES[prompt_key]
    file_path = _snapshot_path(
        prompt_dir=Path(settings.prompt_dir_path),
        prompt_key=prompt_key,
        version=normalized_version,
    )
    if not file_path.is_file():
        return None

    return _snapshot_to_info(
        prompt_key=prompt_key,
        version=normalized_version,
        source=source,
        file_path=file_path,
        is_new=False,
    )


def _provision_disabled_info(
    *,
    prompt_key: str,
    source: PromptSource,
    source_text: str,
    prompt_dir: Path,
) -> PromptVersionInfo:
    checksum = _calculate_checksum(source_text)
    pseudo_version: Final[str] = "source"
    pseudo_file = _versions_directory(prompt_dir=prompt_dir) / f"{prompt_key}/{pseudo_version}/{prompt_key}.prompt.md"
    return PromptVersionInfo(
        prompt_key=prompt_key,
        version=pseudo_version,
        checksum=checksum,
        source_name=source.source_name,
        file_path=pseudo_file,
        created_at=datetime.now(tz=UTC),
        is_new=False,
    )


def _resolve_source_text(*, source: PromptSource, prompt_dir: Path) -> str:
    if source.source_kind == "inline":
        if source.inline_text is None:
            msg = f"Inline prompt source missing text: {source.key}"
            raise PromptRegistryError(msg)
        return source.inline_text

    for candidate_path in _candidate_source_paths(source=source, prompt_dir=prompt_dir):
        if candidate_path.exists():
            return _read_text(candidate_path)

    source_path = prompt_dir / source.source_name
    msg = f"Unable to read prompt file '{source_path}'."
    raise PromptRegistryError(msg)


def _candidate_source_paths(*, source: PromptSource, prompt_dir: Path) -> tuple[Path, ...]:
    return (prompt_dir / source.source_name,)


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        msg = f"Unable to read prompt file '{path}'."
        raise PromptRegistryError(msg) from exc


def _calculate_checksum(content: str) -> str:
    return sha256(content.encode("utf-8")).hexdigest()


def _versions_directory(*, prompt_dir: Path) -> Path:
    return prompt_dir / VERSIONS_DIRECTORY_NAME


def _version_sort_key(version: str) -> tuple[int, int]:
    major_text, minor_text = version.removeprefix("v").split(".", maxsplit=1)
    return int(major_text), int(minor_text)


def _snapshot_path(*, prompt_dir: Path, prompt_key: str, version: str) -> Path:
    return _versions_directory(prompt_dir=prompt_dir) / prompt_key / version / f"{prompt_key}.prompt.md"


def _snapshot_to_info(
    *,
    prompt_key: str,
    version: str,
    source: PromptSource,
    file_path: Path,
    is_new: bool,
) -> PromptVersionInfo:
    content = _read_text(file_path)
    try:
        created_at = datetime.fromtimestamp(file_path.stat().st_mtime, tz=UTC)
    except OSError as exc:
        msg = f"Unable to inspect prompt version file '{file_path}'."
        raise PromptRegistryError(msg) from exc

    return PromptVersionInfo(
        prompt_key=prompt_key,
        version=version,
        checksum=_calculate_checksum(content),
        source_name=source.source_name,
        file_path=file_path,
        created_at=created_at,
        is_new=is_new,
    )


def _normalize_prompt_version(version: str | None) -> str | None:
    if version is None:
        return None
    normalized = version.strip()
    if not normalized.startswith("v") or normalized.count(".") != 1:
        return None
    major_text, minor_text = normalized[1:].split(".", maxsplit=1)
    if not major_text.isdigit() or not minor_text.isdigit():
        return None
    return normalized


def _normalize_version_set_name(version_set_name: str) -> str:
    return version_set_name.strip()


def _is_version_set_mode(version_set_name: str) -> bool:
    normalized = _normalize_version_set_name(version_set_name)
    return bool(normalized) and normalized != EXPERIMENTAL_VERSION_SET


def _parse_single_version_set(*, set_name: str, set_mapping: object) -> dict[str, str]:
    if not isinstance(set_mapping, dict):
        msg = f"Prompt version set '{set_name}' must be an object."
        raise PromptRegistryError(msg)

    prompts_obj = set_mapping.get("prompts") if "prompts" in set_mapping else set_mapping
    if not isinstance(prompts_obj, dict):
        msg = f"Prompt version set '{set_name}' must contain a prompts object."
        raise PromptRegistryError(msg)

    valid_mapping: dict[str, str] = {}
    for prompt_key, version in prompts_obj.items():
        normalized_version = _normalize_prompt_version(version if isinstance(version, str) else None)
        if not isinstance(prompt_key, str) or normalized_version is None:
            msg = f"Prompt version set '{set_name}' contains an invalid pin."
            raise PromptRegistryError(msg)
        valid_mapping[prompt_key] = normalized_version
    return valid_mapping


def _parse_version_sets(*, raw_version_sets: object) -> dict[str, dict[str, str]]:
    if not isinstance(raw_version_sets, dict):
        msg = "Prompt registry 'version_sets' must be an object."
        raise PromptRegistryError(msg)

    parsed_sets: dict[str, dict[str, str]] = {}
    for set_name, set_mapping in raw_version_sets.items():
        if not isinstance(set_name, str):
            msg = "Prompt version-set names must be strings."
            raise PromptRegistryError(msg)
        if set_name == EXPERIMENTAL_VERSION_SET:
            msg = f"The reserved '{EXPERIMENTAL_VERSION_SET}' set cannot appear in the manifest."
            raise PromptRegistryError(msg)
        parsed_sets[set_name] = _parse_single_version_set(set_name=set_name, set_mapping=set_mapping)
    return parsed_sets


def _load_registry_document_from_path(*, registry_path: Path) -> PromptRegistryDocument:
    try:
        raw = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        msg = f"Unable to load prompt registry file '{registry_path}'."
        raise PromptRegistryError(msg) from exc

    if not isinstance(raw, dict):
        msg = "Prompt registry JSON must be an object."
        raise PromptRegistryError(msg)

    unsupported_fields = set(raw) - SUPPORTED_REGISTRY_FIELDS
    if unsupported_fields:
        fields = ", ".join(sorted(str(field) for field in unsupported_fields))
        msg = f"Prompt registry contains unsupported fields: {fields}."
        raise PromptRegistryError(msg)

    version_sets_obj = raw.get("version_sets")
    parsed_sets = _parse_version_sets(raw_version_sets=version_sets_obj)
    return {"version_sets": parsed_sets}


def _registry_directory(*, prompt_dir: Path) -> Path:
    return prompt_dir / REGISTRY_DIRECTORY_NAME


def _registry_file_path(*, prompt_dir: Path) -> Path:
    return _registry_directory(prompt_dir=prompt_dir) / REGISTRY_FILE_NAME


def _load_registry_document(*, prompt_dir: Path) -> PromptRegistryDocument:
    registry_path = _registry_file_path(prompt_dir=prompt_dir)
    if not registry_path.exists():
        msg = f"Prompt registry file '{registry_path}' does not exist."
        raise PromptRegistryError(msg)

    return _load_registry_document_from_path(registry_path=registry_path)


def _get_version_set_entry(*, document: PromptRegistryDocument, version_set_name: str, prompt_key: str) -> str | None:
    normalized_set = _normalize_version_set_name(version_set_name)
    if not normalized_set or normalized_set == EXPERIMENTAL_VERSION_SET:
        return None

    version_set = document["version_sets"].get(normalized_set)
    if version_set is None:
        msg = f"Unknown prompt version set '{normalized_set}'."
        raise PromptRegistryError(msg)

    expected_prompt_keys = set(PROMPT_SOURCES)
    actual_prompt_keys = set(version_set)
    if actual_prompt_keys != expected_prompt_keys:
        expected = ", ".join(sorted(expected_prompt_keys))
        msg = f"Prompt version set '{normalized_set}' must contain exactly these prompts: {expected}."
        raise PromptRegistryError(msg)

    return _normalize_prompt_version(version_set.get(prompt_key))


def _resolve_version_from_settings(*, prompt_key: str, settings: _PromptRegistryConfig) -> str | None:
    explicit_version = _normalize_prompt_version(settings.prompt_version)
    if explicit_version is not None:
        return explicit_version

    if not _is_version_set_mode(settings.prompt_version_set):
        return None

    prompt_dir = Path(settings.prompt_dir_path)
    document = _load_registry_document(prompt_dir=prompt_dir)
    requested_version_set = _normalize_version_set_name(settings.prompt_version_set)
    return _get_version_set_entry(
        document=document,
        version_set_name=requested_version_set,
        prompt_key=prompt_key,
    )
