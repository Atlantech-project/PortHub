"""Rebuild every ATLANTECH logo variant with clean transparency.

Sources (Visual Identity folder):
  Logo.png                  full-colour lockup, real alpha but white-fringed edges
  Logo_only.png             symbol, real alpha
  logo_textpng.png          wordmark + tagline, real alpha
  Logo_monochrome_dark.png  dark mono lockup on a baked white background
  Logo_monochrome_light.png light mono lockup on a baked navy background
"""
import sys, os
import numpy as np
from PIL import Image

SRC = sys.argv[1]
OUT = sys.argv[2]
os.makedirs(OUT, exist_ok=True)

NAVY = np.array([0x08, 0x3A, 0x4F])
GOLD = np.array([0xA5, 0x8D, 0x66])
LTEAL = np.array([0xC0, 0xD5, 0xD6])
MTEAL = np.array([0x40, 0x7E, 0x8C])
OFFW = np.array([0xE5, 0xE1, 0xDD])
WHITE = np.array([255, 255, 255])


def load(name):
    return np.array(Image.open(os.path.join(SRC, name)).convert('RGBA')).astype(np.float32)


def defringe(a, iters=8):
    """Replace RGB of semi-transparent pixels with the average of nearby solid ink,
    so edges carry no white halo. Alpha is left untouched."""
    rgb, al = a[..., :3].copy(), a[..., 3]
    known = al >= 250
    for _ in range(iters):
        acc = np.zeros_like(rgb); cnt = np.zeros(al.shape, np.float32)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                k = np.roll(np.roll(known, dy, 0), dx, 1)
                acc += np.roll(np.roll(rgb, dy, 0), dx, 1) * k[..., None]
                cnt += k
        grow = (~known) & (cnt > 0)
        rgb[grow] = acc[grow] / cnt[grow][:, None]
        known = known | grow
    out = a.copy(); out[..., :3] = rgb
    return out


def key_mono(a, ink_color):
    """Turn a mono logo on a flat baked background into ink + alpha."""
    rgb = a[..., :3]
    h, w = rgb.shape[:2]
    border = np.concatenate([rgb[:8].reshape(-1, 3), rgb[-8:].reshape(-1, 3),
                             rgb[:, :8].reshape(-1, 3), rgb[:, -8:].reshape(-1, 3)])
    bg = np.median(border, 0)
    d = np.linalg.norm(rgb - bg, axis=-1)
    lo = np.percentile(np.linalg.norm(border - bg, axis=-1), 99.5) + 4
    hi = np.percentile(d[d > lo * 3], 60) if (d > lo * 3).any() else d.max()
    alpha = np.clip((d - lo) / (hi * 0.85 - lo), 0, 1)
    out = np.zeros((h, w, 4), np.float32)
    out[..., :3] = ink_color
    out[..., 3] = alpha * 255
    return out


def recolor_dark(a):
    """Full-colour version for dark backgrounds: navy inks become light, teal and gold stay."""
    if a.shape[0] > 256:
        return np.concatenate([recolor_dark(a[y:y + 256]) for y in range(0, a.shape[0], 256)])
    rgb = a[..., :3]
    # ink centroids measured from Logo.png -> their replacements
    pairs = [
        ((0x18, 0x3C, 0x54), OFFW),            # A and wordmark (darkest navy)
        ((0x18, 0x3C, 0x48), OFFW),
        ((0x0C, 0x30, 0x3C), OFFW),
        ((0x18, 0x48, 0x54), OFFW),            # hull: same ink as the A in practice
        ((0x24, 0x54, 0x60), (0x9F, 0xBF, 0xC4)),
        ((0x18, 0x78, 0x84), (0x2F, 0x9C, 0xAD)),  # teal wave, lifted a touch for dark grounds
        ((0x54, 0x90, 0x9C), (0x7F, 0xB4, 0xBF)),
        ((0xA8, 0x84, 0x60), (0xB9, 0x9C, 0x70)),  # gold, a touch brighter
        ((0x9C, 0x84, 0x54), (0xB9, 0x9C, 0x70)),
    ]
    old = np.array([p[0] for p in pairs], np.float32)
    new = np.array([p[1] for p in pairs], np.float32)
    d = np.linalg.norm(rgb[..., None, :] - old, axis=-1)          # H W K
    wts = np.exp(-(d / 10.0) ** 2)
    wts /= wts.sum(-1, keepdims=True) + 1e-6
    # inks close to a centroid snap to the flat target (removes source grain);
    # blends between inks keep a proportional shift so boundaries stay smooth
    snap = np.clip(2.0 - d.min(-1) / 15.0, 0, 1)[..., None]
    shifted = rgb + (wts[..., None] * (new - old)).sum(-2)
    flat = (wts[..., None] * new).sum(-2)
    out = a.copy()
    out[..., :3] = np.clip(snap * flat + (1 - snap) * shifted, 0, 255)
    return out


def recolor_solid(a, color):
    out = a.copy(); out[..., :3] = color
    return out


def trim(a, pad_ratio=0.04, thr=8):
    m = a[..., 3] > thr
    ys, xs = np.where(m)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    c = a[y0:y1, x0:x1]
    p = int(round(max(c.shape[:2]) * pad_ratio))
    out = np.zeros((c.shape[0] + 2 * p, c.shape[1] + 2 * p, 4), np.float32)
    out[p:p + c.shape[0], p:p + c.shape[1]] = c
    out[..., 3][out[..., 3] <= thr] = 0
    return out


def split_lockup(a):
    """Split a lockup into symbol (top) and wordmark + tagline (bottom) at the first
    clear row band below the symbol."""
    rows = (a[..., 3] > 8).any(1)
    ys = np.where(rows)[0]
    min_gap = max(4, int(a.shape[0] * 0.01))
    start = None
    for y in range(ys.min(), ys.max()):
        if not rows[y]:
            start = y if start is None else start
        elif start is not None:
            if y - start >= min_gap:
                cut = (start + y) // 2
                return a[:cut], a[cut:]
            start = None
    raise ValueError('no gap between symbol and wordmark')


def save(a, name):
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA').save(os.path.join(OUT, name), optimize=True)


def shrink(a, width=1600):
    """Trim, then downscale so the longest side is at most `width` (PIL resizes RGBA premultiplied)."""
    a = trim(a, 0)
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
    im.thumbnail((width, width), Image.Resampling.LANCZOS)
    return np.array(im).astype(np.float32)


lockup = shrink(defringe(load('Logo.png')))
symbol = shrink(defringe(load('Logo_only.png')))
wordmark = shrink(defringe(load('logo_textpng.png')))
mono_src = load('Logo_monochrome_dark.png')

variants = {}
for shape, img in [('lockup', lockup), ('symbol', symbol), ('wordmark', wordmark)]:
    variants[(shape, 'color')] = img
    variants[(shape, 'reversed')] = recolor_dark(img)

# Mono: key the designer's mono lockup so internal gaps (containers, hull vs. wave) survive.
mono_alpha = key_mono(mono_src, NAVY)
m_sym, m_word = split_lockup(trim(mono_alpha, 0))
for shape, img in [('lockup', mono_alpha), ('symbol', m_sym), ('wordmark', m_word)]:
    variants[(shape, 'mono-navy')] = recolor_solid(img, NAVY)
    variants[(shape, 'mono-white')] = recolor_solid(img, WHITE)

for (shape, tone), img in variants.items():
    save(trim(img), f'atlantech-{shape}-{tone}.png')
print('\n'.join(sorted(os.listdir(OUT))))
