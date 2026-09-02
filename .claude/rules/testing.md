---
paths:
  - "**/tests/**/*.py"
  - "**/test_*.py"
  - "**/conftest.py"
---

# Testing Conventions

## Test Organization

```text
tests/
├── unit/                    # Fast, isolated, no I/O
│   ├── core/               # Domain logic tests
│   ├── application/        # Service tests with mocks
│   └── ...
├── integration/            # Tests with real dependencies
│   ├── persistence/        # Repository tests with DB
│   ├── api/               # FastAPI endpoint tests
│   └── ...
├── property/              # Property-based tests (Hypothesis)
├── fixtures/              # Shared test data
└── conftest.py           # Shared fixtures
```

## Test Markers

Use pytest markers for test categorization:

```python
import pytest

@pytest.mark.unit
def test_pure_function():
    """Fast unit test with no I/O."""
    pass

@pytest.mark.integration
def test_with_database():
    """Integration test requiring real database."""
    pass

@pytest.mark.property
def test_invariant_holds():
    """Property-based test with Hypothesis."""
    pass

@pytest.mark.slow
def test_performance_benchmark():
    """Slow test (>1s), run separately."""
    pass
```

Run specific markers:
```bash
# Run only unit tests (fast)
uv run pytest -m unit

# Run all except slow tests
uv run pytest -m "not slow"

# Run integration tests
uv run pytest -m integration
```

## Test Structure (AAA Pattern)

```python
def test_feature_behavior():
    """Test docstring explaining WHAT is tested and WHY."""
    # Arrange: Set up test data and dependencies
    entity = EntityFactory.build(status=StatusCode.NEW)
    mock_repo = MagicMock()
    service = EntityService(repo=mock_repo)

    # Act: Execute the behavior under test
    result = service.process(entity)

    # Assert: Verify the expected outcome
    assert result.status == StatusCode.PROCESSED
    assert result.processed_at is not None
    mock_repo.save.assert_called_once_with(entity)
```

## Test Naming

Pattern: `test_<unit>_<scenario>_<expected_outcome>`

```python
# Good: Descriptive test names
def test_entity_service_process_new_entity_updates_status():
    """EntityService.process() updates status to PROCESSED for new entities."""
    pass

def test_identifier_validator_invalid_checksum_raises_validation_error():
    """Identifier validator raises ValidationError when checksum is invalid."""
    pass

def test_entity_repository_get_nonexistent_id_returns_none():
    """EntityRepository.get() returns None when entity does not exist."""
    pass

# Bad: Vague names
def test_entity():
    pass

def test_validation():
    pass
```

## Factory-Based Test Data

Use factory-boy for consistent, reusable test data:

```python
import factory
from factory import Faker, SubFactory

class CustomerFactory(factory.Factory):
    class Meta:
        model = Customer

    customer_id = Faker('uuid4')
    name = Faker('name')
    identifier = Faker('numerify', text='##########')
    email = Faker('email')

class EntityFactory(factory.Factory):
    class Meta:
        model = Entity

    entity_id = Faker('uuid4')
    customer = SubFactory(CustomerFactory)
    status = StatusCode.NEW
    created_at = Faker('date_time')
```

Benefits:
- Consistent test data across tests
- Easy to customize per test: `EntityFactory.build(status=StatusCode.COMPLETED)`
- Reduces test brittleness
- Clear relationships via `SubFactory`

## Async Testing

```python
import httpx
import pytest

@pytest.mark.asyncio
async def test_async_case_service():
    """Test async service method."""
    service = ApplicationService(repo=mock_repo)
    result = await service.create(request)
    assert result is not None

@pytest.mark.asyncio
async def test_api_endpoint(async_client: httpx.AsyncClient):
    """Test FastAPI endpoint."""
    response = await async_client.get("/api/items/123")
    assert response.status_code == 200
    assert response.json()["item_id"] == "123"
```

## Mocking

```python
from unittest.mock import AsyncMock, MagicMock, patch

@pytest.fixture
def mock_entity_repository():
    """Mock entity repository with async methods."""
    repo = MagicMock()
    repo.get = AsyncMock(return_value=test_entity)
    repo.save = AsyncMock()
    repo.list = AsyncMock(return_value=[test_entity])
    return repo

def test_service_with_mock(mock_entity_repository):
    """Service uses mocked repository."""
    service = EntityService(repo=mock_entity_repository)
    result = service.get("123")
    mock_entity_repository.get.assert_called_once_with("123")
```

## Property-Based Testing

Use Hypothesis to test invariants:

