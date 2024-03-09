<img src="assets/htpy.webp" style="max-width: 300px; margin: 0 auto 60px auto; display: block;">

# htpy - HTML in Python

htpy is a library that makes writing HTML in Python fun and efficient,
without the need for a template language.

<div class="grid cards" markdown>

-   __Define HTML elements in Python...__

    ___

    ```python
    from htpy import (
        html, body, h1, img
    )

    is_cool = True

    html[
      body(class_={"cool": is_cool})[
        h1("#hi")["Welcome to htpy!"],
        img(src="cat.jpg"),
      ]
    ]
    ```

-   __...and render it as HTML.__

    ---
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

### Leverage static types
We have been increasing static type coverage and seen great effects of static
typing. But when it comes to HTML produced by templates, after the template
context is created, static type checkers hit a wall. This looses a lot of the
value of using a type checker since a lot of the code that use domain
specific objects cannot be checked.

### Great debugging
Debugging a template system can be hard. The stack traces are often cryptic and
hides the real culprit of a problem. Inspecting/debugging the template context
is not possible without special tooling or debuggers. Debugging code written
with htpy works with any Python debugger and gives usable stack traces.

Many editors provide "goto definition". These often does not work reliably with
templates.

### Automatic code formatting
Black is a very popular code formatter for Python. There are formatters that
formats templates but we have found them lacking compared to tools like Black.

### Easy to extend
Extending a template system with custom tags and filters requires learning about
the template system parser and tokenizer, rather than just writing plain Python
functions. Adding even a trivial filter requires putting the function in a
specific location and registering the filter with the template library. Filters
and tags with htpy are just plain Python functions.

### Creating components
Creating components/partials is typically done with includes or inclusion tags
in a template language. With htpy, components/partials can be plain Python
variables or functions. Making it easy to create partials and components makes
it easier to maintain a library of components/partials. See [UI components](common-patterns.md#ui-components) for more information.

### Familiar concepts
React/JSX has popularized the idea of using a programming language rather than a
separate template language. The concept of building a tree of components and
composing them with regular modules/classes/functions should be familiar to
anyone with React/JSX experience.
