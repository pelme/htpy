
# The html2htpy CLI tool

The `html2htpy` command converts HTML code to htpy Python code.

Looking to convert existing HTML? See the [Convert HTML to htpy guide](../how-to/convert-html.md).

```
usage: html2htpy [-h] [-f {auto,ruff,black,none}] [-i {yes,h,no}] [--no-shorthand] [input]

positional arguments:
  input                 Input HTML file, e.g. home.html. Optional. If not specified, html2htpy will read from stdin.

options:
  -h, --help            show this help message and exit
  -f, --format {auto,ruff,black,none}

                        Format the output code with a code formatter.

                        auto (default):
                          - If black is installed (exists on PATH), use `black` for formatting.
                          - If ruff is installed (exists on PATH): Use `ruff format` for formatting.
                          - If neither black or ruff is installed, do not perform any formatting.

                        black:
                          Use the black formatter (https://black.readthedocs.io/en/stable/).

                        ruff:
                          Use the ruff formatter (https://docs.astral.sh/ruff/formatter/).

                        none:
                          Do not format the output code at all.
  -i, --imports {yes,h,no}

                        Specify formatting for imports.

                        yes (default):
                            Add `from htpy import div, span` for all found elements.
                        h:
                            Add a single `import htpy as h`.
                            Reference elements with `h.div`, `h.span`.
                        no:
                            Do not add imports.
  --no-shorthand        Use explicit `id` and `class_` kwargs instead of the shorthand #id.class syntax.
```

## Import Options

You have a couple of options regarding imports with the `-i`/`--imports` flag.
Options are `yes` (default), `h`, `no`.

#### Module import of htpy: `--imports=h`

This mode will use `import htpy as h` instead of importing individual elements from htpy.

```py title="$ html2htpy --imports=h example.html"
import htpy as h

h.section("#main-section.hero.is-link")[
    h.p(".subtitle.is-3.is-spaced")["Welcome"]
]
```

## id/classes conversion

html2htpy supports multiple modes to handle id/class conversions:

```html title="example.html"
<section id="main-section" class="hero is-link">
  <p class="subtitle is-3 is-spaced">Welcome</p>
</section>
```

### Shorthand
By default, id/classes will be converted to the shorthand notation:

```py title="$ html2htpy example.html"
from htpy import p, section

section("#main-section.hero.is-link")[
    p(".subtitle.is-3.is-spaced")["Welcome"]
]
```

### Explicit id/class attributes

Use the `--no-shorthand` flag to get explicit `id` and `class_` asttributes:

```py title="$ html2htpy --no-shorthand example.html"
from htpy import p, section

section(id="main-section", class_="hero is-link")[
    p(class_="subtitle is-3 is-spaced")["Welcome"]
]
```

## Django/Jinja variable conversion

`html2htpy` will convert Django/Jinja-style template variables to f-strings:

```
$ echo '<div>hi {{ name }}!</div>' | html2htpy

from htpy import div

div[f"hi { name }!"]
```
