"""Root GraphQL mutations."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Final, Protocol
from uuid import uuid4

import strawberry
from strawberry.types import Info

from ekko.config.settings import get_settings
from ekko.presentation.graphql.pii_policy import PIIPolicySettings, apply_pii_policy
from ekko.presentation.graphql.types import (
    AnonymizeTextInput,
    ConversationType,
    DomainErrorType,
    PIIResultType,
    SendMessageInput,
    StartConversationInput,
    StreamCommandInput,
    StreamStatusType,
)

_STREAM_ACTION_START: Final[str] = "start"
_STREAM_ACTION_PAUSE: Final[str] = "pause"
_ERROR_CODE_INVALID_STREAM_ACTION: Final[str] = "INVALID_STREAM_ACTION"
_ERROR_CODE_STREAM_UNAVAILABLE: Final[str] = "STREAM_CONTROLLER_UNAVAILABLE"


class _StreamControllerProtocol(Protocol):
    """Protocol for the stream controller shape used by GraphQL resolvers."""

    async def device_check(self) -> None:
        """Validate audio device state before starting stream."""

    async def send_command(self, command: str) -> None:
        """Send a stream control command to the controller."""


def _policy_settings() -> PIIPolicySettings:
    """Resolve PII policy settings from runtime config."""
    settings = get_settings()
    return PIIPolicySettings(profile=settings.pii_policy_profile)


def _to_domain_error_types(*, errors: tuple[object, ...], field: str | None = None) -> list[DomainErrorType]:
    """Map policy/domain errors into typed GraphQL error payloads."""
    payload: list[DomainErrorType] = []
    for error in errors:
        code = getattr(error, "code", "DOMAIN_ERROR")
        message = getattr(error, "message", "Domain validation failed.")
        payload.append(DomainErrorType(code=str(code), message=str(message), field=field))
    return payload


def _resolve_stream_controller(*, info: Info) -> _StreamControllerProtocol | None:
    """Resolve the stream controller from request/app state context."""
    context = info.context
    if context is None:
        return None

    request = context.get("request")
    if request is None:
        return None
    app = getattr(request, "app", None)
    if app is None:
        return None
    app_state = getattr(app, "state", None)
    if app_state is None:
        return None
    return getattr(app_state, "controller", None)


@strawberry.type
class Mutation:
    """Root mutation type."""

    @strawberry.mutation
    async def control_stream(self, info: Info, command: StreamCommandInput) -> StreamStatusType:
        """Start or pause the audio stream via the real app controller."""
        if command.action not in {_STREAM_ACTION_START, _STREAM_ACTION_PAUSE}:
            return StreamStatusType(
                active=False,
                message=f"Unknown action: {command.action}",
                errors=[
                    DomainErrorType(
                        code=_ERROR_CODE_INVALID_STREAM_ACTION,
                        message="Stream action must be either 'start' or 'pause'.",
                        field="action",
                    )
                ],
            )

        controller = _resolve_stream_controller(info=info)
        if controller is None:
            return StreamStatusType(
                active=False,
                message="Stream controller unavailable",
                errors=[
                    DomainErrorType(
                        code=_ERROR_CODE_STREAM_UNAVAILABLE,
                        message="Stream controller is unavailable in the current runtime context.",
                    )
                ],
            )

        if command.action == _STREAM_ACTION_START:
            await controller.device_check()
            await controller.send_command("start_stream")
        else:
            await controller.send_command("pause_stream")

        return StreamStatusType(
            active=command.action == _STREAM_ACTION_START,
            message=f"Stream {command.action}ed",
        )

    @strawberry.mutation
    async def start_conversation(self, input: StartConversationInput | None = None) -> ConversationType:  # noqa: A002
        """Start a new conversation session."""
        _ = input
        now = datetime.now(UTC)
        return ConversationType(
            id=str(uuid4()),
            started_at=now,
            is_active=True,
        )

    @strawberry.mutation
    async def end_conversation(self, conversation_id: str) -> ConversationType:
        """End an active conversation."""
        now = datetime.now(UTC)
        return ConversationType(
            id=conversation_id,
            started_at=now,  # placeholder
            ended_at=now,
            is_active=False,
        )

    @strawberry.mutation
    async def send_message(self, info: Info, input: SendMessageInput) -> str:  # noqa: A002
        """Send a message in a conversation."""
        context = info.context
        anonymizer = None if context is None else context.get("pii_anonymizer")
        redacted_content = input.content if anonymizer is None else anonymizer.anonymize(input.content).anonymized_text
        return f"Message received in conversation {input.conversation_id}: {redacted_content}"

    @strawberry.mutation
    async def anonymize_text(self, info: Info, input: AnonymizeTextInput) -> PIIResultType:  # noqa: A002
        """Anonymize PII in the given text."""
        context = info.context
        anonymizer = None if context is None else context.get("pii_anonymizer")
        outcome = apply_pii_policy(text=input.text, anonymizer=anonymizer, settings=_policy_settings())

        if outcome.errors:
            return PIIResultType(
                anonymized_text=input.text,
                pii_found=False,
                match_count=0,
                errors=_to_domain_error_types(errors=outcome.errors),
            )

        return PIIResultType(
            anonymized_text=outcome.anonymized_text,
            pii_found=outcome.pii_found,
            match_count=outcome.match_count,
        )
