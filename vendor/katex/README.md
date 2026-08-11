# Vendored KaTeX

This directory contains the browser files needed to render mathematics locally
with KaTeX 0.17.0:

- `katex.min.css`;
- `katex.min.js`;
- `contrib/auto-render.min.js`; and
- the font files referenced by the stylesheet.

The files were taken from the official `katex.zip` release archive:

```text
https://github.com/KaTeX/KaTeX/releases/download/v0.17.0/katex.zip
SHA-256: 8199fe2230362f2933fbaa26d34a18cdf491a9c8c6822c07e46cb4f00028fded
```

KaTeX is distributed under the MIT licence included in `LICENSE`.

The shared configuration in `../../app.js` recognises `\(...\)` for inline
mathematics and `\[...\]` for displayed mathematics. Delimiters inside
`pre`, `code`, `script`, `style`, `textarea`, and `option` elements are ignored.
