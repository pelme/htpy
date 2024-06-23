# Static Typing

htpy was designed to be used with static typing. Since you define all your own
data/components with regular Python, a static type checker like mypy will catch
errors like this:

```python

class User:
    def __init__(self, name: str):
        self.name = name


def greeting(user: User) -> Element:
    return h1[f"Hi {user.first_name.capitalize()}!]
#                        ^^^^^^^^^^
# mypy: error: "User" has no attribute "first_name"  [attr-defined]
```

## Autocompletion of HTML Elements

htpy ships with type annotations for all HTML elements. If your editor supports it, it will show you useful auto completions:

![Screenshot of autocomplete in VS Code.](assets/autocomplete.webp "Using autocomplete in VS Code.")

## `Element` and `VoidElement` Classes

The base types/classes in htpy are `Element` and `VoidElement`. `Element` are
all regular HTML elements that can have children such as `<div>`, `<span>` and
`<table>`. `VoidElement` are [HTML void
element](https://developer.mozilla.org/en-US/docs/Glossary/Void_element) which
cannot have children such as `<img>`, `<input>` and `<br>`.

Use `Element` as the return type when you want to always return an element.

```python
from typing import Literal

from htpy import Element, span


def bootstrap_badge(
    text: str,
    style: Literal["primary", "success", "danger"] = "primary",
) -> Element:
    return span(f".badge.text-bg-{style}")[text]

```

## Node

`Node` is a type alias for all possible objects that can be used as a child
node. [See the source for the exact
definition](https://github.com/pelme/htpy/blob/28ec3b3d469e11192079378598d549305709999c/htpy/__init__.py#L226C1-L226C5)
that defines all kinds of nodes that can be children of an element. This is a
wider type than `Element` since child nodes can be str, markup, None, iterables
or callables.

Use `Node` when you want to create a wrapper function to be flexible with what you accept. This function will accept both a str or some other element to be passed as `contents`:

```python
from htpy import Element, Node, div

def bootstrap_alert(contents: Node) -> Element:
    return div(".alert", role="alert")[contents]
```
