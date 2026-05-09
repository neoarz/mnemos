from __future__ import annotations

from exa_py import AsyncExa

from mnemos.app.errors import InferenceError

TOOL_NAME = "web_search"

WEB_SEARCH: dict[str, object] = {
    "type": "function",
    "function": {
        "name": TOOL_NAME,
        "description": (
            "Search the web for current information. "
            "Use when asked about real-world facts, recent events, news, or anything "
            "that may have changed since your training data. "
            "Returns titles, URLs, and relevant excerpts from the top results. "
            "Always cite the source URLs in your response."
        ),
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "Natural language description of the ideal page to find. "
                        "Be descriptive, e.g. "
                        "'fastest production car in the world 2025' "
                        "rather than short keywords."
                    ),
                },
                "num_results": {
                    "type": ["integer", "null"],
                    "description": (
                        "Number of results to return (1-10). "
                        "Pass null to use the default of 5."
                    ),
                },
            },
            "required": ["query", "num_results"],
            "additionalProperties": False,
        },
    },
}


async def execute_web_search(exa: AsyncExa, args: dict[str, object]) -> str:
    query = str(args["query"])
    raw_n = args.get("num_results")
    num_results = int(raw_n) if isinstance(raw_n, int) else 5
    try:
        response = await exa.search(
            query,
            num_results=num_results,
            contents={"highlights": True},
        )
    except Exception as exc:
        raise InferenceError(f"{TOOL_NAME} failed: {exc}") from exc

    if not response.results:
        return "No results found."

    parts: list[str] = []
    for i, result in enumerate(response.results, start=1):
        title = result.title or "Untitled"
        url = result.url
        highlights = result.highlights or []
        excerpt = " ... ".join(h.strip() for h in highlights if h.strip())
        entry = f"[{i}] {title}\n    {url}"
        if excerpt:
            entry += f"\n    {excerpt}"
        parts.append(entry)

    return "\n\n".join(parts)
