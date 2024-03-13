<p align="center">
    <img src="https://htpy.dev/assets/htpy.webp" width="300">
</p>

# htpy - HTML in Python

htpy is a library that makes writing HTML in Python fun and efficient,
without the need for a template language.

<div class="grid cards" markdown>

-   __Define HTML elements in Python...__

    ```python
    from htpy import html, body, h1, img

    is_cool = True

    html[
      body(class_={"cool": is_cool})[
        h1("#hi")["Welcome to htpy!"],
        img(src="cat.jpg"),
      ]
    ]
    ```

-   __...and render it as HTML.__
    ```html
    <!doctype html>
    <html>
      <body class="cool">
        <h1 id="hi">Welcome to htpy!</h1>
        <img src="cat.jpg">
      </body>
    </html>
    ```
</div>

## Introduction
At [Personalkollen](https://personalkollen.se/start/), where htpy was originally
developed we often found ourselves hitting walls when using classic templates.
htpy was created to improve the productiveness and experience of generating HTML
from a Python backend.

## Key features

- **Leverage static types:** - Use [mypy](https://mypy.readthedocs.io/en/stable/) or [pyright](https://github.com/microsoft/pyright) to type check your code.

- **Great debugging:** Avoid cryptic stack traces from templates. Use your favorite Python debugger.

- **Easy to extend:** There is no special way to define template tags/filters. Just call regular functions.

- **Create reusable components:** Define components, snippets, complex layouts/pages as regular Python variables or functions.

- **Familiar concepts from React:** React helped make it popular writing HTML with a programming language. htpy uses a lot of similar constructs.
