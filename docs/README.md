<p align="center">
    <img src="https://htpy.dev/assets/htpy.webp" width="300">
</p>

# htpy - HTML in Python

htpy is a library that makes writing HTML in plain Python fun and efficient,
without a template language.

**Define HTML in Python:**
```python
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
```

**And get HTML:**
```html
<!DOCTYPE html>
<html>
  <body class="fun">
    <h1 id="hi">Welcome to htpy!</h1>
    <img src="rabbit.jpg">
    <ul class="menu">
      <li>spam</li>
      <li>ham</li>
      <li>eggs</li>
    </ul>
  </body>
</html>
```

## Motivation for this project
At [Personalkollen](https://personalkollen.se/start/), where htpy was originally
developed we often found ourselves hitting walls when using classic templates.
htpy was created to improve the productiveness and experience of generating HTML
from a Python backend.

## Key features

- **Leverage static types:** Use [mypy](https://mypy.readthedocs.io/en/stable/) or [pyright](https://github.com/microsoft/pyright) to type check your code.

- **Great debugging:** Avoid cryptic stack traces from templates. Use your favorite Python debugger.

- **Easy to extend:** There is no special way to define template tags/filters. Just call regular functions.

- **Create reusable components:** Define components, snippets, complex layouts/pages as regular Python variables or functions.

- **Familiar concepts from React:** React helped make it popular writing HTML with a programming language. htpy uses a lot of similar constructs.

## Installation

[htpy is available on PyPI](https://pypi.org/project/htpy/). You may install the latest version using pip:
```
pip install htpy
```

## Documentation
The full documentation is available at https://htpy.dev.
