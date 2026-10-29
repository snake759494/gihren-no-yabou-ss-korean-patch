import struct

PAD2 = bytes(2)


def _items(src):
    """greedy+lazy LZ parse -> list of items: ('L',2bytes) ('M',len,off) ('R',n)"""
    n = len(src); i = 0; items = []
    head = {}; prev = [-1] * n

    def ins(p):
        if p + 3 <= n:
            k = src[p:p + 3]; prev[p] = head.get(k, -1); head[k] = p

    def best(p):
        bl = 0; bo = 0
        if p + 3 > n:
            return 0, 0
        c = head.get(src[p:p + 3], -1); tries = 0
        while c >= 0 and p - c <= 4095 and tries < 64:
            l = 0; mx = min(17, n - p)
            while l < mx and src[c + l] == src[p + l]:
                l += 1
            if l > bl:
                bl, bo = l, p - c
            if bl == 17:
                break
            c = prev[c]; tries += 1
        return bl, bo

    while i < n:
        if i > 0:
            r = 0
            while i + r < n and src[i + r] == src[i - 1] and r < 4098:
                r += 1
            if r >= 18:
                items.append(('R', r))
                for p in range(i, i + r):
                    ins(p)
                i += r
                continue
        l, o = best(i)
        if l >= 3:
            l2, _ = best(i + 1) if i + 1 < n else (0, 0)
            if l2 > l + 1 and i + 2 <= n:
                items.append(('L', src[i:i + 2])); ins(i); ins(i + 1); i += 2
                continue
            items.append(('M', l, o))
            for p in range(i, i + l):
                ins(p)
            i += l
        else:
            if i + 2 <= n:
                items.append(('L', src[i:i + 2])); ins(i); ins(i + 1); i += 2
            else:
                # single trailing byte: literal with a pad byte, trimmed by the trailer
                items.append(('L', src[i:i + 1] + bytes(1))); i += 1
    return items


def _emit(grp):
    flags = 0; body = bytearray()
    for j, it in enumerate(grp):
        if it[0] == 'L':
            flags |= 1 << j; body += it[1]
        elif it[0] == 'M':
            l, o = it[1], it[2]; body += bytes([((l - 2) << 4) | (o >> 8), o & 255])
        else:
            r = it[1] - 3; body += bytes([r >> 8, r & 255])
    return struct.pack('>H', flags) + body


def compress(src):
    """Returns (stream_without_header, full_group_count, 0) in the game's exact layout:
    full 16-item groups, trailer [trim][rem+1 or 0], then (if rem) a final group + 2 pad bytes."""
    src = bytes(src)
    items = _items(src)
    produced = sum(2 if it[0] == 'L' else (it[1] if it[0] == 'M' else it[1]) for it in items)
    trim = produced - len(src)
    assert 0 <= trim <= 1
    full = len(items) // 16; rem = len(items) % 16
    out = bytearray()
    for k in range(full):
        out += _emit(items[k * 16:(k + 1) * 16])
    out += bytes([trim, rem + 1 if rem else 0])
    if rem:
        out += _emit(items[full * 16:]) + PAD2
    return bytes(out), full, 0


def _items_b(src):
    """parse for the byte-mode variant: refs len 3..16 (1 byte) or 17..272 (long form)."""
    n = len(src); i = 0; items = []
    head = {}; prev = [-1] * n

    def ins(p):
        if p + 3 <= n:
            k = src[p:p + 3]; prev[p] = head.get(k, -1); head[k] = p

    def best(p):
        bl = 0; bo = 0
        if p + 3 > n:
            return 0, 0
        c = head.get(src[p:p + 3], -1); tries = 0
        while c >= 0 and p - c <= 4095 and tries < 64:
            l = 0; mx = min(272, n - p)
            while l < mx and src[c + l] == src[p + l]:
                l += 1
            if l > bl:
                bl, bo = l, p - c
            if bl == 272:
                break
            c = prev[c]; tries += 1
        return bl, bo

    while i < n:
        if i > 0:
            r = 0
            while i + r < n and src[i + r] == src[i - 1] and r < 4098:
                r += 1
            if r >= 18:
                items.append(('R', r))
                for p in range(i, i + r):
                    ins(p)
                i += r
                continue
        l, o = best(i)
        if l >= 3:
            items.append(('M', l, o))
            for p in range(i, i + l):
                ins(p)
            i += l
        elif i + 2 <= n:
            items.append(('L', src[i:i + 2])); ins(i); ins(i + 1); i += 2
        else:
            items.append(('L', src[i:i + 1] + bytes(1))); i += 1
    return items


def _emit_b(grp):
    flags = 0; body = bytearray()
    for j, it in enumerate(grp):
        if it[0] == 'L':
            flags |= 1 << j; body += it[1]
        elif it[0] == 'M':
            l, o = it[1], it[2]
            if l <= 16:
                body += bytes([((l - 1) << 4) | (o >> 8), o & 255])
            else:
                body += bytes([0x10 | (o >> 8), o & 255, l - 17])
        else:
            r = it[1] - 3; body += bytes([r >> 8, r & 255])
    return struct.pack('>H', flags) + body


def compress_b(src):
    src = bytes(src)
    items = _items_b(src)
    produced = sum(2 if it[0] == 'L' else it[1] for it in items)
    trim = produced - len(src)
    full = len(items) // 16; rem = len(items) % 16
    out = bytearray()
    for k in range(full):
        out += _emit_b(items[k * 16:(k + 1) * 16])
    out += bytes([trim, rem + 1 if rem else 0])
    if rem:
        out += _emit_b(items[full * 16:]) + PAD2
    return bytes(out), full, 0
