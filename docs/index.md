# htpy - HTML in Python


`htpy` is a small library that helps you write HTML directly in Python, without a template language:

```pycon
>>> from htpy import html, head, title, body, h1
>>> print(html[head[title["Hello htpy"]], body["hi!"]])
<!doctype html><html><head><title>Hello htpy</title></head><body>hi!</body></html>
```

## Motivation
Using Python to generate HTML leads to some benefits compared to template languages:

 - Use static type checking for your HTML generation.
 - Your regular tools/editor with "goto definition" works.
 - Use [black](https://black.readthedocs.io/en/stable/) for formatting.
 - There is no need to learn another (templating) library.
 - Debugging templates becomes easier since you can debug htpy markup just like to debug regular python code.

## Features
htpy has some features that helps writing HTML:

- All strings are escaped by default
- Integrates with Django/jinja2 templates/markup to allow integration in existing projects
- `htpy` code works fine with type annotations
- The `html` element will include a proper doctype automatically

## Usage

### Elements

Elements are imported directly from the `htpy` module as their name:

```pycon
>>> from htpy import div
>> print(div)
<div></div>
```

### Attributes

HTML attributes are defined by calling the element. They can be specified in a couple of different ways.


#### Keyword arguments

Attributes can be specified via keyword arguments:

```pycon
>>> from htpy import img
>>> print(img(src="picture.jpg"))
<img src="picture.jpg">
```

In Python, `class` and `for` cannot be used as keyword arguments. Instead, they can be specified as `class_` or `for_` when using keyword arguments:

```pycon
>>> from htpy import img
>>> print(label(for_="myfield"))
<label for="myfield"></label>
```

#### id/class shorthand

Using `id` and `class` attributes is a very common task. A shorthand that looks like a CSS selector can be used:

```pycon title="Setting an id"
>>> from htpy import div
>>> print(div("#myid"))
<div id="myid"></div>
```

```pycon title="Setting classes"
>>> from htpy import div
>>> print(div(".foo.bar"))
<div id="foo bar"></div>
```

```pycon title="Combining both id and classes"
>>> from htpy import div
>>> print(div("#myid.foo.bar"))
<div id="myid" class="foo bar"></div>
```

#### Dictionary attribute

Attributes can also be specified by a dictionary. This is useful when using attributes that are reserved Python keywords (like `for` or `class`), when the attribute name contains a dash (`-`) or when you want to define attributes dynamically.

```pycon title="Using an attribute with a dash"
>>> from htpy import div
>>> print(div({"data-foo": "bar"}))
<div data-foo="bar"></div>
```

```pycon title="Using an attribute with a reserved keyword"
>>> from htpy import label
>>> print(label({"for": "myfield"}))
<label for="myfield"></label>
```

#### Boolean attributes
In HTML, boolean attributes are considered "true" when they exists or otherwise "false". Python bool `True` and `False` will make an attribute behave like this:

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

#### Combining modes

Attributes via id/class shorthand, keyword arguments and dictionary can be combined:

```pycon title="Specifying attribute via multiple arguments"
>>> from htyp import label
>>> print(label("#myid.foo.bar", {'for': "somefield"}, name="myname",))
<label id="myid" class="foo bar" for="somefield" name="myname"></label>
```

### Child elements

HTML child elements are specified using the `[]` syntax. Children can be
strings, markup, other elements or lists/iterators.

```pycon title="Using a string as children"
>>> from htpy import h1
>>> print(h1["Welcome to my site!"])
<h1>Welcome to my site!</h1>
```

Elements can be arbitrarily nested:
```pycon title="Nested elements"
>>> from htpy import article, section, p
>>> print(section[article[p["Lorem ipsum"]]])
<section><article><p>Lorem ipsum</p></article></section>
```

#### Loops/iterating over children

You can pass an list, tuple or generator to generate multiple children:

```pycon title="Iterate over a generator"
>>> from htpy import ul, li
>>> print(ul[(li[letter] for letter in "abc")])
<ul><li>a</li><li>b</li><li>c</li></ul>
```

#### Conditional rendering

`None` and `False` will not render a element. This can be useful to conditionally render some content.

```pycon title="Conditional rendering"

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
