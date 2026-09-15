from qdrant_client.models import FieldCondition, Filter, MatchValue

from app.rag.vector_store import vector_store
from app.rag.embeddings import embeddings


# Retrieval settings
DEFAULT_K = 8
DEFAULT_SCORE_THRESHOLD = 0.25
FETCH_MULTIPLIER = 3
MIN_FETCH = 20
MMR_LAMBDA = 0.7
RELATIVE_SCORE_THRESHOLD = 0.55


def _filter_for_session(
    session_id: str | None,
    filename: str | None = None,
):
    """
    Build a Qdrant filter for the current session
    and optionally a specific document.
    """

    if not session_id:
        return None

    conditions = [
        FieldCondition(
            key="metadata.session_id",
            match=MatchValue(value=session_id),
        )
    ]

    if filename:
        conditions.append(
            FieldCondition(
                key="metadata.source",
                match=MatchValue(value=filename),
            )
        )

    return Filter(must=conditions)


def _select_dynamic_results(
    results: list[tuple],
    max_results: int = DEFAULT_K,
) -> list[tuple]:
    """
    Keep the strongest and sufficiently relevant results.
    """

    if not results:
        return []

    results = sorted(
        results,
        key=lambda item: float(item[1]),
        reverse=True,
    )

    strongest_score = float(results[0][1])

    selected = []

    for document, score in results:
        score = float(score)

        # Always keep the strongest result.
        if not selected:
            selected.append((document, score))
            continue

        # Maximum number of results.
        if len(selected) >= max_results:
            break

        # Keep results reasonably close to the strongest result.
        if strongest_score > 0:
            relative_score = score / strongest_score

            if relative_score >= RELATIVE_SCORE_THRESHOLD:
                selected.append((document, score))

    return selected


def retrieve_documents(
    query: str,
    k: int = DEFAULT_K,
    score_threshold: float = DEFAULT_SCORE_THRESHOLD,
    session_id: str | None = None,
    filename: str | None = None,
):
    """
    Retrieve relevant and diverse document chunks.

    Pipeline:

    1. Convert query into an embedding.
    2. Search Qdrant.
    3. Use MMR for diversity.
    4. Apply minimum similarity threshold.
    5. Remove weak results.
    """

    if not query or not query.strip():
        return []

    # Don't search the entire database accidentally.
    if not session_id:
        return []

    qdrant_filter = _filter_for_session(
        session_id=session_id,
        filename=filename,
    )

    fetch_k = max(
        k * FETCH_MULTIPLIER,
        MIN_FETCH,
    )

    query_vector = embeddings.embed_query(query)

    results = (
        vector_store
        .max_marginal_relevance_search_with_score_by_vector(
            embedding=query_vector,
            k=k,
            fetch_k=fetch_k,
            lambda_mult=MMR_LAMBDA,
            filter=qdrant_filter,
            score_threshold=score_threshold,
        )
    )

    return _select_dynamic_results(
        results,
        max_results=k,
    )