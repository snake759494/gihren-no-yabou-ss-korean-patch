"""릴리스 자산 생성: xdelta(무압축), 간편 적용 zip, SHA256SUMS.

py -3.14 tools/make_release.py --version v1.0.0 --src "...(Japan) (Track 1).bin" \
    --dst "...(Korean) (Track 1).bin" --xdelta xdelta.exe [--bundle-xdelta xdelta.exe]
"""
import argparse, hashlib, os, subprocess, zipfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 24), b''): h.update(b)
    return h.hexdigest()

def main():
    a = argparse.ArgumentParser()
    a.add_argument('--version', required=True); a.add_argument('--src', required=True)
    a.add_argument('--dst', required=True); a.add_argument('--xdelta', required=True)
    a.add_argument('--bundle-xdelta')
    o = a.parse_args()
    out = os.path.join(REPO, 'release'); os.makedirs(out, exist_ok=True)
    name = f'gihren-no-yabou-ss-korean-{o.version}'
    xd = os.path.join(out, name + '.xdelta')
    subprocess.check_call([o.xdelta, '-e', '-f', '-0', '-S', 'none', '-s', o.src, o.dst, xd])
    zp = os.path.join(out, name + '-easy-apply.zip')
    with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
        ea = os.path.join(REPO, 'easy-apply')
        for f in sorted(os.listdir(ea)):
            if f != 'README.md': z.write(os.path.join(ea, f), f'{name}/{f}')
        z.write(xd, f'{name}/{name}.xdelta')
        if o.bundle_xdelta: z.write(o.bundle_xdelta, f'{name}/xdelta.exe')
    rows = [(sha(p), os.path.basename(p)) for p in (xd, zp)]
    rows += [(sha(o.src), '원본 ' + os.path.basename(o.src)), (sha(o.dst), '결과 ' + os.path.basename(o.dst))]
    with open(os.path.join(out, f'SHA256SUMS_{o.version}.txt'), 'w', encoding='utf-8', newline='\n') as f:
        for h, n in rows: f.write(f'{h}  {n}\n')
    for h, n in rows: print(h, n)

if __name__ == '__main__':
    main()
