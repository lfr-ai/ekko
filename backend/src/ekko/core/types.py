"""Core-layer shared type aliases and scalar wrappers.

Centralizes domain-agnostic type definitions used across layers.
Follows the pattern established in the koda_automation golden standard.
"""

__all__ = [
    "BaseDict",
    "JSONDict",
    "PromptContent",
]

type BaseDict = dict[str, object]
type JSONDict = dict[str, object]
type PromptContent = str
