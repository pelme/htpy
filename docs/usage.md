
# Usage

## Elements

Elements are imported directly from the `htpy` module as their name:

```pycon
>>> from htpy import div
>> print(div)
<div></div>
```

Children are specified using the `[]` "getitem" syntax. Children can
be strings, markup, other elements or lists/iterators.

Elements can be arbitrarily nested:
```pycon title="Nested elements"
>>> from htpy import article, section, p
>>> print(section[article[p["Lorem ipsum"]]])
<section><article><p>Lorem ipsum</p></article></section>
```
### Text/strings

It is possible to pass a string directly:
```pycon title="Using a string as children"
>>> from htpy import h1
>>> print(h1["Welcome to my site!"])
<h1>Welcome to my site!</h1>
```

Strings are automatically escaped to avoid [XSS
vulnerabilites](https://owasp.org/www-community/attacks/xss/). It is convenient
and safe to directly insert variable data via f-strings:

```pycon
>>> from htpy import h1
>>> user_supplied_name = "bobby </h1>"
>>> print(h1[f"hello {user_supplied_name}"])
<h1>hello bobby &lt;/h1&gt;</h1>
```

### Conditional rendering

`None` and `False` will not render anything. This can be useful to conditionally render some content.

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

### Loops/iterating over children

You can pass an list, tuple or generator to generate multiple children:

```pycon title="Iterate over a generator"
>>> from htpy import ul, li
>>> print(ul[(li[letter] for letter in "abc")])
<ul><li>a</li><li>b</li><li>c</li></ul>
```

A `list` can be used similar to a [JSX fragment](https://react.dev/reference/react/Fragment):

```pycon title="Render a list of child elements"
>>> from htpy import div, img
>>> my_images = [img(src="a.jpg"), img(src="b.jpg")]
>>> print(div[my_images])
<div><img src="a.jpg"><img src="b.jpg"></div>
```

### Custom elements / web components

[Custom elements / web
components](https://developer.mozilla.org/en-US/docs/Web/API/Web_components/Using_custom_elements)
are HTML elements that contains at least one dash (`-`). Since `-` cannot be
used in Python identifiers, use underscore (`_`) instead:

```pycon title="Using custom elements"
>>> from htpy import my_custom_element
>>> print(my_custom_element['hi!'])
<my-custom-element>hi!</my-custom-element>
```

### Injecting markup

If you have HTML markup that you want to insert without further escaping, wrap
it in `Markup` from the [markupsafe](https://markupsafe.palletsprojects.com/)
library. markupsafe is a dependency of htpy and is automatically installed:

```pycon title="Injecting markup"
>>> from htpy import div
>>> from markupsafe import Markup
>>> print(div[Markup("<foo></foo>")])
<div><foo></foo></div>
```


## Attributes

HTML attributes are defined by calling the element. They can be specified in a couple of different ways.

### Elements without attributes

Some elements do not have attributes, they can be specified by just the element itself:

```pycon
>>> from htpy import hr
>>> print(hr)
<hr>
```

### Keyword arguments

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

### id/class shorthand

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
<div id="foo bar"></div>
```

```pycon title="Combining both id and classes"
>>> from htpy import div
>>> print(div("#myid.foo.bar"))
<div id="myid" class="foo bar"></div>
```

### Attributes as dict

Attributes can also be specified by a `dict`. This is useful when using
attributes that are reserved Python keywords (like `for` or `class`), when the
attribute name contains a dash (`-`) or when you want to define attributes
dynamically.

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

### Boolean attributes
In HTML, boolean attributes such as `disabled` are considered "true" when they
exists. Specifying an attribute as `True` will make it appear (without a value).
`False` will make it hidden. This is useful and brings to semantics of `bool` to
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

### Combining modes

Attributes via id/class shorthand, keyword arguments and dictionary can be combined:

```pycon title="Specifying attribute via multiple arguments"
>>> from htyp import label
>>> print(label("#myid.foo.bar", {'for': "somefield"}, name="myname",))
<label id="myid" class="foo bar" for="somefield" name="myname"></label>
```
