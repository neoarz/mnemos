from __future__ import annotations

import json
from dataclasses import dataclass

from exa_py import AsyncExa

from mnemos.app.errors import InferenceError
from mnemos.tools.read_url import TOOL_NAME as READ_URL_TOOL_NAME
from mnemos.tools.read_url import execute_read_url
from mnemos.tools.web_search import TOOL_NAME as WEB_SEARCH_TOOL_NAME
from mnemos.tools.web_search import execute_web_search


@dataclass(frozen=True, slots=True)
class ToolExecutor:
    exa: AsyncExa

    async def execute(self, name: str, arguments_json: str) -> str:
        try:
            args: dict[str, object] = json.loads(arguments_json)
        except json.JSONDecodeError as exc:
            raise InferenceError(f"Invalid tool arguments for {name!r}: {exc}") from exc

        if name == WEB_SEARCH_TOOL_NAME:
            return await execute_web_search(self.exa, args)

        if name == READ_URL_TOOL_NAME:
            return await execute_read_url(self.exa, args)

        raise InferenceError(f"Unknown tool: {name!r}")
