
from tools.web_search import web_search


query = "What are AI agents in artificial intelligence?"

try:
    results = web_search(query, max_results=3)

    if not results:
        print("No search results found.")

    for index, result in enumerate(results, start=1):
        print(f"\nResult {index}")
        print("Title:", result["title"])
        print("URL:", result["url"])
        print("Content:", result["content"][:300])

except Exception as error:
    print("Search failed:", error)
