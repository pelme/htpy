import datetime

from htpy import body, div, h1, head, html, p, script, title


class BaseLayout:
    def head(self):
        return [
            title[self.title],
        ]

    def footer(self):
        return div("#footer")[f"Copyright {datetime.date.today().year} by Foo Inc."]

    def render(self):
        return html[
            head[self.head()],
            body[
                self.content,
                self.footer(),
            ],
        ]


class Index(BaseLayout):
    title = "Welcome!"
    content = [
        h1["Welcome to my site!"],
        p["Hello and welcome!"],
    ]

    def head(self):
        return [
            super().head(),
            script(src="./welcome.js"),
        ]


class About(BaseLayout):
    title = "About us"
    content = [
        h1["About us"],
        p["We love creating web sites!"],
    ]

    def head(self):
        return [
            super().head(),
            script(src="./aboutus.js"),
        ]


print(Index().render())
print(About().render())
