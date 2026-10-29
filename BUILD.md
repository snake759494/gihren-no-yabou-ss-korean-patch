# 빌드 방법

정품 디스크, Python 3.11+ (Pillow, numpy), SH-2 크로스 컴파일러(`sh-elf-gcc`, 한글 글꼴 코드·자막 코드용)가 필요합니다.

## 작업 폴더 구성

빌드 스크립트는 다음 구성을 가정합니다.

```
<루트>/
  Kidou Senshi Gundam - Gihren no Yabou (Japan) (Track 1).bin
  Kidou Senshi Gundam - Gihren no Yabou (Japan) (Track 2).bin
  Kidou Senshi Gundam - Gihren no Yabou (Japan).cue
  NanumSquareNeo-cBd.ttf, SeoulHangangEB.ttf 등 글꼴 (각 배포처에서 받으세요)
  work/
    tools/      ← 이 저장소의 tools/
    fonts/      ← 이 저장소의 font/
    ko/ help/ names/ hekik/ ui/ msub/ kfont/ ...   ← 이 저장소의 data/ 안의 내용
    disc/       ← 디스크에서 추출한 파일 (tools/extract.py)
```

## 순서

1. `py tools/extract.py` — Track 1 의 파일 시스템을 풀어 `work/disc/`, `files.txt`, `ip.bin` 을 만듭니다.
2. 대사 원문 복원 — `tools/scene.py` 와 `data/glyph_labels.json`(글리프 판독표)으로 `lines_ja.json` 을 만듭니다.
   원문은 게임 데이터라 저장소에 넣지 않았습니다.
3. `data/kfont/build.cmd`, `tools/build.cmd` — 한글 글꼴 코드와 자막 코드를 컴파일합니다.
4. `py tools/build.py` — 모든 파트를 넣어 `(Korean)` 이미지와 `.cue` 를 만듭니다.
   `PARTS` 환경변수로 파트를 고를 수 있습니다(기본: `scenes,help,ui,names,bram,hekik,mapframe,dock,dev,g16,kfont,msub`).
5. `py tools/make_release.py --version vX.Y.Z --src … --dst … --xdelta xdelta.exe` — 무압축 xdelta, 간편 적용 zip, SHA256SUMS 를 `release/` 에 만듭니다.

`tools/gverify.cpp` 는 화면 확인용 헤드리스 에뮬레이터 래퍼이며 빌드에는 필요하지 않습니다.
일부 확인용 스크립트(`route_*.py`, `r_*.py`, `server.py`)에는 작업 환경의 절대 경로가 남아 있습니다.
