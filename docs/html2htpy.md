
# Convert HTML to htpy code

Maybe you already have a bunch of HTML, or templates that you would like to migrate to htpy. 
We got you covered. The utility command `html2htpy` ships with `htpy`, and can be used to transform existing 
html into Python code (htpy!).

```
$ html2htpy -h
usage: html2htpy [-h] [-e] [-f {auto,ruff,black,none}] [-i] [input]

positional arguments:
  input                 input HTML from file or stdin

options:
  -h, --help            show this help message and exit
  -e, --explicit        Use explicit `id` and `class_` kwargs instead of the shorthand #id.class syntax
  -f {auto,ruff,black,none}, --format {auto,ruff,black,none}
                        Select one of the following formatting options: auto, ruff, black or none
  -i, --imports         Output imports for htpy elements found
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
        <h2>Recipe of the Day: <span class="highlight">Spaghetti Carbonara</span></h2>
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

## Piping input/stdin stream

You can also pipe input to htpy, for example `cat demo.html | html2htpy`.

This can be combinded with other workflows in the way that you find most suitable. 
For example, you might pipe from your clipboard to htpy, and optionaly direct the output to a file.

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


## Formatting the output
`html2htpy` can format the output Python code using `black` or `ruff`.
Select the preferred formatter with the `-f`/`--format` flag. Options are `auto`, `ruff`, `black` and `none`.

By default, the selection will be `auto`, formatting if it finds a formatter on path, prefering `ruff` if it's available.
If no formatters are available on path, the output not be formatted.


## Explicit id and class kwargs


If you prefer the explicit `id="id", class_="class"` kwargs syntax over the default htpy shorthand `#id.class` syntax, you can get it by passing the `-e`/`--explicit` flag.

```html title="example.html"
<section id="main-section" class="hero is-link">
    <p class="subtitle is-3 is-spaced">Welcome</p>
</section>
```

#### Default shorthand `#id.class`
```py title="$ html2htpy example.html"
section("#main-section.hero.is-link")[
    p(".subtitle.is-3.is-spaced")["Welcome"]
]
```

#### Explicit kwargs `id`, `class_`
```py title="$ html2htpy --explicit example.html"
section(id="main-section", class_="hero is-link")[
    p(class_="subtitle is-3 is-spaced")["Welcome"]
]
```

## Detect htpy imports

If you pass the `-i`/`--imports` flag, htpy elements detected will be included as 
imports in the output. For example:

```py title="$ html2htpy --imports example.html"
from htpy import p, section

section("#main-section.hero.is-link")[
    p(".subtitle.is-3.is-spaced")["Welcome"]
]
```



## Template interpolation to f-strings

You might have some templates laying around after using jinja or some other templating language.

`html2htpy` will try to convert the `template {{ variables }}`... 

...to pythonic f-strings: `f"template { variables }"` 

Note that other template template syntax, such as loops `{% for x in y %}` can not be transformed at 
this time, so you will often have to clean up a bit after `html2htpy` is done with its thing.

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

