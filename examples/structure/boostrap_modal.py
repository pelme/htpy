from markupsafe import Markup

from htpy import Element, Node, button, div, h5, span


def bootstrap_modal(*, title: str, body: Node = None, footer: Node = None) -> Element:
    return div(".modal", tabindex="-1", role="dialog")[
        div(".modal-dialog", role="document")[
            div(".modal-content")[
                div(".modal-header")[
                    div(".modal-title")[
                        h5(".modal-title")[title],
                        button(
                            ".close",
                            type="button",
                            data_dismiss="modal",
                            aria_label="Close",
                        )[span(aria_hidden="true")[Markup("&times;")]],
                    ]
                ],
                div(".modal-body")[body],
                footer and div(".modal-footer")[footer],
            ]
        ]
    ]


if __name__ == "__main__":
    from htpy import button, p

    print(
        bootstrap_modal(
            title="Modal title",
            body=p["Modal body text goes here."],
            footer=[
                button(".btn.btn-primary", type="button")["Save changes"],
                button(".btn.btn-secondary", type="button")["Close"],
            ],
        )
    )
