# Changelog

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
