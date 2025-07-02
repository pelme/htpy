# Usage

Elements are imported directly from the `htpy` module as their name. HTML attributes are specified by parenthesis (`()` / "call"). Children are specified using square brackets (`[]` / "getitem").

```pycon
>>> from htpy import div
>>> print(div(id="hi")["Hello!"])
<div id="hi">Hello!</div>

```

## Elements

Children can be strings, markup, other elements or lists/iterators.

Elements can be arbitrarily nested:

```pycon title="Nested elements"
>>> from htpy import article, section, p
>>> print(section[article[p["Lorem ipsum"]]])
<section><article><p>Lorem ipsum</p></article></section>

```

### Text/Strings

It is possible to pass a string directly:

```pycon title="Using a string as children"
>>> from htpy import h1
>>> print(h1["Welcome to my site!"])
<h1>Welcome to my site!</h1>

```

Strings are automatically escaped to avoid [XSS
vulnerabilities](https://owasp.org/www-community/attacks/xss/). It is convenient
and safe to directly insert variable data via f-strings:

```pycon
>>> from htpy import h1
>>> user_supplied_name = "bobby </h1>"
>>> print(h1[f"hello {user_supplied_name}"])
<h1>hello bobby &lt;/h1&gt;</h1>

```

### Conditional Rendering

`True`, `False` and `None` will not render anything. Python's `and` and `or`
operators will
[short-circuit](https://docs.python.org/3/library/stdtypes.html#boolean-operations-and-or-not).
You can use this to conditionally render content with inline `and` and
`or`.

```pycon title="Conditional rendering with a value that may be None"

>>> from htpy import div, b
>>> error = None

>>> # No <b> tag will be rendered since error is None
>>> print(div[error and b[error]])
<div></div>

>>> error = 'Enter a valid email address.'
>>> print(div[error and b[error]])
<div><b>Enter a valid email address.</b></div>

# Inline if/else can also be used:
>>> print(div[b[error] if error else None])
<div><b>Enter a valid email address.</b></div>

```

```pycon title="Conditional rendering based on a bool variable"
>>> from htpy import div
>>> is_happy = True
>>> print(div[is_happy and "😄"])
<div>😄</div>

>>> is_sad = False
>>> print(div[is_sad and "😔"])
<div></div>

>>> is_allowed = True
>>> print(div[is_allowed or "Access denied!"])
<div></div>

>>> is_allowed = False
>>> print(div[is_allowed or "Access denied!"])
<div>Access denied!</div>

```

### Fragments

Fragments allow you to wrap a group of nodes (not necessarily elements) so that
they can be rendered without a wrapping element.

```pycon
>>> from htpy import p, i, fragment
>>> content = fragment["Hello ", None, i["world!"]]
>>> print(content)
Hello <i>world!</i>

>>> print(p[content])
<p>Hello <i>world!</i></p>

```

### Loops / Iterating Over Children

You can pass a list, tuple or generator to generate multiple children:

```pycon title="Iterate over a generator"
>>> from htpy import ul, li
>>> print(ul[(li[letter] for letter in "abc")])
<ul><li>a</li><li>b</li><li>c</li></ul>

```

!!! note

    The generator will be lazily evaluated when rendering the element, not
    directly when the element is constructed. See [Streaming](streaming.md) for
    more information.

!!! warning "Generator Consumption"

    Generators can only be consumed once. If you try to render an element containing a generator multiple times, you will get a `RuntimeError` on the second attempt:

    ```python
    >>> element = div[(x for x in "abc")]
    >>> str(element)  # First render - works
    '<div>abc</div>'
    >>> str(element)  # Second render - fails
    RuntimeError: Generator has already been consumed
    ```

    If you need to render the same content multiple times, use a `list` instead of a generator.

A `list` can be used similar to a [JSX fragment](https://react.dev/reference/react/Fragment):

```pycon title="Render a list of child elements"
>>> from htpy import div, img
>>> my_images = [img(src="a.jpg"), img(src="b.jpg")]
>>> print(div[my_images])
<div><img src="a.jpg"><img src="b.jpg"></div>

```

### Custom Elements / Web Components

[Custom elements / web
components](https://developer.mozilla.org/en-US/docs/Web/API/Web_components/Using_custom_elements)
are HTML elements that contain at least one dash (`-`). Since `-` cannot be
used in Python identifiers, use underscore (`_`) instead:

```pycon title="Using custom elements"
>>> from htpy import my_custom_element
>>> print(my_custom_element['hi!'])
<my-custom-element>hi!</my-custom-element>

```

### Injecting Markup

If you have HTML markup that you want to insert without further escaping, wrap
it in `Markup` from the [markupsafe](https://markupsafe.palletsprojects.com/)
library. markupsafe is a dependency of htpy and is automatically installed:

```pycon title="Injecting markup"
>>> from htpy import div
>>> from markupsafe import Markup
>>> print(div[Markup("<foo></foo>")])
<div><foo></foo></div>

```

If you are generating [Markdown](https://pypi.org/project/Markdown/) and want to insert it into an element,
use `Markup` to mark it as safe:

```pycon title="Injecting generated markdown"
>>> from markdown import markdown
>>> from markupsafe import Markup
>>> from htpy import div
>>> print(div[Markup(markdown('# Hi'))])
<div><h1>Hi</h1></div>

```

### HTML Doctype

The [HTML doctype](https://developer.mozilla.org/en-US/docs/Glossary/Doctype) is automatically prepended to the `<html>` tag:

```pycon
>>> from htpy import html
>>> print(html)
<!doctype html><html></html>

```

### HTML Comments

Since the Python code is the source of the HTML generation, to add a comment to
the code, most of the time regular Python comments (`#`) are used.

If you want to emit HTML comments that will be visible in the browser, use the `comment` function:

```pycon
>>> from htpy import div, comment
>>> print(div[comment("This is a HTML comment, visible in the browser!")])
<div><!-- This is a HTML comment, visible in the browser! --></div>

```

It is safe to pass arbitrary text to the comment function. Double dashes (`--`)
will be removed to avoid being able to break out of the comment.

If you need full control over the exact rendering of the comment, you can create
comments or arbitrary text by injecting your own markup. See the [Injecting
Markup](#injecting-markup) section above for details.

## Attributes

HTML attributes are defined by calling the element. They can be specified in a couple of different ways.

### Elements Without Attributes

Some elements do not have attributes, they can be specified by just the element itself:

```pycon
>>> from htpy import hr
>>> print(hr)
<hr>

```

### Keyword Arguments

Attributes can be specified via keyword arguments:

```pycon
>>> from htpy import img
>>> print(img(src="picture.jpg"))
<img src="picture.jpg">

```

In Python, `class` and `for` cannot be used as keyword arguments. Instead, they can be specified as `class_` or `for_` when using keyword arguments:

```pycon
>>> from htpy import label
>>> print(label(for_="myfield"))
<label for="myfield"></label>

```

Attributes that contain dashes `-` can be specified using underscores:

```pycon
>>> from htpy import form
>>> print(form(hx_post="/foo"))
<form hx-post="/foo"></form>

```

### Id/Class Shorthand

Defining `id` and `class` attributes is common when writing HTML. A string shorthand
that looks like a CSS selector can be used to quickly define id and classes:

```pycon title="Define id"
>>> from htpy import div
>>> print(div("#myid"))
<div id="myid"></div>

```

```pycon title="Define multiple classes"
>>> from htpy import div
>>> print(div(".foo.bar"))
<div class="foo bar"></div>

```

```pycon title="Combining both id and classes"
>>> from htpy import div
>>> print(div("#myid.foo.bar"))
<div id="myid" class="foo bar"></div>

```

### Attributes as Dict

Attributes can also be specified as a `dict`. This is useful when using
attributes that are reserved Python keywords (like `for` or `class`), when the
attribute name contains a dash (`-`) or when you want to define attributes
dynamically.

```pycon title="Using Alpine.js with @-syntax (shorthand for x-on)"
>>> from htpy import button
>>> print(button({"@click.shift": "addToSelection()"}))
<button @click.shift="addToSelection()"></button>

```

```pycon title="Using an attribute with a reserved keyword"
>>> from htpy import label
>>> print(label({"for": "myfield"}))
<label for="myfield"></label>

```

You can also specify multiple dictionaries  containing attributes. This is
especially useful if you have variables with a common preset group of 
attributes, or are using helper functions to create a dictionary of attributes.

```pycon title="Using multiple dictionaries with attributes"
>>> from htpy import button
>>> print(button({"disabled": True}, {"hx-post": "/foo"}))
<button disabled hx-post="/foo"></button>

```

### Boolean/Empty Attributes

In HTML, boolean attributes such as `disabled` are considered "true" when they
exist. Specifying an attribute as `True` will make it appear (without a value).
`False` will make it hidden. This is useful and brings the semantics of `bool` to
HTML.

```pycon title="True bool attribute"
>>> from htpy import button
>>> print(button(disabled=True))
<button disabled></button>

```

```pycon title="False bool attribute"
>>> from htpy import button
>>> print(button(disabled=False))
<button></button>

```

### Conditionally Mixing CSS Classes

To make it easier to mix CSS classes, the `class` attribute
accepts a list of class names or a dict. Falsey values will be ignored.

```pycon
>>> from htpy import button
>>> is_primary = True
>>> print(button(class_=["btn", {"btn-primary": is_primary}]))
<button class="btn btn-primary"></button>
>>> is_primary = False
>>> print(button(class_=["btn", {"btn-primary": is_primary}]))
<button class="btn"></button>
>>>

```

### Combining Modes

Attributes via id/class shorthand, keyword arguments and dictionary can be combined:

```pycon title="Specifying attribute via multiple arguments"
>>> from htpy import label
>>> print(label("#myid.foo.bar", {'for': "somefield"}, name="myname",))
<label id="myid" class="foo bar" for="somefield" name="myname"></label>

```

### Escaping of Attributes

Attributes are always escaped. This makes it possible to pass arbitrary HTML
fragments or scripts as attributes. The output may look a bit obfuscated since
all unsafe characters are escaped but the browser will interpret it correctly:

```pycon
>>> from htpy import button
>>> print(button(onclick="let name = 'andreas'; alert('hi' + name);")["Say hi"])
<button onclick="let name = &#39;andreas&#39;; alert(&#39;hi&#39; + name);">Say hi</button>

```

In the browser, the parsed attribute as returned by
`document.getElementById("example").getAttribute("onclick")` will be the
original string `let name = 'andreas'; alert('hi' + name);`.

Escaping will happen whether or not the value is wrapped in `markupsafe.Markup`
or not. This may seem confusing at first but is useful when embedding HTML
snippets as attributes:

```pycon title="Escaping of Markup"
>>> from htpy import ul
>>> from markupsafe import Markup
>>> # This markup may come from another library/template engine
>>> some_markup = Markup("""<li class="bar"></li>""")
>>> print(ul(data_li_template=some_markup))
<ul data-li-template="&lt;li class=&#34;bar&#34;&gt;&lt;/li&gt;"></ul>

```

## Streaming chunks

htpy objects provide the `iter_chunks()` method to render an element with its
children one piece at a time.

```pycon
>>> from htpy import ul, li
>>> for chunk in ul[li["a"], li["b"]].iter_chunks():
...     print(f"got a chunk: {chunk!r}")
...
got a chunk: '<ul>'
got a chunk: '<li>'
got a chunk: 'a'
got a chunk: '</li>'
got a chunk: '<li>'
got a chunk: 'b'
got a chunk: '</li>'
got a chunk: '</ul>'

```

If you need to get the chunks of an element without parents, wrap it in a `Fragment`:

```pycon
>>> from htpy import li, fragment
>>> for chunk in fragment[li["a"], li["b"]].iter_chunks():
...     print(f"got a chunk: {chunk!r}")
...
got a chunk: '<li>'
got a chunk: 'a'
got a chunk: '</li>'
got a chunk: '<li>'
got a chunk: 'b'
got a chunk: '</li>'

```

## Passing Data with Context

Usually, you pass data via regular function calls and arguments via your
components. Contexts can be used to avoid having to pass the data manually
between components. Contexts in htpy is conceptually similar to contexts in
React.

Using contexts in htpy involves:

- Creating a context object with `my_context = Context(name[, *, default])` to
  define the type and optional default value of a context variable.
- Using `my_context.provider(value, children)` to set the value of a context variable for a subtree.
- Adding the `@my_context.consumer` decorator to a component that requires the
  context value. The decorator will add the context value as the first argument to the decorated function:

The `Context` class is a generic and fully supports static type checking.

The values are passed as part of the tree used to render components without
using global state.

A context value can be passed arbitrarily deep between components. It is
possible to nest multiple context provider and different values can be used in
different subtrees.

A single component can consume as many contexts as possible by using multiple
decorators:

```python
@context_b.consumer
@context_a.consumer
def my_component(a, b):
    ...
```

### Example

This example shows how context can be used to pass data between components:

- `theme_context: Context[Theme] = Context("theme", default="light")` creates a
  context object that can later be used to define/retrieve the value. In this
  case, `"light"` acts as the default value if no other value is provided.
- `theme_context.provider(value, subtree)` defines the value of the
  `theme_context` for the subtree. In this case the value is set to `"dark"` which
  overrides the default value.
- The `sidebar` component uses the `@theme_context.consumer` decorator. This
  will make htpy pass the current context value as the first argument to the
  component function.
- In this example, a `Theme` type is used to ensure that the correct types are
  used when providing the value as well as when it is consumed.

```py
from typing import Literal

from htpy import Context, Node, div, h1

Theme = Literal["light", "dark"]

theme_context: Context[Theme] = Context("theme", default="light")


def my_page() -> Node:
    return theme_context.provider(
        "dark",
        div[
            h1["Hello!"],
            sidebar("The Sidebar!"),
        ],
    )


@theme_context.consumer
def sidebar(theme: Theme, title: str) -> Node:
    return div(class_=f"theme-{theme}")[title]


print(my_page())
```

Output:

```html
<div>
  <h1>Hello!</h1>
  <div class="theme-dark">The Sidebar!</div>
</div>
```
