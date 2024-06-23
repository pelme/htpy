<p align="center">
    <img src="https://htpy.dev/assets/htpy.webp" width="300">
</p>

# htpy - HTML in Python

htpy is a library that makes writing HTML in plain Python fun and efficient,
without a template language.

**Define HTML in Python:**

```python
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
```

**And Get HTML:**

```html
<!DOCTYPE html>
<html>
  <head>
    <title>Todays menu</title>
  </head>
  <body>
    <h1>Menu</h1>
    <ul class="menu">
      <li>egg+bacon</li>
      <li>bacon+spam</li>
      <li>eggs+spam</li>
    </ul>
  </body>
</html>
```

## Motivation for This Project

At [Personalkollen](https://personalkollen.se/start/), where htpy was originally
developed we often found ourselves hitting walls when using classic templates.
htpy was created to improve the productiveness and experience of generating HTML
from a Python backend.

## Key Features

- **Leverage static types:** Use [mypy](https://mypy.readthedocs.io/en/stable/) or [pyright](https://github.com/microsoft/pyright) to type check your code.

- **Great debugging:** Avoid cryptic stack traces from templates. Use your favorite Python debugger.

- **Easy to extend:** There is no special way to define template tags/filters. Just call regular functions.

- **Works with existing Python web framework:** Works great with Django, Flask or any other Python web framework!

- **Works great with htmx:** htpy makes for a great experience when writing server rendered partials/components.

- **Create reusable components:** Define components, snippets, complex layouts/pages as regular Python variables or functions.

- **Familiar concepts from React:** React helped make it popular writing HTML with a programming language. htpy uses a lot of similar constructs.

## Philosophy

htpy generates HTML elements and attributes and provide a few helpers.

htpy does not enforce any particular pattern or style to organize
your pages, components and layouts. That does not mean that htpy cannot be used
to build sophisticated web pages or applications.

Rather the opposite: you are encouraged the leverage the power of Python to
structure your project. Use modules, classes, functions, decorators, list
comprehension, generators, conditionals, static typing and any other feature of
Python to organize your components. This gives you a lot of power and makes htpy
scale from a single small Flask project to bigger applications.

[Common patterns](https://htpy.dev/common-patterns/) can give you some ideas
that you can build upon yourself.

## The Syntax

Child elements are specified using the `[]` syntax. This may look strange at
first but it has some nice benefits. This clearly separates attributes from
child elements and makes the code more readable. It is implemented using the
`__getitem__` method, just like lists or dicts.

## Installation

[htpy is available on PyPI](https://pypi.org/project/htpy/). You may install the latest version using pip:

```
pip install htpy
```

## Documentation

The full documentation is available at [https://htpy.dev](https://htpy.dev):

- [Usage](https://htpy.dev/usage/)
- [Common patterns](https://htpy.dev/common-patterns/)
- [Static typing](https://htpy.dev/static-typing/)
- [Usage with Django](https://htpy.dev/django/)
- [Streaming of contents](https://htpy.dev/streaming/)
- [Convert HTML to htpy code](https://htpy.dev/html2htpy/)
- [FAQ](https://htpy.dev/faq/)
- [References](https://htpy.dev/references/)
