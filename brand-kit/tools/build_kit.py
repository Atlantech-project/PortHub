"""Assemble the ATLANTECH brand kit (logos, Flutter assets, web assets, fonts)."""
import sys, os, shutil
from PIL import Image, ImageDraw
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

LOGOS, FONTS, KIT = sys.argv[1], sys.argv[2], sys.argv[3]
NAVY = (0x08, 0x3A, 0x4F, 255)
OFFW = (0xE5, 0xE1, 0xDD, 255)

def mk(*p):
    path = os.path.join(KIT, *p); os.makedirs(path, exist_ok=True); return path

def logo(name):
    return Image.open(os.path.join(LOGOS, f'atlantech-{name}.png')).convert('RGBA')

def fit(im, w=None, h=None):
    im = im.copy()
    if w and not h: h = round(im.height * w / im.width)
    if h and not w: w = round(im.width * h / im.height)
    return im.resize((w, h), Image.Resampling.LANCZOS)

def on_tile(sym, size, bg, scale, radius=0.0):
    """Symbol centred on a square tile; radius is a fraction of size (0 = square)."""
    tile = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(tile).rounded_rectangle([0, 0, size - 1, size - 1], radius=int(size * radius), fill=bg)
    s = sym.copy(); s.thumbnail((int(size * scale), int(size * scale)), Image.Resampling.LANCZOS)
    tile.alpha_composite(s, ((size - s.width) // 2, (size - s.height) // 2))
    return tile

def save(im, *p):
    im.save(os.path.join(mk(*p[:-1]), p[-1]), optimize=True)

# only clear generated output; hand-written code (lib/, css/, *.vue, README) is kept
for gen in [('logos',), ('flutter', 'assets'), ('flutter', 'fonts'),
            ('web', 'brand', 'logos'), ('web', 'brand', 'fonts')]:
    shutil.rmtree(os.path.join(KIT, *gen), ignore_errors=True)
for f in ('favicon.ico', 'favicon-32.png', 'apple-touch-icon.png', 'icon-192.png', 'icon-512.png', 'icon-maskable-512.png'):
    p = os.path.join(KIT, 'web', 'brand', 'icons', f)
    if os.path.exists(p):
        os.remove(p)

# ---- master logos -------------------------------------------------------
for f in os.listdir(LOGOS):
    shutil.copy(os.path.join(LOGOS, f), mk('logos'))

shapes = {'lockup': 240, 'symbol': 120, 'wordmark': 280}   # logical width in Flutter
tones = ['color', 'reversed', 'mono-navy', 'mono-white']

# ---- Flutter: resolution-aware logo assets ------------------------------
for shape, w in shapes.items():
    for tone in tones:
        src = logo(f'{shape}-{tone}')
        name = f'{shape}_{tone.replace("-", "_")}.png'
        save(fit(src, w), 'flutter', 'assets', 'brand', name)
        save(fit(src, w * 2), 'flutter', 'assets', 'brand', '2.0x', name)
        save(fit(src, w * 3), 'flutter', 'assets', 'brand', '3.0x', name)

sym_rev = logo('symbol-reversed')
sym_col = logo('symbol-color')
# launcher icon: full-bleed square (iOS rounds it itself), plus Android adaptive layers
save(on_tile(sym_rev, 1024, NAVY, 0.70), 'flutter', 'assets', 'brand', 'launcher', 'app_icon.png')
save(on_tile(sym_rev, 1024, (0, 0, 0, 0), 0.56), 'flutter', 'assets', 'brand', 'launcher', 'app_icon_foreground.png')
save(on_tile(sym_rev, 1152, (0, 0, 0, 0), 0.62), 'flutter', 'assets', 'brand', 'launcher', 'splash_dark.png')
save(on_tile(sym_col, 1152, (0, 0, 0, 0), 0.62), 'flutter', 'assets', 'brand', 'launcher', 'splash_light.png')

# ---- Web -----------------------------------------------------------------
for shape in shapes:
    for tone in tones:
        save(fit(logo(f'{shape}-{tone}'), 1200 if shape != 'symbol' else 640),
             'web', 'brand', 'logos', f'atlantech-{shape}-{tone}.png')
favicon = [on_tile(sym_rev, s, NAVY, 0.80, 0.22) for s in (16, 32, 48)]
big = on_tile(sym_rev, 256, NAVY, 0.80, 0.22)
big.save(os.path.join(mk('web', 'brand', 'icons'), 'favicon.ico'), sizes=[(16, 16), (32, 32), (48, 48)])
save(favicon[1], 'web', 'brand', 'icons', 'favicon-32.png')
save(on_tile(sym_rev, 180, NAVY, 0.72).convert('RGB'), 'web', 'brand', 'icons', 'apple-touch-icon.png')
save(on_tile(sym_rev, 192, NAVY, 0.78, 0.22), 'web', 'brand', 'icons', 'icon-192.png')
save(on_tile(sym_rev, 512, NAVY, 0.78, 0.22), 'web', 'brand', 'icons', 'icon-512.png')
save(on_tile(sym_rev, 512, NAVY, 0.58), 'web', 'brand', 'icons', 'icon-maskable-512.png')

# ---- Fonts -----------------------------------------------------------------
weights = {400: 'Regular', 500: 'Medium', 600: 'SemiBold', 700: 'Bold'}
for fam, axes in [('Montserrat', {}), ('Inter', {'opsz': 14})]:
    var = os.path.join(FONTS, f'{fam}.ttf')
    for wt, label in weights.items():
        inst = instancer.instantiateVariableFont(TTFont(var), {'wght': wt, **axes}, updateFontNames=True)
        inst.save(os.path.join(mk('flutter', 'fonts'), f'{fam}-{label}.ttf'))
    web = TTFont(var); web.flavor = 'woff'
    web.save(os.path.join(mk('web', 'brand', 'fonts'), f'{fam}-Variable.woff'))
    for d in (('flutter', 'fonts'), ('web', 'brand', 'fonts')):
        shutil.copy(os.path.join(FONTS, f'OFL-{fam}.txt'), mk(*d))

print('brand kit rebuilt in', KIT)
