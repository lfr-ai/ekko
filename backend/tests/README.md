# Testing Infrastructure

This directory contains the test suite for the Ekko backend.

## Directory Structure

```text
tests/
├── conftest.py           # Root test configuration and shared fixtures
├── factories/            # Factory-boy factories for test data generation
├── fixtures/             # Pre-built domain entity instances
├── mocks/                # Reusable mock objects
├── utils/                # Test utilities and assertion helpers
├── unit/                 # Fast, isolated unit tests
├── integration/          # Database, API, external service integration tests
├── property/             # Property-based tests (Hypothesis)
├── performance/          # Benchmark and timing tests
├── e2e/                  # End-to-end tests
└── database/             # Migration and ORM model tests
```

## Test Markers

Use pytest markers to categorize tests:

- `@pytest.mark.unit` - Fast, isolated, no I/O (default)
- `@pytest.mark.integration` - Database, API, external services
- `@pytest.mark.property` - Property-based tests with Hypothesis
- `@pytest.mark.performance` - Benchmark and timing tests
- `@pytest.mark.slow` - Tests that take >1 second
- `@pytest.mark.e2e` - End-to-end system tests

## Factory Usage

The `tests/factories/` directory contains Factory-boy factories for generating test data with sensible defaults and controlled variation.

### Available Factories

- `ConversationFactory` - Generate conversation entities
- `MessageFactory` - Generate message entities
- `TranscriptFactory` - Generate transcript entities
- `AgentResultFactory` - Generate agent result entities

### Basic Usage

```python
from tests.factories import ConversationFactory, MessageFactory

def test_conversation_creation(conversation_factory):
    """Test creating a conversation with factory."""
    conversation = conversation_factory.create()
    assert conversation.is_active()

def test_multiple_messages(message_factory):
    """Test creating multiple messages."""
    messages = message_factory.create_batch(3, role=MessageRole.USER)
    assert len(messages) == 3
    assert all(msg.role == MessageRole.USER for msg in messages)
```

### Factory Traits and Helpers

Factories provide trait methods for common scenarios:

```python
from tests.factories import ConversationFactory, MessageFactory, TranscriptFactory

# Ended conversation
ended_conv = ConversationFactory.ended(summary="Project discussion")

# Role-specific messages
user_msg = MessageFactory.user_message(content="Hello")
assistant_msg = MessageFactory.assistant_message(content="Hi there")
system_msg = MessageFactory.system_message(content="Instructions")

# Transcript with specific status
completed = TranscriptFactory.completed(text="Final transcript")
failed = TranscriptFactory.failed()
low_conf = TranscriptFactory.low_confidence(confidence=0.3)

# Agent results with execution times
fast = AgentResultFactory.fast_execution(execution_time_seconds=0.5)
slow = AgentResultFactory.slow_execution(execution_time_seconds=15.0)
```

### Override Defaults

All factory attributes can be overridden:

```python
from tests.factories import ConversationFactory
import uuid

conversation = ConversationFactory.create(
    id=uuid.UUID("12345678-1234-5678-1234-567812345678"),
    summary="Custom summary"
)
```

### Using Fixtures

Factories are exposed as pytest fixtures in `conftest.py`:

```python
def test_with_factory_fixture(conversation_factory, message_factory):
    """Test using factory fixtures."""
    conv = conversation_factory.create()
    msg = message_factory.create(conversation_id=conv.id)
    assert msg.conversation_id == conv.id
```

## Static Fixtures

The `tests/fixtures/` directory contains pre-built domain entity instances for consistent testing across the suite.

### Available Fixtures

```python
from tests.fixtures import (
    ACTIVE_CONVERSATION,
    COMPLETED_CONVERSATION,
    SAMPLE_CONVERSATION_ID,
    SAMPLE_MESSAGES,
    TRANSCRIPT_RECEIVED,
    TRANSCRIPT_COMPLETED,
    TRANSCRIPT_LOW_CONFIDENCE,
    TRANSCRIPT_FAILED,
    ALL_TRANSCRIPT_FIXTURES,
)

def test_with_static_fixture():
    """Test using pre-built fixture data."""
    assert ACTIVE_CONVERSATION.is_active()
    assert not COMPLETED_CONVERSATION.is_active()
    assert len(SAMPLE_MESSAGES) == 4
```

## Running Tests

```bash
# All tests
task test

# Unit tests only (fast)
task test:unit

# Integration tests
task test:integration

# Property-based tests
task test:property

# Performance tests
task test:performance

# E2E tests
task test:e2e

# With coverage
task test:coverage

# Specific test file
uv run python -m pytest tests/unit/test_entities.py

# Specific test
uv run python -m pytest tests/unit/test_entities.py::test_conversation_is_active

# With verbose output
uv run python -m pytest -v tests/

# Show print statements
uv run python -m pytest -s tests/
```

## Coverage Requirements

- Core layer (`backend/src/ekko/core/`): >= 80%
- Application layer (`backend/src/ekko/application/`): >= 80%
- Other layers: Best effort

## Writing Good Tests

1. **Use factories for test data** - Prefer factories over manual entity construction
2. **Keep tests focused** - One assertion theme per test
3. **Use descriptive names** - `test_conversation_is_active_when_not_ended`
4. **Test edge cases** - Empty inputs, boundary values, error conditions
5. **Avoid test interdependencies** - Each test should be isolated
6. **Mock external dependencies** - Database, API calls, file I/O
7. **Use appropriate markers** - Tag tests correctly for selective runs
8. **Follow AAA pattern** - Arrange, Act, Assert

## Example Test

```python
import pytest
from tests.factories import ConversationFactory, MessageFactory
from ekko.core.enums import MessageRole


@pytest.mark.unit
def test_conversation_is_active_when_not_ended(conversation_factory):
    """Conversation is active when ended_at is None."""
    # Arrange
    conversation = conversation_factory.create(ended_at=None)

    # Act
    result = conversation.is_active()

    # Assert
    assert result is True


@pytest.mark.unit
def test_message_factory_creates_user_message(message_factory):
    """MessageFactory.user_message creates message with USER role."""
    # Arrange & Act
    message = message_factory.user_message(content="Hello")

    # Assert
    assert message.role == MessageRole.USER
    assert message.content == "Hello"
```
