from app.rag.retriever import retrieve_documents


SESSION_ID = "research-user"

QUERIES = [
    "How many years of experience does Omniscient have?",
    "What type of company is Omniscient?",
    "What domain does Omniscient have experience in?",
    "What product helps banking and financial service providers connect with corporate customers?",
]


for query in QUERIES:

    print("\n" + "=" * 70)
    print(f"QUERY: {query}")
    print("=" * 70)

    results = retrieve_documents(
        query=query,
        k=8,
        session_id=SESSION_ID,
    )

    if not results:
        print("No results found.")
        continue

    for index, (document, score) in enumerate(results, start=1):

        print(f"\nResult {index}")
        print(f"Score: {float(score):.4f}")
        print(f"Source: {document.metadata.get('source')}")
        print(f"Page: {document.metadata.get('page', 0) + 1}")

        print("Content:")
        print(document.page_content[:1000])