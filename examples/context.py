from typing import Literal

from htpy import Context, Node, div, h1

Theme = Literal["light", "dark"]

theme_context: Context[Theme] = Context("theme", default="light")


def my_page() -> Node:
    return theme_context.provider(
        "dark",
        div[
            h1["Hello!"],
            sidebar("The Sidebar!"),
        ],
    )


@theme_context.consumer
def sidebar(theme: Theme, title: str) -> Node:
    return div(class_=f"theme-{theme}")[title]


print(my_page())
