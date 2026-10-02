---
name: rag
description: 'Retrieval-Augmented Generation conventions — chunking, embeddings, pgvector storage, retrieval and reranking, and evaluation. Use when adding or changing a document-ingestion, chunking, embedding, retrieval, or reranking pipeline step.'
---

# RAG Skill

A RAG pipeline is a chain of Core ports, each independently swappable and
independently testable — never one monolithic "do RAG" function.

| Stage | Owns | Port shape |
| --- | --- | --- |
| Load | Fetch raw source documents | `DocumentLoaderClientPort` |
| Chunk | Split into retrieval-sized units | pure Core function, no port needed |
| Embed | Text → vector | `EmbeddingClientPort` |
| Store | Persist vectors + metadata | `RepositoryPort` over the vector column |
| Retrieve | Query vector (+ optional full-text) → candidates | `RetrievalPort` |
| Rerank (optional) | Reorder candidates by relevance | `RerankerPort` |
| Generate | Candidates + query → answer | `ChatClientPort` (see the `litellm` skill) |

## Chunking

- `chunk_size` and `chunk_overlap` are plain `int`s, not value objects — they
  are internal knobs sourced from a validated module constant, not user input
  crossing a trust boundary (see the `python-conventions` skill's Hard Rule 16
  worked example).
- Chunk on structure first (heading, paragraph, section) and fall back to a
  fixed token/character window only when structure is absent — a chunk that
  splits mid-sentence degrades retrieval quality more than a slightly uneven
  chunk size.
- Keep a stable, reversible link from each chunk back to its source document
  and offset (for citation and re-ingestion) — chunking is lossy in one
  direction only.

## Embeddings

- Pick one embedding model per corpus/vector column and never mix dimensions
  in the same column — re-embed the whole corpus on a model change instead of
  appending vectors of a different dimensionality.
- Define `EmbeddingClientPort` as a Core `Protocol` the same way as
  `ChatClientPort`; the adapter is the only place that imports the embedding
  provider's SDK.
- Batch embedding calls (provider APIs bill and rate-limit per request, not
  per token-equivalent-of-a-single-call) — never embed one chunk per request
  in a loop when the provider supports batched input.

## Vector storage (pgvector)

- Match the index type to the distance function used at query time — a
  cosine-distance query against an L2-indexed column silently returns
  degraded (not wrong-shaped, just wrong-ranked) results.
- Prefer an HNSW index for read-heavy retrieval workloads over IVFFlat
  (better recall/latency trade-off without a training step); IVFFlat needs a
  representative data sample before `CREATE INDEX` or its clusters are poor.
- Keep the vector column and its index behind the Repository port — Core and
  Application never import `pgvector` or issue raw SQL distance operators.

## Retrieval

- `top_k` is a plain `int` query parameter (same reasoning as `chunk_size`),
  sourced from a validated module constant like `RAG_TOP_K`.
- Prefer hybrid search (vector similarity + full-text/keyword) over pure
  vector search when exact-term recall matters (product names, IDs, codes) —
  pure embeddings under-retrieve on tokens the embedding model undertrained
  on.
- Retrieval is a read path: never mutate state as a side effect of a query.

## Reranking

A reranker is a second-stage, cross-encoder-style port applied only to the
already-retrieved candidate set (tens, not the whole corpus) — running it
over the full corpus defeats the purpose of the first-stage vector search
and is a latency/cost regression, not an accuracy improvement.

## Evaluation

- Treat retrieval quality (precision/recall of the right chunks) and
  generation quality (faithfulness/groundedness of the answer to the
  retrieved chunks) as two separate metrics — a good answer built on the
  wrong chunk is a retrieval bug wearing a generation-quality costume.
- Run a fixed evaluation/backtest set on every retrieval or chunking change,
  not just on prompt changes — chunking and embedding-model swaps silently
  shift which documents are even retrievable.

## Observability

Trace each pipeline stage as its own OTel span (see the `observability-stack`
skill's `with tracer.start_as_current_span(...)` example) so a slow or
low-quality answer can be attributed to load, chunk, embed, retrieve, rerank,
or generate — a single end-to-end span cannot localize which stage
regressed.

## Port boundary discipline

Never leak a vector-store client, an embedding-provider SDK type, or a raw
SQL distance expression past Infrastructure — mirrors the
`clean-architecture` skill's Dependency Rule and is checked the same way any
other port/adapter pair is by `ports:check`/`check_ports_adapters.py`.

## References

- [pgvector README](https://github.com/pgvector/pgvector) — index types,
  distance operators, and query planning.
- [OpenTelemetry Python instrumentation](https://opentelemetry.io/docs/languages/python/instrumentation/)
