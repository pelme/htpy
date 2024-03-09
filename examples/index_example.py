from htpy import body, h1, html, img

is_cool = True

html[
    body(class_={"cool": is_cool})[
        h1("#hi")["Welcome to htpy!"],
        img(src="grumpycat.jpg"),
    ]
]
