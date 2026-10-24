# ATLANTECH Design Kit

Everything you need to design ATLANTECH screens that match what the developers build, token for token.

**Brand owner:** Marwan Nabil. He created the ATLANTECH identity and maintains this kit. You design with it; changes to the brand itself go through him (see [Asking for a change](#asking-for-a-change)).

The kit version is in the zip name and in [`CHANGELOG.md`](CHANGELOG.md).

## What's in the folder

| Folder / file | What it is |
|---|---|
| `tokens/atlantech.tokens.json` | Every colour, type style, radius and spacing value, for Figma (W3C design token format) |
| `TOKENS.md` | The same tokens as a readable table, with the names developers use |
| `logos/` | 12 transparent PNG logos, 1600 px |
| `fonts/` | Montserrat and Inter. Install these before opening Figma. |
| `swatches/atlantech.ase` | The palette for Illustrator, Photoshop and InDesign |
| `swatches/atlantech-palette.png` | The palette as a sheet, for slides or a Figma cover |
| `reference/` | The kit rendered in light and dark, to compare your work against |
| `CHANGELOG.md` | What changed in each version |

## Setting up Figma

### 1. Install the fonts

Install everything in `fonts/` on your computer (on Windows: select all, then right-click > Install), then restart Figma. The files bundled in the kit are the exact versions the apps ship with.

### 2. Bring in the tokens

**With Tokens Studio (recommended).** Install the free Tokens Studio for Figma plugin, then:

1. Open the plugin, choose **Settings**, and set the token format to **W3C DTCG**.
2. Choose **Tools > Load from file** and pick `tokens/atlantech.tokens.json`.
3. You'll see four token sets (`palette`, `base`, `light`, `dark`) and two themes, **Light** and **Dark**, in the group **ATLANTECH**.
4. Choose **Styles & Variables > Export styles & variables**, select both themes, and export.

You get one variable collection, **ATLANTECH**, with a **Light** and a **Dark** mode, plus text styles named `type/...`. Switch a frame's mode to Dark and the whole design re-colours.

Some Tokens Studio features, themes among them, have moved between the free and paid plans over time. If exporting themes isn't available on your plan, use the manual route below. It takes about 20 minutes and gives the same result.

**By hand.** In Figma, create a variable collection called **ATLANTECH** with two modes, **Light** and **Dark**. Then add one colour variable per row of the colour table in `TOKENS.md`, with the same name (`color/bg`, `color/surface`, ...) and the light and dark values from the table. Add the five `palette/...` colours, and create one text style per row of the type table.

### 3. Check it

Build a quick card with `color/surface`, a `type/title-large` heading and a `color/primary` button, then compare it with `reference/specimen-light.png` and `reference/specimen-dark.png`. If it looks the same, you're set up.

## The logo

**The primary logo is the full-colour lockup:** `logos/atlantech-lockup-color.png`. Use it first. Every other file is a variation for places where the primary can't work.

| File | When to use it |
|---|---|
| `lockup-color` | **Primary.** On white, paper, off-white or light teal. |
| `lockup-color` on a paper card | On dark screens. Put the primary logo on a rounded `color/logo-card` (`#F7F5F2`) rectangle instead of swapping it for a light version. |
| `lockup-reversed` | Only when the logo must sit directly on navy or a dark surface, such as a dark app bar or splash screen. |
| `lockup-mono-navy` | Single-colour needs on light grounds: print, stamps, watermarks. |
| `lockup-mono-white` | On photos, gradients and strong colour fields. |
| `symbol-*` | App icon, favicon, compact headers, loading states. |
| `wordmark-*` | Wide, short spaces such as a top bar. |

- **Clear space:** leave empty space around the logo at least the height of the letter "A" in the wordmark.
- **Minimum size:** lockup 140 px wide, symbol 24 px.
- **Please don't** recolour it outside these tones, stretch it, add shadows, outlines or effects, rotate it, crop it, or redraw it.

## Colour, in practice

- **Always design with the `color/...` variables**, never with raw hex values. That way your screens switch to dark mode correctly and match the code exactly.
- **Muted Gold is decoration.** At 2.9:1 on light backgrounds it's not readable as text. For gold text, use `color/accent-text`.
- **Mid Teal links need help.** `color/link` is 4.2:1 on paper, so underline links or set them at 18 px or larger.
- **Success, warning and danger** are UI colours, not brand colours. Use them for status only, never in brand artwork.
- **Every text and background pair** in the token table reaches WCAG AA, as long as each colour is used for what its "Use" column says.

## Type, in practice

- **Montserrat** (`type/display-*`, `headline-*`, `title-large`): headings, screen titles and the numbers people scan for, such as berth numbers, times and counts.
- **Inter** (everything else): body text, tables, forms, labels and buttons.
- Stick to the 15 text styles. If a screen seems to need a new size, that's a request for the brand owner, not a one-off.

## Handing off to developers

Developers have every token under the same name, so annotate with names, not values:

- **Colour:** `color/surface-2`. The web developer reads it as `--atl-surface-2`, the Flutter developer as `context.atl.surface2`.
- **Type:** `type/title-large`.
- **Radius and spacing:** `radius/md`, `space/4`.

If something in a design can't be described with an existing token, flag it rather than inventing a value. That flag is exactly what the brand owner needs to hear about.

## Asking for a change

You're free to design any screen, component or layout with the kit. What stays with the brand owner is the brand itself: the logo, the palette, the fonts and the token values.

To propose a change, send Marwan:

1. **What:** the token name (new or existing), for example `color/info`.
2. **Why:** the screen or situation that needs it, ideally with a screenshot.
3. **Values:** both light and dark, with a contrast check if it's used for text.

If it's approved, the change comes back to you, and to the developers, as a new kit version. Nobody edits their own copy of the tokens.

## Getting updates

Each new version arrives as a zip named with its version number. When one arrives:

1. Read `CHANGELOG.md` to see what changed.
2. Replace your old kit folder with the new one.
3. In Tokens Studio, load the new `atlantech.tokens.json` and export again. Existing variables are updated in place, so your designs pick up the new values. If you set things up by hand, update the values listed in the changelog.
