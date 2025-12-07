# Convert HTML to htpy code

Maybe you already have a bunch of HTML, or templates that you would like to migrate to htpy. We got you covered. This page describes how you can convert existing HTML to htpy code.

The utility command `html2htpy` ships with `htpy`, and can be used to transform existing HTML into Python code (htpy!).

Lets say you have an existing HTML file:

```html title="index.html"
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>htpy Recipes</title>
  </head>
  <body>
    <div id="header">
      <h1>Welcome to the cooking site</h1>
      <p>Your go-to place for delicious recipes!</p>
    </div>

    <div id="recipe-of-the-day" class="section">
      <h2>
        Recipe of the Day: <span class="highlight">Spaghetti Carbonara</span>
      </h2>
      <p>This classic Italian dish is quick and easy to make.</p>
    </div>

    <div id="footer">
      <p>&copy; 2024 My Cooking Site. All rights reserved.</p>
    </div>
  </body>
</html>
```

Now, if you run the command, it outputs the corresponding Python code (htpy).

```
$ html2htpy index.html
```

```py
from htpy import body, div, h1, h2, head, html, meta, p, span, title

html(lang="en")[
    head[
        meta(charset="UTF-8"),
        meta(name="viewport", content="width=device-width, initial-scale=1.0"),
        title["htpy Recipes"],
    ],
    body[
        div("#header")[
            h1["Welcome to the cooking site"], p["Your go-to place for delicious recipes!"]
        ],
        div("#recipe-of-the-day.section")[
            h2["Recipe of the Day: ", span(".highlight")["Spaghetti Carbonara"]],
            p["This classic Italian dish is quick and easy to make."],
        ],
        div("#footer")[p["© 2024 My Cooking Site. All rights reserved."]],
    ],
]
```

## Convert HTML snippets from the clipboard

This can be combined with other workflows in the way that you find most suitable.
For example, you might pipe from your clipboard to htpy, and optionally direct the output to a file.

### Linux

```
xclip -o -selection clipboard | html2htpy > output.py
```

### Mac

```
pbpaste | html2htpy > output.py
```

### Windows

```
powershell Get-Clipboard | html2htpy > output.py
```

## Converting Django/Jinja templates

`html2htpy` will convert Django/Jinja-style template variables to f-strings:

``` html title="input"
<div>hi {{ name }}!</div>
```

``` py title="html2htpy output"

from htpy import div

div[f"hi { name }!"]

```

### Limitations

Other typical template syntax, such as loops `{% for x in y %}`, can not be transformed this way,
so you will often have to clean up a bit after `html2htpy` is done with its thing.

See the example below:

```html title="jinja.html"
<body>
  <h1>{{ heading }}</h1>
  <p>Welcome to our cooking site, {{ user.name }}!</p>

  <h2>Recipe of the Day: {{ recipe.name }}</h2>
  <p>{{ recipe.description }}</p>

  <h3>Instructions:</h3>
  <ol>
    {% for step in recipe.steps %}
      <li>{{ step }}</li>
    {% endfor %}
  </ol>
</body>
```

```py title="$ html2htpy jinja.html"
from htpy import body, h1, h2, h3, li, ol, p

body[
    h1[f"{ heading }"],
    p[f"Welcome to our cooking site, { user.name }!"],
    h2[f"Recipe of the Day: { recipe.name }"],
    p[f"{ recipe.description }"],
    h3["Instructions:"],
    ol[" {% for step in recipe.steps %}", li[f"{ step }"], " {% endfor %}"],
]
```

## VSCode Extension

If you are using VSCode, you can install the [html2htpy](https://marketplace.visualstudio.com/items?itemName=dunderrrrrr.html2htpy) extension to quickly convert HTML to htpy code.
