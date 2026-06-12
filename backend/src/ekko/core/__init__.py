"""Core domain layer — entities, value objects, enums, and interface protocols.

This layer is the innermost ring of the Clean Architecture. It contains:
- Domain entities (aggregate roots and supporting entities)
- Value objects (immutable, self-validating domain primitives)
- Domain enumerations
- Domain exceptions
- Domain events (past-tense facts about what happened)
- Interface protocols (ports) for repositories and external services
- Shared type aliases

Framework independence: This layer has ZERO imports from application frameworks
(FastAPI, Django) or infrastructure libraries (SQLAlchemy, httpx).
"""

__all__: list[str] = []
