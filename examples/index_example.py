from htpy import body, h1, html, img, li, ul

is_fun = True
menu = ["spam", "ham", "eggs"]

print(
    html[
        body(class_={"fun": is_fun})[
            h1("#hi")["Welcome to htpy!"],
            img(src="rabbit.jpg"),
            ul(".menu")[(li[item] for item in menu)],
        ]
    ]
)
