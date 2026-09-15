import re
from pathlib import Path

from app.graph.state import ResearchState
from app.llm import llm
from app.prompts.answer import answer_prompt
from app.prompts.router import router_prompt
from app.rag.retriever import retrieve_documents
from app.tools.web_search import web_search
from app.prompts.web_query import web_query_prompt


def analyze_question(state: ResearchState):
    return {"question": state["question"].strip()}

def route_question(state: ResearchState):
    session_id = state.get("session_id")

    has_documents = False

    if session_id:
        safe_session = "".join(
            ch for ch in session_id
            if ch.isalnum() or ch in "-_"
        )[:80]

        upload_dir = Path("data/uploads") / safe_session

        if upload_dir.exists():
            has_documents = any(
                upload_dir.glob("*.pdf")
            )

    prompt = router_prompt.invoke(
        {
            "question": state["question"],
            "history": state.get("history", ""),
            "has_documents": "yes" if has_documents else "no",
        }
    )

    response = llm.invoke(prompt)

    raw = response.content.strip().lower()

    match = re.search(
        r"\b(document|web|both)\b",
        raw,
    )

    route = match.group(1) if match else "web"

    # Safety rule:
    # Never select document if the session has no PDFs.
    if route == "document" and not has_documents:
        route = "web"

    return {"route": route}
def _format_document_results(results):
    context_parts = []
    sources = []

    for index, (document, score) in enumerate(results, start=1):
        metadata = document.metadata

        filename = metadata.get(
            "source",
            "Unknown document",
        )

        page = metadata.get(
            "page",
            0,
        )

        content = document.page_content.strip()

        context_parts.append(
            f"[Document {index}]\n"
            f"File: {filename}\n"
            f"Page: {page + 1}\n"
            f"Content:\n{content}"
        )

        sources.append(
            {
                "type": "document",
                "label": f"{filename} — Page {page + 1}",
                "file": filename,
                "page": page + 1,
                "score": round(float(score), 4),
                "session_id": metadata.get(
                    "session_id"
                ),
                "citation": f"[Document {index}]",
            }
        )

    return "\n\n".join(context_parts), sources

def retrieve_from_qdrant(state: ResearchState):
    results = retrieve_documents(
        query=state["question"],
        k=8,
        session_id=state.get("session_id"),
    )

    context, sources = _format_document_results(results)

    strongest_score = (
        float(results[0][1])
        if results
        else 0.0
    )

    route = state.get("route")

    # Normal document questions require a stronger match.
    if route == "document":
        document_found = strongest_score >= 0.25

    # "both" questions can be broader because they are
    # intended to combine document knowledge with web research.
    elif route == "both":
        document_found = strongest_score >= 0.25

    else:
        document_found = False

    if not document_found:
        context = ""
        sources = []

    return {
        "document_context": (
            context
            or "No relevant uploaded document context was found."
        ),
        "sources": sources,
        "document_found": document_found,
    }
def validate_document_relevance(state: ResearchState):
    document_context = state.get("document_context", "")

    if not document_context or document_context.startswith(
        "No relevant uploaded document"
    ):
        return {
            "document_found": False,
        }

    prompt = f"""
You are a strict document relevance checker for a RAG system.

Your task is to determine whether the uploaded document contains
enough information to directly answer the user's question.

User question:
{state["question"]}

Uploaded document:
{document_context[:6000]}

Rules:

1. Answer YES only if the document explicitly contains the
   information needed to answer the question.

2. Answer NO if the document only talks about the same company,
   person, product, or topic but does not contain the requested fact.

3. Do not use your general knowledge.

4. Do not infer or guess information that is not explicitly present.

5. For example:
   - If the document mentions "Omniscient" but does not mention
     its CEO, then a question asking for the CEO must be NO.
   - If the document mentions "Omniscient" but does not mention
     its headquarters, then a headquarters question must be NO.
   - If the document mentions "19+ years of experience" and the
     question asks about experience, then it is YES.

Return ONLY one word:

YES

or

NO
"""

    response = llm.invoke(prompt)

    result = response.content.strip().upper()

    is_relevant = result == "YES"

    if not is_relevant:
        return {
            "document_found": False,
            "document_context": "No relevant uploaded document context was found.",
            "sources": [],
        }

    return {
        "document_found": True,
    }

def generate_web_query(state: ResearchState):
    prompt = web_query_prompt.invoke(
        {
            "question": state["question"],
        }
    )

    response = llm.invoke(prompt)

    web_query = response.content.strip()

    return {
        "web_query": web_query,
    }
def search_from_web(state: ResearchState):
    query = state.get("web_query") or state["question"]

    response = web_search.invoke(
        {"query": query}
    )

    results = response.get("results", [])

    context_parts = []
    sources = []

    for index, result in enumerate(results, start=1):
        title = result.get("title", "Untitled")
        url = result.get("url", "")
        content = result.get("content", "")

        context_parts.append(
            f"[Web {index}]\n"
            f"Title: {title}\n"
            f"URL: {url}\n"
            f"Content:\n{content}"
        )

        sources.append(
            {
                "type": "web",
                "label": f"Web {index}",
                "title": title,
                "url": url,
                "citation": f"[Web {index}]",
            }
        )

    return {
        "web_context": "\n\n".join(context_parts),
        "sources": state.get("sources", []) + sources,
    }

def generate_answer(state: ResearchState):
    prompt = answer_prompt.invoke(
        {
            "question": state["question"],
            "history": state.get("history", ""),
            "document_context": state.get(
                "document_context",
                "No relevant uploaded document context was found.",
            ),
            "web_context": state.get(
                "web_context",
                "No web context was retrieved.",
            ),
        }
    )

    response = llm.invoke(prompt)

    return {
        "answer": response.content.strip(),
    }