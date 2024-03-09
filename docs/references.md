# References

htpy was heavily inspired by many other libraries and articles. This page lists some of them.

## Similar libraries and tools

- [JSX/React](https://legacy.reactjs.org/docs/introducing-jsx.html) - Made writing HTML in a programming language popular.
- [pyxl](https://github.com/dropbox/pyxl), [pyxl3](https://github.com/gvanrossum/pyxl3), [pyxl4](https://github.com/pyxl4/pyxl4) - Write HTML in Python with JSX-like syntax. Not actively maintained.
- [htbuilder](https://github.com/tvst/htbuilder/) - Very similar to htpy but does not currently support automatic escaping.
- [breve](https://github.com/cwells/breve) - An early implementation of HTML in Python. Using getattr `[]` syntax for children. Not actively maintained.
- [hyperscript](https://github.com/hyperhype/hyperscript) - JavaScript library that also uses CSS selector-like syntax for specifying id and classes.
- [hyperpython](https://github.com/ejplatform/hyperpython) - A Python interpretation of hyperscript. Not actively maintained.
- [h by Adam Johnson](https://github.com/adamchainz/h) - Similar to htpy, uses call syntax (`()`) for attributes and getitem (`[]`) for children.

## Articles about HTML generation without templates
- [Jeff Atwood - You're Doing It Wrong](https://blog.codinghorror.com/youre-doing-it-wrong/) - Stack Overflow co-founder Jeff Atwood
- [Tavis Rudd - Throw out your templates](https://github.com/tavisrudd/throw_out_your_templates) - Tavis Rudd, creator of Python template language "Cheetah" argues for creating HTML without templates.
- [David Ford - 80% of my coding is doing this (or why templates are dead)](https://codeburst.io/80-of-my-coding-is-doing-this-or-why-templates-are-dead-b640fc149e22) - Discusses various techniques for rendering HTML.
