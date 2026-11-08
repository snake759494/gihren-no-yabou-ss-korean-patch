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
    out += bytes([trim, rem])
    if rem:
        out += _emit(items[full * 16:])
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
    out += bytes([trim, rem])
    if rem:
        out += _emit_b(items[full * 16:])
    return bytes(out), full, 0


def _items_opt(src, tries=100000):
    """minimum-item parse (every item costs one flag bit + 2 bytes): DP over the longest match
    at each position (shorter lengths reuse the same offset), literals and runs. The decoder reads
    zeros before the start of the output, so a virtual 4095-byte zero prefix is searchable too."""
    n = len(src); Z = 4095
    buf = bytes(Z) + src; N = len(buf)
    head = {}; prev = [-1] * N
    ml = [0] * n; mo = [0] * n
    for q in range(N):
        if q + 3 > N:
            break
        k = buf[q:q + 3]
        if q >= Z:
            p = q - Z; c = head.get(k, -1); t = 0; bl = 0; bo = 0
            mx = min(17, n - p)
            while c >= Z and q - c <= 4095 and t < tries and mx >= 3:
                l = 3
                while l < mx and buf[c + l] == buf[q + l]:
                    l += 1
                if l > bl:
                    bl, bo = l, q - c
                    if bl == mx:
                        break
                c = prev[c]; t += 1
            ml[p], mo[p] = bl, bo
        prev[q] = head.get(k, -1); head[k] = q
    run = [0] * (n + 1)
    for p in range(n - 1, -1, -1):
        before = src[p - 1] if p > 0 else -1
        run[p] = run[p + 1] + 1 if src[p] == before else 0
    INF = 1 << 30
    f = [INF] * (n + 2); ch = [None] * (n + 1); f[n] = 0
    for i in range(n - 1, -1, -1):
        if i + 2 <= n:
            b = f[i + 2] + 1; c = ('L',)
        else:
            b = 1; c = ('L1',)
        for k in range(3, ml[i] + 1):
            v = f[i + k] + 1
            if v < b: b, c = v, ('M', k, mo[i])
        r = min(run[i], 4098)
        if r >= 3:
            for k in range(3, r + 1):
                v = f[i + k] + 1
                if v < b: b, c = v, ('R', k)
        f[i] = b; ch[i] = c
    items = []; i = 0
    while i < n:
        c = ch[i]
        if c[0] == 'L': items.append(('L', src[i:i + 2])); i += 2
        elif c[0] == 'L1': items.append(('L', src[i:i + 1] + bytes(1))); i += 1
        else: items.append(c); i += c[1]
    return items


def compress_opt(src):
    """same stream layout as compress(), minimum-item parse (slower; used when greedy output
    would be larger than the original file and overflow the game's load buffer)."""
    global _items
    keep = _items
    try:
        _items = _items_opt
        return compress(src)
    finally:
        _items = keep
