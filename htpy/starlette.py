from __future__ import annotations

import typing as t

from starlette.responses import StreamingResponse

from . import aiter_node

if t.TYPE_CHECKING:
    from starlette.background import BackgroundTask

    from . import Node


class HtpyResponse(StreamingResponse):
    def __init__(
        self,
        content: Node,
        status_code: int = 200,
        headers: t.Mapping[str, str] | None = None,
        media_type: str | None = "text/html",
        background: BackgroundTask | None = None,
    ):
        super().__init__(
            aiter_node(content),
            status_code=status_code,
            headers=headers,
            media_type=media_type,
            background=background,
        )
