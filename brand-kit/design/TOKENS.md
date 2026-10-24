# ATLANTECH token reference

_Generated from `tokens/atlantech.tokens.json` by `tools/build_design_assets.py`. Do not edit by hand._

Use the **Figma name** in your files and handoff notes. Developers have the same token under the names on the right.

## Colour

| Figma name | Light | Dark | Web (CSS) | Flutter | Use |
|---|---|---|---|---|---|
| `color/bg` | `#F7F5F2` | `#04222F` | `--atl-bg` | `context.atl.bg` | Page background (paper) |
| `color/surface` | `#FFFFFF` | `#072B3A` | `--atl-surface` | `context.atl.surface` | Cards, inputs |
| `color/surface-2` | `#F2EFEB` | `#0B3446` | `--atl-surface-2` | `context.atl.surface2` | Raised or grouped areas |
| `color/surface-3` | `#E5E1DD` (Off-White) | `#103D51` | `--atl-surface-3` | `context.atl.surface3` | Strongest neutral fill |
| `color/text` | `#0F2A36` | `#E5E1DD` (Off-White) | `--atl-text` | `context.atl.text` | Body and headings (ink) |
| `color/text-muted` | `#4B5F68` | `#A9BEC3` | `--atl-text-muted` | `context.atl.textMuted` | Metadata, helper text |
| `color/border` | `#D3DEDF` | `#1E4A5B` | `--atl-border` | `context.atl.border` |  |
| `color/border-strong` | `#8FA3AA` | `#5F7F89` | `--atl-border-strong` | `context.atl.borderStrong` | Input outlines, outlined buttons |
| `color/primary` | `#083A4F` (Deep Navy) | `#C0D5D6` (Light Teal) | `--atl-primary` | `context.atl.primary` | Main buttons, key actions |
| `color/on-primary` | `#E5E1DD` (Off-White) | `#083A4F` (Deep Navy) | `--atl-on-primary` | `context.atl.onPrimary` |  |
| `color/primary-soft` | `#C0D5D6` (Light Teal) | `#1C5466` | `--atl-primary-soft` | `context.atl.primarySoft` | Selected states, soft fills |
| `color/accent` | `#A58D66` (Muted Gold) | `#C2A77B` | `--atl-accent` | `context.atl.accent` | Decoration only |
| `color/accent-text` | `#7A6440` | `#C2A77B` | `--atl-accent-text` | `context.atl.accentText` | Gold when it must be text |
| `color/link` | `#407E8C` (Mid Teal) | `#7FB4BF` | `--atl-link` | `context.atl.link` |  |
| `color/focus` | `#407E8C` (Mid Teal) | `#7FB4BF` | `--atl-focus` | `context.atl.focus` |  |
| `color/header-bg` | `#083A4F` (Deep Navy) | `#0B3446` | `--atl-header-bg` | `context.atl.headerBg` |  |
| `color/header-text` | `#E5E1DD` (Off-White) | `#E5E1DD` (Off-White) | `--atl-header-text` | `context.atl.headerText` |  |
| `color/success` | `#2E7D5B` | `#7CC9A4` | `--atl-success` | `context.atl.success` |  |
| `color/warning` | `#8A5C0F` | `#E3B766` | `--atl-warning` | `context.atl.warning` |  |
| `color/danger` | `#B3412F` | `#F2A493` | `--atl-danger` | `context.atl.danger` |  |
| `color/logo-card` | `transparent` | `#F7F5F2` | `--atl-logo-card` | `context.atl.logoCard` | No card behind the primary logo in light mode |

## Brand palette

Identity colours. Use them through the colour tokens above in UI; use them directly only in brand artwork.

| Figma name | Value | Use |
|---|---|---|
| `palette/deep-navy` | `#083A4F` | Identity. Trust, stability. Primary brand colour. |
| `palette/muted-gold` | `#A58D66` | Identity. Value, progress. Accents and dividers; 2.9:1 on paper, so not for text. |
| `palette/light-teal` | `#C0D5D6` | Identity. Clarity, balance. Soft fills, selected states. |
| `palette/mid-teal` | `#407E8C` | Identity. Innovation, growth. Links and focus; 4.2:1 on paper, so 18px+ or underlined. |
| `palette/off-white` | `#E5E1DD` | Identity. Simplicity, focus. Text on navy, quiet backgrounds. |

## Type

| Figma text style | Font | Weight | Size / line height | Letter spacing |
|---|---|---|---|---|
| `type/display-large` | Montserrat | 700 | 57px / 64px | -0.25px |
| `type/display-medium` | Montserrat | 700 | 45px / 52px | 0px |
| `type/display-small` | Montserrat | 600 | 36px / 44px | 0px |
| `type/headline-large` | Montserrat | 600 | 32px / 40px | 0px |
| `type/headline-medium` | Montserrat | 600 | 28px / 36px | 0px |
| `type/headline-small` | Montserrat | 600 | 24px / 32px | 0px |
| `type/title-large` | Montserrat | 600 | 22px / 28px | 0px |
| `type/title-medium` | Inter | 600 | 16px / 24px | 0.1px |
| `type/title-small` | Inter | 600 | 14px / 20px | 0.1px |
| `type/body-large` | Inter | 400 | 16px / 24px | 0.15px |
| `type/body-medium` | Inter | 400 | 14px / 20px | 0.25px |
| `type/body-small` | Inter | 400 | 12px / 16px | 0.4px |
| `type/label-large` | Inter | 600 | 14px / 20px | 0.1px |
| `type/label-medium` | Inter | 500 | 12px / 16px | 0.5px |
| `type/label-small` | Inter | 500 | 11px / 16px | 0.5px |

## Radius and spacing

| Figma name | Value | Use |
|---|---|---|
| `radius/sm` | 8px | Chips, small controls |
| `radius/md` | 12px | Buttons, inputs, default |
| `radius/lg` | 16px | Cards, sheets |
| `space/1` | 4px | |
| `space/2` | 8px | |
| `space/3` | 12px | |
| `space/4` | 16px | |
| `space/6` | 24px | |
| `space/8` | 32px | |
| `space/12` | 48px | |
