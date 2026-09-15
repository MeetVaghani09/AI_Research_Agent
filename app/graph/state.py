from typing import Any, TypedDict


class ResearchState(TypedDict, total=False):
    question: str
    session_id: str
    history: str
    route: str

    document_context: str
    web_context: str
    web_query: str

    document_found: bool
    sources: list[dict[str, Any]]
    answer: str