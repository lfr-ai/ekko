"""CLI to migrate table data from PostgreSQL into SQLite for local development."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from dataclasses import asdict, dataclass
from typing import Final

from sqlalchemy import MetaData, Table, func, insert, select, text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from ekko.config.enums import DatabaseBackend
from ekko.config.settings import get_settings
from ekko.infrastructure.db import models as _  # noqa: F401
from ekko.infrastructure.db.base import Base

_DEFAULT_CHUNK_SIZE: Final[int] = 500


@dataclass(frozen=True, slots=True)
class TableMigrationResult:
    """Per-table migration counts for source and target validation."""

    table_name: str
    migrated_rows: int
    source_rows: int
    target_rows: int


@dataclass(frozen=True, slots=True)
class MigrationSummary:
    """Final migration output payload."""

    source_database_url: str
    target_database_url: str
    migrated_tables: list[TableMigrationResult]


async def _run_migration(
    *,
    source_database_url: str,
    target_database_url: str,
    tables: set[str] | None,
    chunk_size: int,
    truncate_target: bool,
) -> MigrationSummary:
    _validate_database_url(database_url=source_database_url, expected_backend=DatabaseBackend.POSTGRESQL)
    _validate_database_url(database_url=target_database_url, expected_backend=DatabaseBackend.SQLITE)

    source_engine = create_async_engine(source_database_url, future=True, echo=False)
    target_engine = create_async_engine(
        target_database_url,
        future=True,
        echo=False,
        connect_args={"check_same_thread": False},
    )

    try:
        target_tables = _select_tables(metadata=Base.metadata, table_names=tables)
        source_metadata = await _reflect_source_metadata(
            source_engine=source_engine,
            table_names={table.name for table in target_tables},
        )

        async with target_engine.begin() as connection:
            await connection.execute(text("PRAGMA foreign_keys = ON"))
            await connection.execute(text("PRAGMA journal_mode = WAL"))
            await connection.run_sync(
                lambda sync_connection: Base.metadata.create_all(bind=sync_connection, checkfirst=True),
            )

        migrated_table_results = []

        if truncate_target:
            await _truncate_tables(target_engine=target_engine, tables=target_tables)

        for target_table in target_tables:
            source_table = source_metadata.tables.get(target_table.name)

            migrated_rows = await _copy_table_rows(
                source_engine=source_engine,
                target_engine=target_engine,
                source_table=source_table,
                target_table=target_table,
                chunk_size=chunk_size,
            )
            source_rows = (
                await _count_rows(engine=source_engine, table=source_table)
                if source_table is not None
                else 0
            )
            target_rows = await _count_rows(engine=target_engine, table=target_table)
            migrated_table_results.append(
                TableMigrationResult(
                    table_name=target_table.name,
                    migrated_rows=migrated_rows,
                    source_rows=source_rows,
                    target_rows=target_rows,
                ),
            )

        return MigrationSummary(
            source_database_url=_redact_database_url(database_url=source_database_url),
            target_database_url=_redact_database_url(database_url=target_database_url),
            migrated_tables=migrated_table_results,
        )
    finally:
        await source_engine.dispose()
        await target_engine.dispose()


def _validate_database_url(*, database_url: str, expected_backend: DatabaseBackend) -> None:
    if expected_backend == DatabaseBackend.POSTGRESQL and not database_url.startswith("postgresql"):
        raise ValueError("Source database URL must use PostgreSQL (postgresql://...).")
    if expected_backend == DatabaseBackend.SQLITE and not database_url.startswith("sqlite"):
        raise ValueError("Target database URL must use SQLite (sqlite://...).")


def _redact_database_url(*, database_url: str) -> str:
    parsed: URL = make_url(database_url)
    return parsed.render_as_string(hide_password=True)


async def _reflect_source_metadata(*, source_engine: AsyncEngine, table_names: set[str]) -> MetaData:
    metadata = MetaData()
    async with source_engine.connect() as source_connection:
        await source_connection.run_sync(
            lambda sync_connection: metadata.reflect(
                bind=sync_connection,
                only=list(table_names),
            ),
        )
    return metadata


def _select_tables(*, metadata: MetaData, table_names: set[str] | None) -> list[Table]:
    if table_names is None:
        return list(metadata.sorted_tables)

    return [table for table in metadata.sorted_tables if table.name in table_names]


async def _truncate_tables(*, target_engine: AsyncEngine, tables: list[Table]) -> None:
    async with target_engine.begin() as target_connection:
        await target_connection.execute(text("PRAGMA foreign_keys = OFF"))
        for table in reversed(tables):
            await target_connection.execute(table.delete())
        await target_connection.execute(text("PRAGMA foreign_keys = ON"))


async def _copy_table_rows(
    *,
    source_engine: AsyncEngine,
    target_engine: AsyncEngine,
    source_table: Table | None,
    target_table: Table,
    chunk_size: int,
) -> int:
    if source_table is None:
        return 0

    shared_columns = [column.name for column in target_table.columns if column.name in source_table.c]
    if not shared_columns:
        return 0

    copied_rows = 0
    select_statement = select(*(source_table.c[column_name] for column_name in shared_columns))

    async with source_engine.connect() as source_connection:
        stream_result = (await source_connection.stream(select_statement)).mappings()

        async with target_engine.begin() as target_connection:
            async for row_partition in stream_result.partitions(chunk_size):
                payload = [dict(row) for row in row_partition]
                if payload:
                    await target_connection.execute(insert(target_table), payload)
                    copied_rows += len(payload)

    return copied_rows


async def _count_rows(*, engine: AsyncEngine, table: Table) -> int:
    async with engine.connect() as connection:
        query = select(func.count()).select_from(table)
        result = await connection.execute(query)
    return int(result.scalar_one())


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Migrate PostgreSQL data to SQLite")
    parser.add_argument(
        "--source-url",
        help="Optional PostgreSQL source URL override. Defaults to active settings URL.",
    )
    parser.add_argument(
        "--target-url",
        help="Optional SQLite target URL override. Defaults to active settings URL.",
    )
    parser.add_argument(
        "--tables",
        nargs="*",
        help="Optional subset of table names to migrate.",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=_DEFAULT_CHUNK_SIZE,
        help=f"Rows per insert batch (default: {_DEFAULT_CHUNK_SIZE}).",
    )
    parser.add_argument(
        "--append",
        action="store_true",
        help="Append rows to existing target data instead of truncating first.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    settings = get_settings()
    source_database_url = args.source_url or settings.postgresql_async_database_url
    target_database_url = args.target_url or f"sqlite+aiosqlite:///{settings.resolved_db_path}"

    summary = asyncio.run(
        _run_migration(
            source_database_url=source_database_url,
            target_database_url=target_database_url,
            tables=set(args.tables) if args.tables else None,
            chunk_size=args.chunk_size,
            truncate_target=not args.append,
        ),
    )

    json.dump(asdict(summary), sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
