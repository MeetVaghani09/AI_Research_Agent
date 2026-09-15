from app.rag.retriever import retrieve_documents

if __name__ == "__main__":
    question = input("Question: ")
    results = retrieve_documents(question, k=5, session_id="global")

    print("\n" + "=" * 80)
    print("RETRIEVAL RESULTS")
    print("=" * 80)

    for i, (document, score) in enumerate(results, 1):
        print(f"\nRESULT {i}")
        print("Score:", score)
        print("File:", document.metadata.get("source"))
        print("Page:", document.metadata.get("page"))
        print(document.page_content[:700])
