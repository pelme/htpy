<img src="assets/htpy.webp" style="max-width: 300px; margin: 0 auto 60px auto; display: block;">

# htpy - HTML in Python

htpy is a small library that helps you write HTML directly in Python, without a template language:

```pycon
>>> from htpy import html, head, title, body, h1
>>> print(html[head[title["Hello htpy"]], body["hi!"]])
<!doctype html><html><head><title>Hello htpy</title></head><body>hi!</body></html>
```

## Introduction
At [Personalkollen](https://personalkollen.se/start/), where htpy was originally
developed we often found ourselves hitting walls when using classic templates.
htpy was created to improve the productiveness and experience of generating HTML
from a Python backend.

### Static types
We have been increasing static type coverage and seen great effects of static
typing. But when it comes to HTML produced by templates, after the template
context is created, static type checkers hit a wall. This looses a lot of the
value of using a type checker since a lot of the code that use domain
specific objects cannot be checked.

### Debugging
Debugging a template system can be hard. The stack traces are often cryptic and
hides the real culprit of a problem. Inspecting/debugging the template context
is not possible without special tooling or debuggers. Debugging code written
with htpy works with any Python debugger and gives usable stack traces.

### Tooling
We are big fans of black to format our code. There are formatters that
formats templates but we have found them lacking compared to tools like black.

Many editors provide "goto definition". These often does not work reliably with
templates.

### Extending
Extending a template system with custom tags and filters requires learning about
the template system parser and tokenizer, rather than just writing plain Python
functions. Adding even a trivial filter requires putting the function in a
specific location and registering the filter with the template library. Filters
and tags with htpy are just plain Python functions.

### Creating components/partials
Creating components/partials is typically done with includes or inclusion tags
in a template language. With htpy, components/partials can be plain Python
variables or functions. Making it easy to create partials and components makes
it easier to maintain a library of components/partials.

### Familiar concepts
React/JSX has popularized the idea of using a programming language rather than a separate template language. The concept of building a tree of components and composing them with regular modules/classes/functions should be familiar to anyone with React/JSX experience.
