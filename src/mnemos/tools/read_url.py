from __future__ import annotations

from exa_py import AsyncExa

from mnemos.app.errors import InferenceError

TOOL_NAME = "read_url"

READ_URL: dict[str, object] = {
    "type": "function",
    "function": {
        "name": TOOL_NAME,
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


async def execute_read_url(exa: AsyncExa, args: dict[str, object]) -> str:
    url = str(args["url"])
    try:
        response = await exa.get_contents(
            [url],
            text={"max_characters": 5000},
        )
    except Exception as exc:
        raise InferenceError(f"{TOOL_NAME} failed for {url!r}: {exc}") from exc

    if not response.results:
        return f"Could not fetch content from {url}"

    page = response.results[0]
    title = page.title or "Untitled"
    text = (page.text or "").strip()
    if not text:
        return f"No readable content found at {url}"

    return f"Title: {title}\nURL: {url}\n---\n{text}"
