from __future__ import annotations

import typing as t

from starlette.responses import StreamingResponse

from ._fragments import fragment

if t.TYPE_CHECKING:
    from starlette.background import BackgroundTask

    from ._types import Node


class HtpyResponse(StreamingResponse):
    def __init__(
        self,
        node: Node,
        status_code: int = 200,
        headers: t.Mapping[str, str] | None = None,
        media_type: str | None = "text/html",
        background: BackgroundTask | None = None,
    ) -> None:
        super().__init__(
            content=fragment[node].aiter_chunks(),
            status_code=status_code,
            headers=headers,
            media_type=media_type,
            background=background,
        )
