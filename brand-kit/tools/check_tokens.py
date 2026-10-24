"""Check that the design tokens and the code agree.

Run from the brand-kit folder before sending a new version to anyone:

    python tools/check_tokens.py

Compares design/tokens/atlantech.tokens.json against
  web/brand/css/tokens.css      (every colour, light and dark)
  web/brand/tokens.js           (palette, light, dark)
  flutter/lib/brand/*.dart      (palette and the type scale)
and exits non-zero on any mismatch.
"""
import json, os, re, sys

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def read(*p):
    with open(os.path.join(KIT, *p), encoding='utf-8') as f:
        return f.read()

tokens = json.loads(read('design', 'tokens', 'atlantech.tokens.json'))
problems = []


def resolve(value, sets):
    """Follow {palette.deep-navy}-style aliases through the given token sets."""
    m = re.fullmatch(r'\{(.+)\}', str(value))
    if not m:
        return value
    node = None
    for s in sets:
        node = s
        for part in m.group(1).split('.'):
            node = node.get(part) if isinstance(node, dict) else None
        if node is not None:
            break
    if node is None:
        problems.append(f'unresolved alias {value}')
        return value
    return resolve(node['$value'], sets)


def hexnorm(v):
    v = str(v).strip().lower()
    return '#00000000' if v == 'transparent' else v


def colours(mode):
    sets = [tokens['palette'], tokens['base'], tokens[mode]]
    return {k: hexnorm(resolve(t['$value'], sets)) for k, t in tokens[mode]['color'].items()}


def compare(where, expected, actual):
    for k, v in expected.items():
        if k not in actual:
            problems.append(f'{where}: missing {k}')
        elif hexnorm(actual[k]) != v:
            problems.append(f'{where}: {k} is {actual[k]}, tokens.json says {v}')


palette = {k: hexnorm(t['$value']) for k, t in tokens['palette']['palette'].items()}
light, dark = colours('light'), colours('dark')

# --- CSS ------------------------------------------------------------------
css = read('web', 'brand', 'css', 'tokens.css')
blocks = {
    'light': css.split('@media')[0],
    'dark (data-theme)': css.split(':root[data-theme="dark"]')[1].split('}')[0],
    'dark (prefers-color-scheme)': css.split('@media (prefers-color-scheme: dark)')[1].split('}\n}')[0],
}
for name, block in blocks.items():
    found = dict(re.findall(r'--atl-([\w-]+):\s*([^;]+);', block))
    expected = light if name == 'light' else dark
    compare(f'tokens.css {name}', expected, found)
    if name == 'light':
        compare('tokens.css palette', palette, found)

# --- JS -------------------------------------------------------------------
js = read('web', 'brand', 'tokens.js')
camel = lambda s: re.sub(r'-(\w)', lambda m: m.group(1).upper(), s)
for name, expected in [('palette', palette), ('light', light), ('dark', dark)]:
    m = re.search(rf'export const {name} = Object\.freeze\(\{{(.*?)\}}\)', js, re.S)
    if not m:
        problems.append(f'tokens.js: no export {name}')
        continue
    body = m.group(1)
    found = {k: v for k, v in re.findall(r"(\w+):\s*'(#[0-9A-Fa-f]{6})'", body)}
    present = {camel(k): v for k, v in expected.items() if camel(k) in found}
    compare(f'tokens.js {name}', present, {k: v.lower() for k, v in found.items()})

# --- Flutter ----------------------------------------------------------------
dart_colours = dict(re.findall(r'static const (\w+) = Color\(0xFF([0-9A-Fa-f]{6})\)', read('flutter', 'lib', 'brand', 'atlantech_colors.dart')))
compare('atlantech_colors.dart palette', palette,
        {re.sub(r'([A-Z])', lambda m: '-' + m.group(1).lower(), k): '#' + v.lower() for k, v in dart_colours.items()})

dart_tokens = read('flutter', 'lib', 'brand', 'atlantech_tokens.dart')
for mode, expected in [('light', light), ('dark', dark)]:
    m = re.search(rf'static const {mode} = AtlantechTokens\((.*?)\n  \);', dart_tokens, re.S)
    if not m:
        problems.append(f'atlantech_tokens.dart: no {mode} tokens')
        continue
    found = {}
    for k, argb in re.findall(r'(\w+): Color\(0x([0-9A-Fa-f]{8})\)', m.group(1)):
        argb = argb.lower()
        found[k] = '#' + argb[2:] if argb[:2] == 'ff' else '#' + argb[2:] + argb[:2]
    compare(f'atlantech_tokens.dart {mode}', {camel(k): v for k, v in expected.items()}, found)

theme = read('flutter', 'lib', 'brand', 'atlantech_theme.dart')
weights = {v['$value']: k for k, v in tokens['base']['weight'].items()}
for name, t in tokens['base']['type'].items():
    v = t['$value']
    dart_name = camel(name)
    m = re.search(rf'{dart_name}: [db]\((\d+(?:\.\d+)?), FontWeight\.w(\d+), (\d+(?:\.\d+)?)(?:, (-?[\d.]+))?\)', theme)
    if not m:
        problems.append(f'atlantech_theme.dart: no {dart_name}')
        continue
    size, weight, height, ls = m.groups()
    want_weight = int(resolve(v['fontWeight'], [tokens['base']]))
    checks = [
        ('fontSize', float(size), float(v['fontSize'].rstrip('px'))),
        ('fontWeight', int(weight), want_weight),
        ('lineHeight', float(height), float(v['lineHeight'].rstrip('px'))),
        ('letterSpacing', float(ls or 0), float(v['letterSpacing'].rstrip('px'))),
    ]
    for field, got, want in checks:
        if got != want:
            problems.append(f'atlantech_theme.dart {dart_name}.{field} is {got}, tokens.json says {want}')

if problems:
    print('Out of sync:')
    for p in problems:
        print('  -', p)
    sys.exit(1)
print(f'All in sync: {len(palette)} palette colours, {len(light)} light and {len(dark)} dark colours, '
      f'{len(tokens["base"]["type"])} type styles.')
