# Changelog

## next
- Implement `Element.__html__`. This avoids double escaping when passed to
`markupsafe.escape` and Django's `django.utils.html.conditional_escape`. [PR #65](https://github.com/pelme/htpy/pull/65).
- Raise errors directly on invalid children. This avoids cryptic stack traces.
[PR #56](https://github.com/pelme/htpy/pull/56).
- Raise TypeError rather than ValueError when invalid types are passed as
attributes or children. [PR #59].

## 24.9.1 - 2024-09-09
- Raise errors directly on invalid attributes. This avoids cryptic stack traces
  for invalid attributes. [Issue #49](https://github.com/pelme/htpy/issues/49)
  [PR #55](https://github.com/pelme/htpy/pull/55).

## 24.8.3 - 2024-08-28
- Support passing htpy elements directly to Starlette responses. Document Starlette support. [PR #50](https://github.com/pelme/htpy/pull/50).
- Allow passing ints to attributes and children [PR #52](https://github.com/pelme/htpy/pull/52).

## 24.8.2 - 2024-08-23
- Added support for passing data between components via Context. See the [Usage
docs](usage.md#passing-data-with-context) for more information. [PR #48](https://github.com/pelme/htpy/pull/48).
- Added Django template backend. The Django template backend allows you to
integrate htpy components directly with Django. [See the docs for more information](django.md#the-htpy-template-backend). [PR #37](https://github.com/pelme/htpy/pull/37).

## 24.8.1 - 2024-08-16
 - Added the `comment()` function to render HTML comments.
 [Documentation](usage.md#html-comments) /  [Issue
 #42](https://github.com/pelme/htpy/issues/42).
 - Run tests on Python 3.13 RC (no changes were required, earlier versions
 should work fine too). [PR #45](https://github.com/pelme/htpy/pull/45).
 - Attributes that are not strings will now be rejected runtime. Attributes have
 been typed as strings previously but this is now also enforced during runtime.
 If you need to pass non-strings as attribute values, wrap them in str() calls.

## 24.8.0 - 2024-08-03
- Allow conditional rendering based on `bool`. [PR #40](https://github.com/pelme/htpy/pull/41).

For previous versions and changes, please see the [git commit
history](https://github.com/pelme/htpy/commits/main/?since=2023-10-19&until=2024-07-17).
