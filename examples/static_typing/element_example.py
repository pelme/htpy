from typing import Literal

from htpy import Element, span


def bootstrap_badge(
    text: str,
    style: Literal["success", "danger"],
) -> Element:
    return span(f".badge.text-bg-{style}")[text]
