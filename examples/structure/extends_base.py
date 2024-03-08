import datetime

from htpy import body, div, h1, head, html, p, title


def base_layout(*, page_title=None, extra_head=None, content=None, body_class=None):
    return html[
        head[title[page_title], extra_head],
        body(class_=body_class)[
            content,
            div("#footer")[f"Copyright {datetime.date.today().year} by Foo Inc."],
        ],
    ]


def index():
    return base_layout(
        page_title="Welcome!",
        body_class="green",
        content=[h1["Welcome to my site!"], p["Hello and welcome!"]],
    )


def about():
    return base_layout(
        page_title="About us",
        content=[
            h1["About us"],
            p["We love creating web sites!"],
        ],
    )
