from app.evaluation.dataset import EVALUATION_DATASET
from app.graph.graph import graph


SESSION_ID = "research-user"


def check_retrieval(
    document_context: str,
    keywords: list[str],
) -> tuple[bool, float]:

    if not keywords:
        return True, 1.0

    if not document_context:
        return False, 0.0

    context = document_context.lower()

    matched_keywords = sum(
        keyword.lower() in context
        for keyword in keywords
    )

    coverage = matched_keywords / len(keywords)

    return coverage >= 0.5, coverage


def check_answer(
    answer: str,
    expected_answer: str,
) -> bool:

    if not answer:
        return False

    answer_lower = answer.lower()
    expected_lower = expected_answer.lower()

    expected_keywords = [
        word.strip(".,!?()")
        for word in expected_lower.split()
        if len(word.strip(".,!?()")) > 3
    ]

    if not expected_keywords:
        return True

    matched = sum(
        keyword in answer_lower
        for keyword in expected_keywords
    )

    coverage = matched / len(expected_keywords)

    return coverage >= 0.5


def run_evaluation():

    print("=" * 70)
    print("ResearchOS Evaluation")
    print("=" * 70)

    retrieval_passed = 0
    answer_passed = 0
    total_tests = len(EVALUATION_DATASET)

    for index, test_case in enumerate(
        EVALUATION_DATASET,
        start=1,
    ):

        question = test_case["question"]
        expected_answer = test_case["expected_answer"]
        keywords = test_case["retrieval_keywords"]
        should_find_document = test_case["should_find_document"]

        result = graph.invoke(
            {
                "question": question,
                "session_id": SESSION_ID,
                "history": "",
            }
        )

        route = result.get("route")
        document_context = result.get(
            "document_context",
            "",
        )
        document_found = result.get(
            "document_found",
            False,
        )
        answer = result.get(
            "answer",
            "",
        )

        print()
        print(f"Test {index}")
        print("-" * 70)
        print(f"Question: {question}")
        print(f"Route: {route}")

        # -------------------------------------------------
        # DOCUMENT RETRIEVAL EVALUATION
        # -------------------------------------------------

        if should_find_document:

            retrieval_ok, retrieval_score = check_retrieval(
                document_context,
                keywords,
            )

            if retrieval_ok:
                retrieval_passed += 1

            print(
                f"Retrieval: "
                f"{'PASS' if retrieval_ok else 'FAIL'} "
                f"({retrieval_score:.0%} keyword coverage)"
            )

        else:

            retrieval_ok = not document_found

            if retrieval_ok:
                retrieval_passed += 1

            print(
                "Document Rejection: "
                f"{'PASS' if retrieval_ok else 'FAIL'}"
            )

        # -------------------------------------------------
        # ANSWER EVALUATION
        # -------------------------------------------------

        if should_find_document:

            answer_ok = check_answer(
                answer,
                expected_answer,
            )

        else:

            answer_ok = not document_found

        if answer_ok:
            answer_passed += 1

        print(f"Expected: {expected_answer}")
        print(f"Answer: {answer}")

        print(
            f"Answer Check: "
            f"{'PASS' if answer_ok else 'FAIL'}"
        )

    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    overall_passed = (
        retrieval_passed == total_tests
        and answer_passed == total_tests
    )

    print()
    print("=" * 70)
    print("Evaluation Summary")
    print("=" * 70)

    print(
        f"Retrieval: "
        f"{retrieval_passed}/{total_tests}"
    )

    print(
        f"Answer Quality: "
        f"{answer_passed}/{total_tests}"
    )

    print(
        f"Overall: "
        f"{total_tests}/{total_tests}"
        if overall_passed
        else "FAILED"
    )

    print("=" * 70)


if __name__ == "__main__":
    run_evaluation()