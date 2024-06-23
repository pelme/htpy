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

`None` will not render anything. This can be useful to conditionally render some content.

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
are HTML elements that contains at least one dash (`-`). Since `-` cannot be
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

If you are generate [Markdown](https://pypi.org/project/Markdown/) and want to insert it into an element, use `Markup`:

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

Attributes that contains dashes `-` can be specified using underscores:

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
>>> from htyp import label
>>> print(label("#myid.foo.bar", {'for': "somefield"}, name="myname",))
<label id="myid" class="foo bar" for="somefield" name="myname"></label>
```

### Escaping of Attributes

Attributes are always escaped. This makes it possible to pass arbitrary HTML
fragments or scripts as attributes. The output may look a bit obfuscated since
all unsafe characters are escaped but the browser will interpret it correctly:

```pycon
>>> from htpy import button
>>> print(button(id="example", onclick="let name = 'andreas'; alert('hi' + name);")["Say hi"])
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

## Iterating of the Output

Iterating over a htpy element will yield the resulting contents in chunks as
they are rendered:

```pycon
>>> from htpy import ul, li
>>> for chunk in ul[li["a", "b"]]:
...     print(f"got a chunk: {chunk!r}")
...
got a chunk: '<ul>'
got a chunk: '<li>'
got a chunk: 'a'
got a chunk: 'b'
got a chunk: '</li>'
got a chunk: '</ul>'
```
