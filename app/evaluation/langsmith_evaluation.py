from langsmith import Client

from app.config import settings
from app.graph.graph import graph

DATASET_NAME = "ai-research-agent-evaluation"


def run_agent(inputs):
    question = inputs["question"]

    result = graph.invoke(
        {
            "question": question,
            "session_id": "langsmith-evaluation",
            "history": "",
        }
    )

    return {
        "answer": result.get("answer", ""),
        "sources": result.get("sources", []),
        "route": result.get("route", ""),
    }


def correctness_evaluator(inputs, outputs, reference_outputs):
    expected = reference_outputs.get("answer", "").lower()
    actual = outputs.get("answer", "").lower()

    key_terms = [
        term for term in expected.split()
        if len(term.strip(".,!?")) > 3
    ]

    matches = sum(
        1 for term in key_terms
        if term.strip(".,!?") in actual
    )

    score = matches / len(key_terms) if key_terms else 0.0

    return {
        "key": "answer_keyword_overlap",
        "score": score,
    }


def main():
    client = Client(
        api_key=settings.langsmith_api_key,
        api_url=settings.langsmith_endpoint,
    )

    print("=" * 80)
    print("LANGSMITH AGENT EVALUATION")
    print("=" * 80)

    results = client.evaluate(
        run_agent,
        data=DATASET_NAME,
        evaluators=[correctness_evaluator],
        experiment_prefix="research-agent",
    )

    print("\nEvaluation completed.")
    print(results)


if __name__ == "__main__":
    main()
