
import os

from dotenv import load_dotenv
from tavily import TavilyClient


load_dotenv()


def web_search(query: str, max_results: int = 5) -> list[dict]:
    """
    Search the web and return relevant results.

    Args:
        query: The user's search query.
        max_results: Maximum number of results to return.

    Returns:
        A list of search result dictionaries.
    """

    if not query.strip():
        raise ValueError("Search query cannot be empty.")

    if not 1 <= max_results <= 10:
        raise ValueError("max_results must be between 1 and 10.")

    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        raise RuntimeError(
            "TAVILY_API_KEY is missing from the .env file."
        )

    client = TavilyClient(api_key=api_key)

    response = client.search(
        query=query,
        max_results=max_results,
    )

    results = []

    for item in response.get("results", []):
        results.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "content": item.get("content", ""),
        })

    return results
