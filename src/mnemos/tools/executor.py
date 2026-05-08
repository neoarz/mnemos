from __future__ import annotations

import json
from dataclasses import dataclass

from exa_py import AsyncExa

from mnemos.app.errors import InferenceError


@dataclass(frozen=True, slots=True)
class ToolExecutor:
    exa: AsyncExa

    async def execute(self, name: str, arguments_json: str) -> str:
        try:
            args: dict[str, object] = json.loads(arguments_json)
        except json.JSONDecodeError as exc:
            raise InferenceError(f"Invalid tool arguments for {name!r}: {exc}") from exc

        if name == "web_search":
            query = str(args["query"])
            raw_n = args.get("num_results")
            num_results = int(raw_n) if isinstance(raw_n, int) else 5
            return await self._web_search(query=query, num_results=num_results)

        if name == "read_url":
            return await self._read_url(url=str(args["url"]))

        raise InferenceError(f"Unknown tool: {name!r}")

    async def _web_search(self, query: str, num_results: int) -> str:
        try:
            response = await self.exa.search(
                query,
                num_results=num_results,
                contents={"highlights": True},
            )
        except Exception as exc:
            raise InferenceError(f"web_search failed: {exc}") from exc

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

    async def _read_url(self, url: str) -> str:
        try:
            response = await self.exa.get_contents(
                [url],
                text={"max_characters": 5000},
            )
        except Exception as exc:
            raise InferenceError(f"read_url failed for {url!r}: {exc}") from exc

        if not response.results:
            return f"Could not fetch content from {url}"

        page = response.results[0]
        title = page.title or "Untitled"
        text = (page.text or "").strip()
        if not text:
            return f"No readable content found at {url}"

        return f"Title: {title}\nURL: {url}\n---\n{text}"
