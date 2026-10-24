"""Build the designer-only assets in design/ from the tokens file.

    python tools/build_design_assets.py

Writes
  design/swatches/atlantech.ase           Adobe swatch exchange (Illustrator, Photoshop, InDesign)
  design/swatches/atlantech-palette.png   palette sheet to drop into Figma or slides
"""
import json, os, struct
from PIL import Image, ImageDraw, ImageFont

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(KIT, 'design', 'swatches')
os.makedirs(OUT, exist_ok=True)

with open(os.path.join(KIT, 'design', 'tokens', 'atlantech.tokens.json'), encoding='utf-8') as f:
    tokens = json.load(f)
palette = {k: t['$value'] for k, t in tokens['palette']['palette'].items()}
title = lambda k: k.replace('-', ' ').title().replace('Off White', 'Off-White')


def rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# ---- ASE ---------------------------------------------------------------------
def ase_block(name, hexv):
    n = (name + '\0').encode('utf-16-be')
    body = struct.pack('>H', len(n) // 2) + n + b'RGB ' + struct.pack('>3f', *[c / 255 for c in rgb(hexv)]) + struct.pack('>H', 0)
    return struct.pack('>HI', 0x0001, len(body)) + body


def ase_group(name, start):
    n = (name + '\0').encode('utf-16-be')
    if not start:
        return struct.pack('>HI', 0xC002, 0)
    body = struct.pack('>H', len(n) // 2) + n
    return struct.pack('>HI', 0xC001, len(body)) + body


blocks = [ase_group('ATLANTECH', True)]
blocks += [ase_block(f'ATLANTECH {title(k)}', v) for k, v in palette.items()]
blocks.append(ase_group('ATLANTECH', False))
with open(os.path.join(OUT, 'atlantech.ase'), 'wb') as f:
    f.write(b'ASEF' + struct.pack('>HHI', 1, 0, len(blocks)) + b''.join(blocks))


# ---- Palette sheet -----------------------------------------------------------
def font(size, bold=False):
    fam = 'Montserrat-SemiBold.ttf' if bold else 'Inter-Regular.ttf'
    return ImageFont.truetype(os.path.join(KIT, 'flutter', 'fonts', fam), size)


W, H, pad, gap = 2000, 900, 100, 36
sw = (W - 2 * pad - gap * 4) // 5
sheet = Image.new('RGB', (W, H), '#F7F5F2')
d = ImageDraw.Draw(sheet)
d.text((pad, 80), 'ATLANTECH COLOUR PALETTE', font=font(34, True), fill='#083A4F')
d.line([(pad, 140), (W - pad, 140)], fill='#A58D66', width=3)
notes = {
    'deep-navy': 'Trust, stability',
    'muted-gold': 'Value, progress',
    'light-teal': 'Clarity, balance',
    'mid-teal': 'Innovation, growth',
    'off-white': 'Simplicity, focus',
}
for i, (k, v) in enumerate(palette.items()):
    x = pad + i * (sw + gap)
    d.rounded_rectangle([x, 200, x + sw, 560], radius=24, fill=v, outline='#D3D0CB' if k == 'off-white' else None, width=2)
    r, g, b = rgb(v)
    d.text((x, 600), title(k).upper(), font=font(26, True), fill='#083A4F')
    d.text((x, 646), v.upper(), font=font(26), fill='#4B5F68')
    d.text((x, 688), f'RGB {r} {g} {b}', font=font(22), fill='#4B5F68')
    d.text((x, 760), notes[k], font=font(22), fill='#7A6440')
sheet.save(os.path.join(OUT, 'atlantech-palette.png'), optimize=True)


# ---- TOKENS.md: the reference table, generated so it never drifts ----------
def resolve(v, mode):
    if isinstance(v, str) and v.startswith('{'):
        group, name = v.strip('{}').split('.')
        src = tokens['palette'] if group == 'palette' else tokens[mode]
        return resolve(src[group][name]['$value'], mode)[0], name
    return v, None


def cell(v, mode):
    value, alias = resolve(v, mode)
    value = 'transparent' if value.upper() == '#00000000' else value.upper()
    return f'`{value}` ({title(alias)})' if alias else f'`{value}`'


camel = lambda s: s.split('-')[0] + ''.join(p.title() for p in s.split('-')[1:])
lines = [
    '# ATLANTECH token reference',
    '',
    '_Generated from `tokens/atlantech.tokens.json` by `tools/build_design_assets.py`. Do not edit by hand._',
    '',
    'Use the **Figma name** in your files and handoff notes. Developers have the same token under the names on the right.',
    '',
    '## Colour',
    '',
    '| Figma name | Light | Dark | Web (CSS) | Flutter | Use |',
    '|---|---|---|---|---|---|',
]
for name, t in tokens['light']['color'].items():
    dark_t = tokens['dark']['color'][name]
    use = t.get('$description') or dark_t.get('$description', '')
    lines.append(f'| `color/{name}` | {cell(t["$value"], "light")} | {cell(dark_t["$value"], "dark")} '
                 f'| `--atl-{name}` | `context.atl.{camel(name)}` | {use} |')

lines += ['', '## Brand palette', '', 'Identity colours. Use them through the colour tokens above in UI; use them directly only in brand artwork.', '',
          '| Figma name | Value | Use |', '|---|---|---|']
for name, t in tokens['palette']['palette'].items():
    lines.append(f'| `palette/{name}` | `{t["$value"]}` | {t["$description"]} |')

lines += ['', '## Type', '', '| Figma text style | Font | Weight | Size / line height | Letter spacing |', '|---|---|---|---|---|']
for name, t in tokens['base']['type'].items():
    v = t['$value']
    fam = tokens['base']['font'][v['fontFamily'].strip('{}').split('.')[1]]['$value']
    wt = tokens['base']['weight'][v['fontWeight'].strip('{}').split('.')[1]]['$value']
    lines.append(f'| `type/{name}` | {fam} | {wt} | {v["fontSize"]} / {v["lineHeight"]} | {v["letterSpacing"]} |')

lines += ['', '## Radius and spacing', '', '| Figma name | Value | Use |', '|---|---|---|']
for name, t in tokens['base']['radius'].items():
    lines.append(f'| `radius/{name}` | {t["$value"]} | {t.get("$description", "")} |')
for name, t in tokens['base']['space'].items():
    lines.append(f'| `space/{name}` | {t["$value"]} | |')

with open(os.path.join(KIT, 'design', 'TOKENS.md'), 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(lines) + '\n')

print('wrote', ', '.join(sorted(os.listdir(OUT))), 'and TOKENS.md')
