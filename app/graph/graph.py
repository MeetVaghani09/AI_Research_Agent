
from langgraph.graph import END, START, StateGraph

from app.graph.nodes import (
    analyze_question,
    generate_answer,
    generate_web_query,
    retrieve_from_qdrant,
    route_question,
    search_from_web,
    validate_document_relevance,
)

from app.graph.state import ResearchState


# Create the graph
builder = StateGraph(ResearchState)


# --------------------------------------------------
# Nodes
# --------------------------------------------------

builder.add_node(
    "analyze_question",
    analyze_question,
)

builder.add_node(
    "route_question",
    route_question,
)

builder.add_node(
    "retrieve_from_qdrant",
    retrieve_from_qdrant,
)

builder.add_node(
    "validate_document_relevance",
    validate_document_relevance,
)

builder.add_node(
    "generate_web_query",
    generate_web_query,
)

builder.add_node(
    "search_from_web",
    search_from_web,
)

builder.add_node(
    "generate_answer",
    generate_answer,
)


# --------------------------------------------------
# Initial flow
# --------------------------------------------------

builder.add_edge(
    START,
    "analyze_question",
)

builder.add_edge(
    "analyze_question",
    "route_question",
)


# --------------------------------------------------
# Route question
# --------------------------------------------------

builder.add_conditional_edges(
    "route_question",
    lambda state: state["route"],
    {
        "document": "retrieve_from_qdrant",
        "web": "generate_web_query",
        "both": "retrieve_from_qdrant",
    },
)


# --------------------------------------------------
# Document retrieval
#
# document:
#   relevant PDF → answer
#   irrelevant PDF → web
#
# both:
#   PDF → web → answer
# --------------------------------------------------
builder.add_edge(
    "retrieve_from_qdrant",
    "validate_document_relevance",
)

builder.add_conditional_edges(
    "validate_document_relevance",
    lambda state: (
        "web"
        if state.get("route") == "both"
        or not state.get("document_found", False)
        else "answer"
    ),
    {
        "web": "generate_web_query",
        "answer": "generate_answer",
    },
)

# --------------------------------------------------
# Web query generation
# --------------------------------------------------

builder.add_edge(
    "generate_web_query",
    "search_from_web",
)


# --------------------------------------------------
# Web search → final answer
# --------------------------------------------------

builder.add_edge(
    "search_from_web",
    "generate_answer",
)


# --------------------------------------------------
# Final answer
# --------------------------------------------------

builder.add_edge(
    "generate_answer",
    END,
)


# Compile graph
graph = builder.compile()

