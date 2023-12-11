from flask import Flask, url_for

from htpy import body, button, div, h1, head, html, li, p, script, title, ul

app = Flask(__name__)


@app.route("/")
def home():
    return str(
        html[
            head[
                title["My awesome htmx/flask app!"],
                script(src="https://unpkg.com/htmx.org@1.9.8"),
            ],
            body[
                div(".container")[
                    div(".header")[h1["This is my page!"]],
                    div(".content")[
                        p["Hey, I can count to 10!"],
                        button(
                            hx_get=url_for("counter"),
                            hx_trigger="click",
                            hx_target="#result",
                        )["Count"],
                    ],
                ],
                div("#result"),
            ],
        ]
    )


@app.route("/count")
def counter():
    one_to_ten = [li[i] for i in range(1, 11)]
    return str(ul[one_to_ten])


if __name__ == "__main__":
    app.run(debug=True)
