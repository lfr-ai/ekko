"""Prompt registry, versioning, and provisioning utilities.

This module provides a file-backed prompt registry that snapshots prompt sources
into immutable versioned files. If a source prompt changes, a new version is
provisioned automatically (unless disabled in settings).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Final, Literal, TypedDict, cast

from ekko.ai.prompts.templates import CONVERSATIONAL_SYSTEM
from ekko.config.settings import BaseAppConfig, get_settings

REGISTRY_SCHEMA_VERSION: Final[int] = 1
VERSIONS_DIRECTORY_NAME: Final[str] = "versions"
REGISTRY_FILE_NAME: Final[str] = "registry.json"

PROMPT_KEY_SUMMARY_CHUNKS: Final[str] = "summary_chunks"
PROMPT_KEY_CONVERSATIONAL_SYSTEM: Final[str] = "conversational_system"


class PromptRegistryError(RuntimeError):
    """Raised when prompt registry operations fail."""


@dataclass(frozen=True, slots=True)
class PromptVersionInfo:
    """Metadata for a provisioned prompt version."""

    prompt_key: str
    version: str
    checksum: str
    source_name: str
    file_path: Path
    created_at: datetime
    is_new: bool


@dataclass(frozen=True, slots=True)
class PromptSource:
    """Prompt source descriptor."""

    key: str
    source_kind: Literal["file", "inline"]
    source_name: str
    inline_text: str | None = None


class VersionRecord(TypedDict):
    """Serialized prompt version record."""

    version: str
    file_name: str
    source_name: str
    checksum: str
    created_at: str


class PromptEntry(TypedDict):
    """Serialized prompt entry in registry."""

    current_version: str
    versions: list[VersionRecord]


class PromptRegistryDocument(TypedDict):
    """Serialized prompt registry document."""

    schema_version: int
    prompts: dict[str, PromptEntry]


PROMPT_SOURCES: Final[dict[str, PromptSource]] = {
    PROMPT_KEY_SUMMARY_CHUNKS: PromptSource(
        key=PROMPT_KEY_SUMMARY_CHUNKS,
        source_kind="file",
        source_name="summary_prompt_chunks.txt",
    ),
    PROMPT_KEY_CONVERSATIONAL_SYSTEM: PromptSource(
        key=PROMPT_KEY_CONVERSATIONAL_SYSTEM,
        source_kind="inline",
        source_name="templates.CONVERSATIONAL_SYSTEM",
        inline_text=CONVERSATIONAL_SYSTEM,
    ),
}


def get_prompt_text(
    prompt_key: str,
    *,
    settings: BaseAppConfig | None = None,
) -> str:
    """Return prompt text for the requested prompt key.

    If prompt auto-provisioning is enabled, source changes are snapshotted into
    a new immutable version file automatically.
    """
    config = settings or get_settings()
    source = PROMPT_SOURCES.get(prompt_key)
    if source is None:
        raise PromptRegistryError(f"Unknown prompt key: {prompt_key}")

    active_version = _normalize_prompt_version(config.prompt_version)
    if not config.prompt_auto_provision and active_version is None:
        return _resolve_source_text(source=source, prompt_dir=Path(config.prompt_dir_path))

    info = provision_prompt(prompt_key=prompt_key, settings=config)
    if active_version is None:
        return _read_text(info.file_path)

    version_info = _get_prompt_version(prompt_key=prompt_key, version=active_version, settings=config)
    if version_info is None:
        raise PromptRegistryError(
            f"Prompt version '{active_version}' not found for key '{prompt_key}'.",
        )
    return _read_text(version_info.file_path)


def provision_all_prompts(*, settings: BaseAppConfig | None = None) -> list[PromptVersionInfo]:
    """Provision all known prompts and return their active version metadata."""
    config = settings or get_settings()
    return [
        provision_prompt(prompt_key=prompt_key, settings=config)
        for prompt_key in PROMPT_SOURCES
    ]


def get_prompt_versions(
    prompt_key: str,
    *,
    settings: BaseAppConfig | None = None,
) -> list[PromptVersionInfo]:
    """List all provisioned versions for a prompt key."""
    config = settings or get_settings()
    if prompt_key not in PROMPT_SOURCES:
        raise PromptRegistryError(f"Unknown prompt key: {prompt_key}")

    prompt_dir = Path(config.prompt_dir_path)
    document = _load_registry_document(prompt_dir=prompt_dir)
    entry = document["prompts"].get(prompt_key)
    if entry is None:
        return []

    versions_directory = _versions_directory(prompt_dir=prompt_dir)
    return [
        PromptVersionInfo(
            prompt_key=prompt_key,
            version=record["version"],
            checksum=record["checksum"],
            source_name=record["source_name"],
            file_path=versions_directory / record["file_name"],
            created_at=datetime.fromisoformat(record["created_at"]),
            is_new=False,
        )
        for record in entry["versions"]
    ]


def provision_prompt(
    *,
    prompt_key: str,
    settings: BaseAppConfig | None = None,
) -> PromptVersionInfo:
    """Provision one prompt and return active version metadata."""
    config = settings or get_settings()
    source = PROMPT_SOURCES.get(prompt_key)
    if source is None:
        raise PromptRegistryError(f"Unknown prompt key: {prompt_key}")

    prompt_dir = Path(config.prompt_dir_path)
    source_text = _resolve_source_text(source=source, prompt_dir=prompt_dir)

    if not config.prompt_auto_provision:
        return _provision_disabled_info(
            prompt_key=prompt_key,
            source=source,
            source_text=source_text,
            prompt_dir=prompt_dir,
        )

    versions_directory = _versions_directory(prompt_dir=prompt_dir)
    registry_path = versions_directory / REGISTRY_FILE_NAME
    document = _load_registry_document(prompt_dir=prompt_dir)

    checksum = _calculate_checksum(source_text)
    prompt_entry = document["prompts"].get(prompt_key)
    if prompt_entry is not None:
        current_record = _find_version(prompt_entry=prompt_entry, version=prompt_entry["current_version"])
        if current_record is not None and current_record["checksum"] == checksum:
            return _record_to_info(
                prompt_key=prompt_key,
                record=current_record,
                versions_directory=versions_directory,
                is_new=False,
            )

    version_value = _next_version(prompt_entry=prompt_entry)
    file_name = f"{prompt_key}.{version_value}.txt"
    file_path = versions_directory / file_name
    _write_text(file_path=file_path, content=source_text)

    created_at = datetime.now(tz=UTC)
    record: VersionRecord = {
        "version": version_value,
        "file_name": file_name,
        "source_name": source.source_name,
        "checksum": checksum,
        "created_at": created_at.isoformat(),
    }

    if prompt_entry is None:
        new_entry: PromptEntry = {
            "current_version": version_value,
            "versions": [record],
        }
        document["prompts"][prompt_key] = new_entry
        prompt_entry = new_entry
    else:
        prompt_entry["versions"].append(record)
        prompt_entry["current_version"] = version_value

    _write_registry_document(registry_path=registry_path, document=document)
    return _record_to_info(
        prompt_key=prompt_key,
        record=record,
        versions_directory=versions_directory,
        is_new=True,
    )


def _get_prompt_version(
    *,
    prompt_key: str,
    version: str,
    settings: BaseAppConfig,
) -> PromptVersionInfo | None:
    prompt_dir = Path(settings.prompt_dir_path)
    document = _load_registry_document(prompt_dir=prompt_dir)
    entry = document["prompts"].get(prompt_key)
    if entry is None:
        return None

    version_record = _find_version(prompt_entry=entry, version=version)
    if version_record is None:
        return None

    return _record_to_info(
        prompt_key=prompt_key,
        record=version_record,
        versions_directory=_versions_directory(prompt_dir=prompt_dir),
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
    pseudo_file = _versions_directory(prompt_dir=prompt_dir) / f"{prompt_key}.{pseudo_version}.txt"
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
            raise PromptRegistryError(f"Inline prompt source missing text: {source.key}")
        return source.inline_text
    source_path = prompt_dir / source.source_name
    return _read_text(source_path)


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as error:
        raise PromptRegistryError(f"Unable to read prompt file '{path}'.") from error


def _write_text(*, file_path: Path, content: str) -> None:
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
    except OSError as error:
        raise PromptRegistryError(f"Unable to write prompt version file '{file_path}'.") from error


def _calculate_checksum(content: str) -> str:
    return sha256(content.encode("utf-8")).hexdigest()


def _versions_directory(*, prompt_dir: Path) -> Path:
    return prompt_dir / VERSIONS_DIRECTORY_NAME


def _load_registry_document(*, prompt_dir: Path) -> PromptRegistryDocument:
    versions_directory = _versions_directory(prompt_dir=prompt_dir)
    registry_path = versions_directory / REGISTRY_FILE_NAME
    if not registry_path.exists():
        return {
            "schema_version": REGISTRY_SCHEMA_VERSION,
            "prompts": {},
        }

    try:
        raw = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise PromptRegistryError(f"Unable to load prompt registry file '{registry_path}'.") from error

    if not isinstance(raw, dict):
        raise PromptRegistryError("Prompt registry JSON must be an object.")

    schema_version = raw.get("schema_version")
    prompts = raw.get("prompts")
    if schema_version != REGISTRY_SCHEMA_VERSION or not isinstance(prompts, dict):
        raise PromptRegistryError("Prompt registry JSON has unsupported schema or invalid shape.")

    typed_prompts: dict[str, PromptEntry] = {}
    for key, entry in prompts.items():
        parsed_entry = _parse_prompt_entry(key=key, entry=entry)
        if parsed_entry is None:
            continue
        typed_prompts[key] = parsed_entry

    return {
        "schema_version": REGISTRY_SCHEMA_VERSION,
        "prompts": typed_prompts,
    }


def _parse_prompt_entry(*, key: object, entry: object) -> PromptEntry | None:
    if not isinstance(key, str) or not isinstance(entry, dict):
        return None

    entry_dict = cast(dict[str, object], entry)
    current_version = entry_dict.get("current_version")
    versions = entry_dict.get("versions")
    if not isinstance(current_version, str) or not isinstance(versions, list):
        return None

    typed_versions = [
        parsed
        for item in versions
        if (parsed := _parse_version_record(item=item)) is not None
    ]
    return {
        "current_version": current_version,
        "versions": typed_versions,
    }


def _parse_version_record(*, item: object) -> VersionRecord | None:
    if not isinstance(item, dict):
        return None

    item_dict = cast(dict[str, object], item)
    version = item_dict.get("version")
    file_name = item_dict.get("file_name")
    source_name = item_dict.get("source_name")
    checksum = item_dict.get("checksum")
    created_at = item_dict.get("created_at")
    if not (
        isinstance(version, str)
        and isinstance(file_name, str)
        and isinstance(source_name, str)
        and isinstance(checksum, str)
        and isinstance(created_at, str)
    ):
        return None
    return {
        "version": version,
        "file_name": file_name,
        "source_name": source_name,
        "checksum": checksum,
        "created_at": created_at,
    }


def _write_registry_document(*, registry_path: Path, document: PromptRegistryDocument) -> None:
    try:
        registry_path.parent.mkdir(parents=True, exist_ok=True)
        registry_path.write_text(
            json.dumps(document, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except OSError as error:
        raise PromptRegistryError(f"Unable to write prompt registry file '{registry_path}'.") from error


def _next_version(*, prompt_entry: PromptEntry | None) -> str:
    if prompt_entry is None or not prompt_entry["versions"]:
        return "v1"
    current = prompt_entry["current_version"]
    if not current.startswith("v"):
        return "v1"
    try:
        value = int(current[1:])
    except ValueError:
        return "v1"
    return f"v{value + 1}"


def _find_version(*, prompt_entry: PromptEntry, version: str) -> VersionRecord | None:
    for record in prompt_entry["versions"]:
        if record["version"] == version:
            return record
    return None


def _record_to_info(
    *,
    prompt_key: str,
    record: VersionRecord,
    versions_directory: Path,
    is_new: bool,
) -> PromptVersionInfo:
    return PromptVersionInfo(
        prompt_key=prompt_key,
        version=record["version"],
        checksum=record["checksum"],
        source_name=record["source_name"],
        file_path=versions_directory / record["file_name"],
        created_at=datetime.fromisoformat(record["created_at"]),
        is_new=is_new,
    )


def _normalize_prompt_version(version: str | None) -> str | None:
    if version is None:
        return None
    normalized = version.strip()
    return normalized or None
