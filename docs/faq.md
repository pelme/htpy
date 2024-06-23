# FAQ

## How does htpy performance compare to Django or Jinja templates?

The performance of HTML rendering is rarely the bottleneck in most web application. It is usually fast enough regardless of what method of constructing the HTML is being used.

Given that it has been fast enough, there has not been much effort in optimizing htpy. It should be possible to significantly increase the effectiveness and we are open to contributions with benchmarks and speed improvements.

That said, htpy is currently on par with Django templates when it comes to speed. Jinja2 is currently significantly faster than both Django templates and htpy. There is a [small benchmark script](https://github.com/pelme/htpy/blob/855a2a6648ce955be9730fe030a97930df42930a/scripts/benchmark_big_table.py) in the repo that generates a table with 50 000 rows.

## Can htpy generate XML/XHTML?

No. Generating XML/XHTML is out of scope for this project. Use a XML library if
you are looking to generate XML.

htpy generates HTML, therefore "void elements" such as `<br>` does not include a trailing `/`.

If you are looking to generate generic XML, [`lxml.builder`](https://lxml.de/apidoc/lxml.builder.html) could be a good alternative.

## Does not generating HTML from Python mean mixing concerns between presentation and business logic?

With a template language, putting HTML markup in separate files is enforced by
design. Avoiding logic in the presentation layer is also mostly done by making
the language very restrictive.

It takes a little bit of planning and effort, but it is possible to have a
nicely separated presentation layer that is free from logic. See [Common
patterns](common-patterns.md) for more details on how you can structure your
project.

## What kind of black magic makes `from htpy import whatever_element` work?

htpy uses the [module level `__getattr__`](https://docs.python.org/3/reference/datamodel.html#customizing-module-attribute-access). It was [introduced in Python 3.7](https://docs.python.org/3/whatsnew/3.7.html#pep-562-customization-of-access-to-module-attributes). It allows [creating `Element` instances](https://github.com/pelme/htpy/blob/855a2a6648ce955be9730fe030a97930df42930a/htpy/__init__.py#L146-L147) for any elements that are imported.

## Why does htpy not provide HTML like tag syntax with angle brackets like pyxl and JSX?

htpy must be compatible with standard Python code formatters, editors and static
type checkers. Unfortunately, it is not possible to support those workflows with a custom
syntax without a massive effort to change those tools to support that syntax.
