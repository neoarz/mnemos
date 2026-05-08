from __future__ import annotations

# Chat Completions API tool format: {"type": "function", "function": {...}}
# strict=True requires all properties in `required` and additionalProperties=False.
# Optional params use ["type", "null"] and are still listed in required.

WEB_SEARCH: dict[str, object] = {
    "type": "function",
    "function": {
        "name": "web_search",
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

READ_URL: dict[str, object] = {
    "type": "function",
    "function": {
        "name": "read_url",
        "description": (
            "Fetch and read the full content of a specific URL. "
            "Use when a user shares a link and wants to know what is on that page. "
            "Handles JavaScript-rendered pages and PDFs automatically."
        ),
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The full URL to read, e.g. 'https://example.com/article'.",
                },
            },
            "required": ["url"],
            "additionalProperties": False,
        },
    },
}

ALL_TOOLS: list[dict[str, object]] = [WEB_SEARCH, READ_URL]
