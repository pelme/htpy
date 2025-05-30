from typing import Literal

from htpy import Renderable, span


def bootstrap_badge(
    text: str,
    style: Literal["success", "danger"],
) -> Renderable:
    return span(f".badge.text-bg-{style}")[text]
