from app.tools.web_search import web_search

if __name__ == "__main__":
    query = input("Search query: ")
    result = web_search.invoke({"query": query})

    print("\n" + "=" * 80)
    print("TAVILY RESULTS")
    print("=" * 80)

    for item in result.get("results", []):
        print("\nTitle:", item.get("title"))
        print("URL:", item.get("url"))
        print("Content:", item.get("content", "")[:500])
