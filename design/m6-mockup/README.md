# M6 mockup (design reference only)

These are the approved mockup screens from 1 Nov 2026, saved so a Muse can read them. They are **a picture of the look, not code to copy and not a spec**. The M6 spec (`plan/milestones/M6-app.md`) and master-plan section 7 win wherever they differ.

| File | What it shows |
|---|---|
| `platform.html` | The platform's guided journey (computer side): Welcome, Connect, Questions, Your phone, Services, Research, Build, Boot, Done |
| `computer-side-phone-page.html` | The phone's page as seen on the computer: Files and Assistant tabs, sidebar with the logo and the connection line |
| `phone-home.html` | The phone's own controls-only home screen and service screens |
| `logo-light.png` | The logo mark (light version, 12 KB). The only brand element. |

## What to take from it
- **Colours:** background `#06080F`, panels `rgba(15,22,40,.85)` with `#1E2638` borders, text `#E6EAF2`, muted text `#A7B0C4` and `#8A94AB`, teal accent `#5EEAD4`, indigo accent `#818CF8` (teal-to-indigo gradient on main buttons and progress bars), warning amber `#F2B66D`.
- **Shapes:** rounded corners (12 to 20 px), soft radial glows in the background, a faint 40 px grid on the platform, buttons at least 44 px tall.
- **Motion:** short fade-and-rise on new content, pulsing dots while waiting, growing progress bars. All motion stops under `prefers-reduced-motion`.
- **Type:** the mockup loads Space Grotesk and JetBrains Mono from Google Fonts. The product may not load anything from outside hosts (its Content-Security-Policy forbids it), so use `system-ui` and `ui-monospace` unless the font files are already in the repo.
- **Layout:** one step per screen with a step rail, short plain sentences, warnings in amber boxes.

## What NOT to take from it
- The mockup's runtime (`support.js`, `<x-dc>`, `sc-if`, `data-props`) is the mockup tool's, not ours. Write plain HTML, CSS and JavaScript.
- Example numbers, file names, the "1.1 GB model in the image" step, Wi-Fi pairing, budget wording, updates and reboot buttons are mockup-era. The spec decides: the model goes on after boot (M4 v2.3), there is no money or budget tracking (M4c v2.5), cable first and Wi-Fi out of scope (M6 section 4), no updater or privileged reboot (M6 section 3).
- The words "spare" in example text are ordinary English, not the dropped product name.
