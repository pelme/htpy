# Changelog

## 25.5.1 - 2025-05-30
- Split source code into multiple private modules. See PR #119.
  Thanks to [Stein Magnus Jodal (@jodal)](https://github.com/jodal).
- Add `@with_children` decorator to help creating custom components that get passed children in the same way as regular HTML elements.
  See PR #113.
  [Read the docs for more details](common-patterns.md#components-with-children).
  Thanks to [Stein Magnus Jodal (@jodal)](https://github.com/jodal).

## 25.5.0 - 2025-05-25
- Allow multiple attribute dictionaries when defining `Elements`.
  PR #117.
  Thanks to [Chase Sterling (@gazpachoking)](https://github.com/gazpachoking).

## 25.4.2 - 2025-04-16
- Fix import of `@deprecated()` annotation on Python >= 3.13. It is part of the `warnings` module, not the `typing` module.
  Fixes #106. PR #107.
  Thanks to [Stein Magnus Jodal (@jodal)](https://github.com/jodal).

## 25.4.1 - 2025-04-12
- Add the `Renderable` protocol, a consistent API to render an `htpy` object as HTML or to iterate over it. `Element`, `Fragment`, `ContextProvider`, and `ContextConsumer` are all `Renderable`.
  PR #92.
  Thanks to [Stein Magnus Jodal (@jodal)](https://github.com/jodal) and [Dave Peck (@davepeck)](https://github.com/davepeck).
- Deprecate `render_node()` and `iter_node()` and direct iteration over elements. Call `Renderable.__str__()` or `Renderable.iter_chunks()` instead.
  Read the [Usage docs](usage.md#renderable) for more details.

## 25.4.0 - 2025-04-10
- Make `Context`'s repr debug friendly PR #96.
  Thanks to [Stein Magnus Jodal (@jodal)](https://github.com/jodal)).
- Strip whitespace around id and class values in CSS selector.
  Fixes #97. PR #100.
  Thanks to [William Jackson (@williamjacksn)](https://github.com/williamjacksn).

## 25.3.0 - 2025-03-16
- Add `fragment` for explicitly grouping a collection of nodes.
  [Read the Usage docs for more details](usage.md#fragments).
  Fixes #82. PRs #86 and #95.
  Thanks to [Thomas Scholtes (@geigerzaehler)](https://github.com/geigerzaehler).

## 25.2.0 - 2025-02-01
- Context providers longer require wrapping nodes in a function/lambda. This
simplifies context usage while still being backward compatible.
  PR #83.
  Thanks to [Thomas Scholtes (@geigerzaehler)](https://github.com/geigerzaehler) for the patch.

## 25.1.0 - 2025-01-27
- Adjust typing for attributes: Allow Mapping instead of just dict.
  PR #80.
  Thanks to [David Svenson (@Majsvaffla)](https://github.com/Majsvaffla) for the initial report+patch.

## 24.12.0 - 2024-12-15
- Fixed handling of non-generator iterators such as `itertools.chain()` as children.
  PR #72.
  Thanks to [Aleksei Pirogov (@astynax)](https://github.com/astynax).

## 24.10.1 - 2024-10-24
- Fix handling of Python keywords such as `<del>` in html2htpy.
  PR #61.

## 24.10.0 - 2024-10-23
- Implement `Element.__html__`. This avoids double escaping when passed to `markupsafe.escape` and Django's `django.utils.html.conditional_escape`.
  PR #65.
- Raise errors directly on invalid children. This avoids cryptic stack traces.
  PR #56.
- Raise TypeError rather than ValueError when invalid types are passed as attributes or children.
  PR #59.

## 24.9.1 - 2024-09-09
- Raise errors directly on invalid attributes. This avoids cryptic stack traces for invalid attributes.
  Fixes #49. PR #55.

## 24.8.3 - 2024-08-28
- Support passing htpy elements directly to Starlette responses. Document Starlette support.
  PR #50.
- Allow passing ints to attributes and children.
  PR #52.

## 24.8.2 - 2024-08-23
- Added support for passing data between components via `Context`.
  See the [Usage docs](usage.md#passing-data-with-context) for more information.
  PR #48.
- Added Django template backend. The Django template backend allows you to integrate htpy components directly with Django.
  [See the docs for more information](django.md#the-htpy-template-backend).
  PR #37.

## 24.8.1 - 2024-08-16
 - Added the `comment()` function to render HTML comments.
   See the [documentation](usage.md#html-comments).
   Fixes #42.
 - Run tests on Python 3.13 RC. No changes were required, earlier versions should work fine too.
   PR #45.
 - Attributes that are not strings will now be rejected runtime. Attributes have been typed as strings previously but this is now also enforced during runtime. If you need to pass non-strings as attribute values, wrap them in `str()` calls.

## 24.8.0 - 2024-08-03
- Allow conditional rendering based on `bool`.
  Fixes #40. PR #41.

For earlier versions and changes, please see the [git commit
history](https://github.com/pelme/htpy/commits/main/?since=2023-10-19&until=2024-07-17).
