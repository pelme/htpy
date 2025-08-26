# Static Typing

htpy was designed to be used with static typing. Since you define all your own
data/components with regular Python, a static type checker like mypy will catch
errors like this:

```python

class User:
    def __init__(self, name: str):
        self.name = name


def greeting(user: User) -> Renderable:
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

## Renderable

htpy elements, fragments and context objects provides are "renderable". The `Renderable` type provides a consistent API to render a `htpy` object as HTML.

The `Renderable` protocol defines these methods:

 - `.__str__()` - render as a HTML string by calling `str()`
 - `.__html__()`  - render as a HTML string that is safe to use as markup. This makes it possible to directly embed a `Renderable` object in [Django/Jinja templates](django.md#using-htpy-as-part-of-an-existing-django-template).
 - `.iter_chunks()` - stream the contents as string "chunks". See [Streaming](streaming.md) for more information.

All `Renderable`'s are also `Node`'s and can always be used as a child element. You can use this to write reusable components that can be used as a child node but also be rendered by themselves or embedded into a Django or Jinja template:

```pycon
>>> from htpy import div, h1, Renderable
>>> def my_component(name: str) -> Renderable:
...     return div[h1[f"Hello {name}!"]]
>>> print(my_component("Dave"))
<div><h1>Hello Dave!</h1></div>

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
from htpy import Node, Renderable, div

def bootstrap_alert(contents: Node) -> Renderable:
    return div(".alert", role="alert")[contents]
```
