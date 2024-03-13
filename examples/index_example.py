from htpy import body, h1, html, img

is_cool = True

print(
    html[
        body(class_={"cool": is_cool})[
            h1("#hi")["Welcome to htpy!"],
            img(src="cat.jpg"),
        ]
    ]
)
