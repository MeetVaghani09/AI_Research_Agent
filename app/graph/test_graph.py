from app.graph.graph import graph


if __name__ == "__main__":
    question = input("Question: ")

    result = graph.invoke(
        {
            "question": question,
            "session_id": "cli-test",
            "history": "",
        }
    )

    print("\nRoute:", result.get("route"))
    print("\nAnswer:\n", result.get("answer"))

    print("\nSources:")
    for source in result.get("sources", []):
        print(source)
