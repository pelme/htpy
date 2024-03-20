from htpy import body, h1, head, html, li, title, ul

menu = ["egg+bacon", "bacon+spam", "eggs+spam"]

print(
    html[
        head[title["Todays menu"]],
        body[
            h1["Menu"],
            ul(".menu")[(li[item] for item in menu)],
        ],
    ]
)
