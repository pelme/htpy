# Convert HTML to htpy Code

Maybe you already have a bunch of HTML, or templates that you would like to migrate to htpy.
We got you covered. The utility command `html2htpy` ships with `htpy`, and can be used to transform existing
html into Python code (htpy!).

```
$ html2htpy -h
usage: html2htpy [-h] [-f {auto,ruff,black,none}] [-i {yes,h,no}] [--no-shorthand] [input]

positional arguments:
  input                 input HTML from file or stdin

options:
  -h, --help            show this help message and exit
  -f {auto,ruff,black,none}, --format {auto,ruff,black,none}
                        Select one of the following formatting options: auto, ruff, black or none
  -i {yes,h,no}, --imports {yes,h,no}
                        Output mode for imports of found htpy elements
  --no-shorthand        Use explicit `id` and `class_` kwargs instead of the shorthand #id.class syntax
```

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
$  html2htpy index.html
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

## Piping Input/Stdin Stream

You can also pipe input to htpy, for example `cat demo.html | html2htpy`.

This can be combined with other workflows in the way that you find most suitable.
For example, you might pipe from your clipboard to htpy, and optionally direct the output to a file.

#### Linux

```
xclip -o -selection clipboard | html2htpy > output.py
```

#### Mac

```
pbpaste | html2htpy > output.py
```

#### Windows

```
powershell Get-Clipboard | html2htpy > output.py
```

## Formatting the Output

`html2htpy` can format the output Python code using `black` or `ruff`.
Select the preferred formatter with the `-f`/`--format` flag. Options are `auto`, `ruff`, `black` and `none`.

By default, the selection will be `auto`, formatting if it finds a formatter on path, prefering `ruff` if it's available.
If no formatters are available on path, the output will not be formatted.

## Import Options

You have a couple of options regarding imports with the `-i`/`--imports` flag.
Options are `yes` (default), `h`, `no`.

#### Module import of htpy: `--imports=h`

Some people prefer to `import htpy as h` instead of importing individual elements from htpy.
If this is you, you can use the `--imports=h` option to get corresponding output when using `html2htpy`.

```py title="$ html2htpy --imports=h example.html"
import htpy as h

h.section("#main-section.hero.is-link")[
    h.p(".subtitle.is-3.is-spaced")["Welcome"]
]
```

## Explicit ID and Class Kwargs

If you prefer the explicit `id="id", class_="class"` kwargs syntax over the default htpy shorthand `#id.class` syntax, you can get it by passing the `--no-shorthand` flag.

```html title="example.html"
<section id="main-section" class="hero is-link">
  <p class="subtitle is-3 is-spaced">Welcome</p>
</section>
```

#### Default Shorthand Yield `#id.class`

```py title="$ html2htpy example.html"
from htpy import p, section

section("#main-section.hero.is-link")[
    p(".subtitle.is-3.is-spaced")["Welcome"]
]
```

#### No Shorthand Yields Kwargs `id`, `class_`

```py title="$ html2htpy --no-shorthand example.html"
from htpy import p, section

section(id="main-section", class_="hero is-link")[
    p(class_="subtitle is-3 is-spaced")["Welcome"]
]
```

## Template Interpolation to f-strings

`html2htpy` will try to convert template variables to pythonic f-strings:

`template {{ variables }}` -> `f"template { variables }"`

Note that other typical template syntax, such as loops `{% for x in y %}`, can not be transformed this way,
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
    ol[
        """        {% for step in recipe.steps %}        """,
        li[f"{ step }"],
        """        {% endfor %}    """,
    ],
]
```
