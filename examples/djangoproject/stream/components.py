from collections.abc import Iterable

from htpy import Element, body, h1, head, html, link, table, td, th, title, tr

from .items import Item


def streaming_table_page(items: Iterable[Item]) -> Element:
    return html[
        head[
            title["Stream example"],
            link(
                href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css",
                rel="stylesheet",
                integrity="sha384-T3c6CoIi6uLrA9TneNEoa7RxnatzjcDSCmG1MXxSR1GAsXEV/Dwwykc2MPK8M2HN",
                crossorigin="anonymous",
            ),
        ],
        body[
            h1["Stream example"],
            table(".table.table-striped")[
                tr[th["Table row #"],],
                (
                    tr[td(style=f"background-color: {item.color}")[f"#{item.count}"],]
                    for item in items
                ),
            ],
        ],
    ]
