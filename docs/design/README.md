# Pixel design language

The company's design language, as used across Pixel Inspiration tools
(frosted-glass theme, grey and crimson, adopted 25 September 2026):

- [`tokens.css`](tokens.css): colours, radii, glass effects and fonts as CSS custom properties.
- [`pixel-ui.css`](pixel-ui.css): component classes (panels, buttons, inputs,
  badges, dialogs, ...) built on those tokens.

These files are the source of truth for how Pixel Media Checker looks. The
desktop app is Tk, not a web page, so it cannot load them directly. Instead
`app/appearance.py` mirrors the tokens. [CLAUDE.md](../../CLAUDE.md#design-language)
maps every token and component to its Tk equivalent and sets the rules for
UI changes.

Copied unchanged from the company design files; update them here when the
design language changes, then bring `app/appearance.py` back in line.
