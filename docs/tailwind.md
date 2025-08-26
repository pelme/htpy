# Usage with Tailwind CSS

## VS Code IntelliSense

Install *Tailwind CSS IntelliSense* extension.

Add this configuration to your VS Code `settings.json` to enable Tailwind IntelliSense in htpy:

```jsonc
{
    "tailwindCSS.includeLanguages": {
        "python": "html"
    },
    "tailwindCSS.experimental.classRegex": [
        // keyword‑args and helper args: class_, base_classes, error_classes, etc.
        "\\b\\w*class\\w*\\b\\s*=\\s*['\\\"]([^'\\\"]*)['\\\"]",
        // dict‑style class entries: "class": "..."
        "['\\\"]class['\\\"]\\s*:\\s*['\\\"]([^'\\\"]*)['\\\"]"
    ],
    ]
}
```

This enables autocomplete and on hover for:
- `class_="text-sm text-zinc-50"`
- `base_classes="flex gap-2"`
- `{"class": "flex gap-2"}` 