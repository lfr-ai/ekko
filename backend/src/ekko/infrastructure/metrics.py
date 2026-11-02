"""Application-level Prometheus metrics for Ekko.

Defines domain-specific metrics for the audio-streaming, transcription,
and summarization pipeline. Exposed alongside HTTP metrics at ``/metrics``.
"""

from __future__ import annotations

from typing import Final

from prometheus_client import Counter, Gauge, Histogram

# ── Transcription ─────────────────────────────────────────────

TRANSCRIPTION_SEGMENTS_TOTAL: Final[Counter] = Counter(
    "ekko_transcription_segments_total",
    "Total transcript segments produced by the STT pipeline.",
    ("source",),
)

# ── LLM / Chat ───────────────────────────────────────────────

LLM_REQUESTS_TOTAL: Final[Counter] = Counter(
    "ekko_llm_requests_total",
    "Total LLM completion requests.",
    ("operation", "status"),
)

LLM_REQUEST_DURATION_SECONDS: Final[Histogram] = Histogram(
    "ekko_llm_request_duration_seconds",
    "LLM completion request duration in seconds.",
    ("operation",),
    buckets=(0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0),
)

# Optional cost and token tracking (only recorded when cost tracking is enabled)
LLM_REQUEST_TOKENS_TOTAL: Final[Counter] = Counter(
    "ekko_llm_request_tokens_total",
    "Total tokens used in LLM requests (input + output).",
    ("operation", "token_type"),  # token_type: input, output
)

LLM_REQUEST_COST_TOTAL: Final[Counter] = Counter(
    "ekko_llm_request_cost_usd_total",
    "Total cost of LLM requests in USD (when cost tracking is enabled).",
    ("operation",),
)

# ── Audio Streaming ───────────────────────────────────────────

AUDIO_STREAMS_ACTIVE: Final[Gauge] = Gauge(
    "ekko_audio_streams_active",
    "Currently active audio capture streams.",
)