```python
from hypothesis import given, strategies as st

@given(st.text(min_size=10, max_size=10, alphabet="0123456789"))
def test_identifier_validation_always_accepts_10_digits(value: str):
    """Property: Any 10-digit string should be accepted."""
    identifier = Identifier(value)
    assert len(str(identifier)) == 10

@given(st.integers(min_value=0), st.floats(min_value=0.0))
def test_amount_never_negative(base_amount: int, multiplier: float):
    """Property: Calculated amount should never be negative."""
    result = calculate_amount(base_amount, multiplier)
    assert result >= 0
```

## Test Isolation

### Rules
1. **No shared state** between tests
2. **Function-scoped fixtures** for mutable objects
3. **No test order dependency** — tests pass in any order
4. **Mock external dependencies** — network, filesystem, time

### Database Fixtures
```python
@pytest.fixture(scope="session")
def db_engine():
    """Session-scoped engine for all tests."""
    engine = create_async_engine(TEST_DATABASE_URL)
    yield engine
    engine.dispose()

@pytest.fixture(scope="function")
async def db_session(db_engine):
    """Function-scoped session with transaction rollback."""
    async with db_engine.connect() as conn:
        trans = await conn.begin()
        session = AsyncSession(bind=conn)
        yield session
        await trans.rollback()  # Rollback isolates tests
```

## Assertions

### Clear and Specific
```python
# Good: Clear, specific assertions
assert result.status == StatusCode.COMPLETED
assert len(result.items) == 3
assert result.total_amount == 150.00
assert "error" not in result.messages

# Bad: Vague assertions
assert result
assert result.items
assert result.total_amount
```

### Error Testing
```python
# Good: Test exception with message pattern
def test_invalid_identifier_raises_validation_error():
    """Identifier validator raises ValidationError with clear message."""
    with pytest.raises(ValidationError, match="Invalid identifier format"):
        Identifier("invalid")

# Bad: Test exception without checking message
def test_invalid_identifier_raises_validation_error():
    with pytest.raises(ValidationError):
        Identifier("invalid")
```

## Parameterized Tests

Test multiple scenarios efficiently:

```python
@pytest.mark.parametrize("value,expected_valid", [
    ("1234567890", True),
    ("invalid", False),
    ("", False),
    ("123", False),
    ("12345678901", False),  # Too long
])
def test_identifier_validation_scenarios(value: str, expected_valid: bool):
    """Test identifier validation with various inputs."""
    if expected_valid:
        result = Identifier(value)
        assert str(result) == value
    else:
        with pytest.raises(ValidationError):
            Identifier(value)
```

## Coverage Requirements

| Layer | Target | Rationale |
|-------|--------|-----------|
| Core (domain) | 90%+ | Critical business logic |
| Application | 80%+ | Orchestration and use cases |
| Infrastructure | 60%+ | Adapters have edge cases |
| Presentation | 70%+ | API endpoints and error handling |

Run coverage:
```bash
uv run pytest --cov=src --cov-report=html --cov-report=term-missing
```

## Integration Test Patterns

### API Testing
```python
@pytest.mark.integration
async def test_create_item_endpoint(async_client: AsyncClient, db_session):
    """POST /api/items creates new item in database."""
    request_data = {
        "customer_id": "cust-123",
        "product_id": "prod-456",
        "amount": 1000.00
    }
    response = await async_client.post("/api/items", json=request_data)

    assert response.status_code == 201
    item_data = response.json()
    assert item_data["customer_id"] == "cust-123"

    # Verify database state
    item = await db_session.get(Item, item_data["item_id"])
    assert item is not None
    assert item.customer_id == "cust-123"
```

### Repository Testing
```python
@pytest.mark.integration
async def test_entity_repository_save_and_retrieve(db_session):
    """Repository saves entity and retrieves it correctly."""
    repo = SqlAlchemyEntityRepository(session=db_session)
    entity = EntityFactory.build()

    # Save
    await repo.save(entity)
    await db_session.flush()

    # Retrieve
    retrieved = await repo.get(entity.entity_id)
    assert retrieved is not None
    assert retrieved.entity_id == entity.entity_id
    assert retrieved.customer_id == entity.customer_id
```

## Test Documentation

Every test must have a docstring explaining:
- **What** is being tested
- **Why** this behavior matters (if not obvious)

```python
def test_service_retries_on_transient_error():
    """Service retries database operations on transient errors.

    This ensures the system is resilient to temporary database
    connection issues without failing the entire request.
    """
    pass
```

## Verification Commands

All test commands run through **uv**/**Task**. Never use `pdm`, `poetry`, or a
bare `pytest`.

```bash
# Run all tests
task test

# Run with verbose output
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/unit/core/test_entity.py

# Run specific test
uv run pytest tests/unit/core/test_entity.py::test_entity_creation

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing

# Run only fast tests
uv run pytest -m "unit and not slow"
```
