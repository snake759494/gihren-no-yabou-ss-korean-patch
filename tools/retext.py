"""Replace a Japanese text label inside a palettized UI image with Korean text.
Background is rebuilt row by row from the pixels left/right of the text box, the original text's
fill and outline colours are sampled, and the result is quantized back to the image's own palette."""
import struct, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def palette(data):
    n = struct.unpack_from('>H', data, 2)[0]
    v = struct.unpack_from('>%dH' % n, data, 4)
    return np.array([[(c & 31) * 8, ((c >> 5) & 31) * 8, ((c >> 10) & 31) * 8] for c in v], np.float32)


def decode(data):
    w, h = struct.unpack_from('>HH', data, 0); px = data[4:]
    if len(px) >= w * h:
        return np.frombuffer(px[:w * h], np.uint8).reshape(h, w).copy(), 8
    x = np.frombuffer(px[:w * h // 2], np.uint8)
    a = np.empty(w * h, np.uint8); a[0::2] = x >> 4; a[1::2] = x & 15
    return a.reshape(h, w), 4


def encode(a, bpp, tail=b''):
    h, w = a.shape
    if bpp == 8:
        body = a.astype(np.uint8).tobytes()
    else:
        f = a.reshape(-1).astype(np.uint8); body = bytes((f[0::2] << 4) | f[1::2])
    return struct.pack('>HH', w, h) + body + tail


def _mask(text, font, w, h, x, y):
    S = 4
    big = Image.new('L', (w * S, h * S), 0)
    fb = ImageFont.truetype(font.path, font.size * S)
    ImageDraw.Draw(big).text((x * S, y * S), text, font=fb, fill=255)
    return np.asarray(big.resize((w, h), Image.LANCZOS), np.float32) / 255


def retext(data, pal, box, text, fontfile, size, align='left', outline=True, shrink_to_fit=True, glow=False, xoff=0, rowmode=None, textset=(1,2,3,12,13), ink=None):
    a, bpp = decode(data)
    h, w = a.shape
    x0, y0, x1, y1 = box
    x1 = min(x1, w - 1); y1 = min(y1, h - 1)
    if rowmode: rowmode = (rowmode[0], min(rowmode[1], w - 1))
    rgb = pal[a]
    # --- background: per row linear blend between the columns just outside the box
    bg = rgb.copy()
    L = max(0, x0 - 1); R = min(w - 1, x1 + 1)
    R = R if R > x1 else x1
    for y in range(y0, y1 + 1):
        cl, cr = rgb[y, L], rgb[y, R]
        for x in range(x0, x1 + 1):
            t = (x - L) / max(1, (R - L))
            bg[y, x] = cl * (1 - t) + cr * t
    if rowmode:
        bx0, bx1 = rowmode
        for y in range(y0, y1 + 1):
            for p in (0, 1):
                xs = [x for x in range(bx0, bx1 + 1) if x % 2 == p and a[y, x] not in textset]
                if not xs:
                    continue
                vals, cnt = np.unique(a[y, xs], return_counts=True)
                v = vals[cnt.argmax()]
                for x in range(x0, x1 + 1):
                    if x % 2 == p and bx0 <= x <= bx1:
                        bg[y, x] = pal[v]
    # --- sample original text colours: bright core, dark outline, mid glow
    diff = np.abs(rgb - bg).sum(2)
    m = np.zeros((h, w), bool); m[y0:y1 + 1, x0:x1 + 1] = diff[y0:y1 + 1, x0:x1 + 1] > 60
    sel = rgb[m] if m.any() else rgb[y0:y1 + 1, x0:x1 + 1].reshape(-1, 3)
    lum = sel @ np.array([0.3, 0.59, 0.11])
    o = np.argsort(lum)
    n = len(o)
    edge_c = np.median(sel[o[:max(1, n // 4)]], 0)
    core_c = np.median(sel[o[-max(1, n // 4):]], 0)
    glow_c = np.median(sel[o[n // 3: 2 * n // 3]], 0) if n > 3 else core_c
    if ink == 'dark': core_c = edge_c
    # --- render Korean
    font = ImageFont.truetype(os.path.join(ROOT, fontfile), size)
    while shrink_to_fit and font.getlength(text) + xoff > (x1 - x0 + 1) - 4 and size > 8:
        size -= 1; font = ImageFont.truetype(os.path.join(ROOT, fontfile), size)
    tw = font.getlength(text)
    asc, desc = font.getmetrics()
    bb = font.getbbox(text)
    ty = y0 + ((y1 - y0 + 1) - (bb[3] - bb[1])) / 2 - bb[1]
    tx = x0 + 1 + xoff if align == 'left' else x0 + ((x1 - x0 + 1) - tw) / 2
    al = _mask(text, font, w, h, tx, ty)
    out = bg.copy()
    if glow:
        gl = np.zeros_like(al)
        for dy in (-2, -1, 0, 1, 2):
            for dx in (-2, -1, 0, 1, 2):
                gl = np.maximum(gl, np.roll(np.roll(al, dy, 0), dx, 1) * (0.55 if abs(dy) + abs(dx) > 2 else 0.8))
        out = out * (1 - gl[..., None]) + glow_c * gl[..., None]
    if outline:
        ol = np.zeros_like(al)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                ol = np.maximum(ol, np.roll(np.roll(al, dy, 0), dx, 1))
        out = out * (1 - ol[..., None]) + edge_c * ol[..., None]
    out = out * (1 - al[..., None]) + core_c * al[..., None]
    # --- quantize inside the box only, to colours the original image already uses
    used = np.unique(a)
    up = pal[used]
    res = a.copy()
    region = out[y0:y1 + 1, x0:x1 + 1].reshape(-1, 3)
    d = ((region[:, None, :] - up[None, :, :]) ** 2).sum(2)
    res[y0:y1 + 1, x0:x1 + 1] = used[d.argmin(1)].reshape(y1 - y0 + 1, x1 - x0 + 1)
    w0, h0 = struct.unpack_from('>HH', data, 0)
    nbytes = w0 * h0 if bpp == 8 else w0 * h0 // 2
    return encode(res, bpp, data[4 + nbytes:]), res

