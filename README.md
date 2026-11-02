# 기동전사 건담 기렌의 야망 (세가새턴) 한글패치

세가새턴 게임 **기동전사 건담 기렌의 야망**(機動戦士ガンダム ギレンの野望, T-13327G)의 비공식 한국어 번역 패치입니다.
번역 데이터와 빌드 도구를 담고 있습니다.

> **게임 데이터는 이 저장소에 없습니다.** 배포물은 원본 디스크에 적용하는 xdelta 바이너리 패치뿐입니다.
> 본인이 소유한 디스크에서 직접 추출한 이미지가 필요합니다.

현재 최신 릴리스는 **v1.0.1** 입니다. 자세한 내용은 [docs/RELEASE_NOTES_v1.0.1.md](docs/RELEASE_NOTES_v1.0.1.md)에 있습니다.

---

## 무엇이 한글화되었나

| 영역 | 상태 |
|---|---|
| 이벤트 대사 *(그림 글자)* | 3,661줄 |
| 도움말·메시지 창 *(그림 글자)* | 132개 |
| 메뉴·명령·보고·병기·인물·거점 이름 | 전체 (게임 내 한글 글꼴 추가) |
| 인물·병기 이름판 *(그림)* | 269개 |
| 병기 백과 | 122개 |
| 전략 화면 라벨·버튼 *(그림)* | 전체 |
| 페이즈 제목 *(그림)* | 5개 |
| 전체 맵 틀·생산 도크 화면 *(그림)* | 전체 |
| 세이브(백업 RAM) 안내 | 전체 |
| 이벤트 동영상 | 한글 자막 321개 추가 |

이 게임은 대사와 라벨 대부분이 문자 코드가 아니라 미리 그려 둔 그림입니다. 원본 글리프 1,490개를 판독표로 읽어
원문을 복원한 뒤 직접 번역했고, 원본 서체와 가까운 나눔스퀘어 네오·서울한강체로 다시 그려 넣었습니다.
아주 작은 글자에만 [Galmuri](https://quiple.dev/font/galmuri)를 썼습니다. 외부 기계번역은 쓰지 않았습니다.

---

## 패치 적용 방법

### 준비물

- 정품 **기동전사 건담 기렌의 야망**(T-13327G) 디스크를 **2352바이트 raw(MODE1/2352)** 로 추출한 `.bin` 2개
- 세가새턴 에뮬레이터 (Ymir, Mednafen, SSF 등)와 새턴 BIOS

`.iso`(2048바이트)나 압축 포맷(`.chd` 등)은 그대로 쓸 수 없습니다. `.chd` 는 `chdman extractcd` 로 `.bin`/`.cue` 를 먼저 만드세요.

### 원본 확인값

**Track 1 (데이터) — 615,675,984 바이트**

| 알고리즘 | 값 |
|---|---|
| MD5 | `fc48c74b24dfa90a6880b4e98d63df2c` |
| SHA-1 | `55e4a390c1a7fb1cb9ca6e4715d9a5b4a5697b19` |
| SHA-256 | `a27adec617d05787bbf6fd440176b71cc303d2edb40f1b5527bedbf044de7899` |
| CRC32 | `481741EB` |

**Track 2 (오디오) — 14,819,952 바이트** · 패치가 건드리지 않습니다

| 알고리즘 | 값 |
|---|---|
| MD5 | `fe74ef222abf7ccec7a83bc00a3c597d` |
| SHA-1 | `23c4b793f5c40c2ad7a1e3eddf25a04445f6ff6b` |
| SHA-256 | `e0975d00e307925b56cbee433c7844edc90f17fe3cf8bd4057ec4788a858a3ec` |
| CRC32 | `51F07B75` |

### 방법 1 — 간편 적용 (Windows, 권장)

1. 릴리스에서 `gihren-no-yabou-ss-korean-v1.0.1-easy-apply.zip` 을 받아 압축을 풉니다.
2. 원본 `.bin` 2개를 압축 푼 폴더에 복사합니다.
3. **`한글패치 적용하기.bat`** 을 더블클릭합니다.
4. 원본 검증 → 패치 → 결과 검증이 자동으로 진행됩니다(1~2분).
5. 같은 폴더에 생긴 **`.cue`** 파일을 에뮬레이터에서 엽니다.

원본 `.bin` 을 `.bat` 아이콘 위로 끌어다 놓아도 됩니다.

### 방법 2 — xdelta 직접 실행

```bash
xdelta3 -d -s "Kidou Senshi Gundam - Gihren no Yabou (Japan) (Track 1).bin" \
        gihren-no-yabou-ss-korean-v1.0.1.xdelta \
        "Kidou Senshi Gundam - Gihren no Yabou Korean v1.0.1 (Track 1).bin"
```

그 다음 아래 내용으로 `.cue` 파일을 만듭니다. Track 2 파일명은 실제 파일명과 같아야 합니다.

```
FILE "Kidou Senshi Gundam - Gihren no Yabou Korean v1.0.1 (Track 1).bin" BINARY
  TRACK 01 MODE1/2352
    INDEX 01 00:00:00
FILE "Kidou Senshi Gundam - Gihren no Yabou (Japan) (Track 2).bin" BINARY
  TRACK 02 AUDIO
    INDEX 00 00:00:00
    INDEX 01 00:02:00
```

### 결과 확인값

패치된 Track 1 은 원본보다 **3,179,904 바이트 큽니다.** 한글 그림 글자와 자막 데이터가 늘어 일부 파일을 디스크 뒤쪽으로 옮겼기 때문이며, 정상입니다.

**패치 결과 Track 1 — 618,855,888 바이트**

| 알고리즘 | 값 |
|---|---|
| MD5 | `40fe91c743d7c254f560165bdb5275df` |
| SHA-1 | `fed813fcffbfd6fa091efb42cc7434cffaeac086` |
| SHA-256 | `831d4a50cdc4eb121fd04595494777bf9ed20426e9cc1b55d8a5c58570fc6dc4` |
| CRC32 | `E12765FF` |

**패치 파일 `gihren-no-yabou-ss-korean-v1.0.1.xdelta` — 8,387,758 바이트 (무압축)**

| 알고리즘 | 값 |
|---|---|
| SHA-256 | `7ee1611a76de9315928adc6e3168bf22f689d91e1b4c9b610751e808b49924b9` |

### 문제 해결

| 증상 | 원인과 해결 |
|---|---|
| `지원하지 않는 원본입니다 (SHA-256 불일치)` | 다른 판이거나 2048바이트 덤프입니다. 2352바이트 raw 로 다시 추출하세요. |
| 음악이 안 나온다 | `.bin` 을 직접 열었거나 Track 2 가 `.cue` 와 다른 폴더에 있습니다. |
| 글자가 깨진다 | 패치가 덜 적용된 이미지입니다. 결과 SHA-256 을 확인하세요. |
| xdelta 가 `XD3_INVALID_INPUT` 을 낸다 | 원본이 아닌 파일에 적용했거나 패치 파일이 손상됐습니다. |

---

## 직접 빌드하기

[BUILD.md](BUILD.md) 를 보세요.

## 저장소 구성

```
tools/          빌드 도구 (MFD/LZ 재패킹, 그림 글자 렌더링, ISO 재구성, 검증용 에뮬레이터 래퍼)
data/           번역 데이터 (대사·도움말·이름·백과·UI·자막·글꼴 문자열), 글리프 판독표, 용어집
font/           Galmuri (SIL OFL 1.1)
easy-apply/     릴리스 zip 에 들어가는 간편 적용 스크립트
docs/           릴리스 노트, 작업 기록
release/        릴리스별 SHA256SUMS
```

## 권리 관계

- 이 프로젝트는 **비공식 비상업 팬 번역**이며, 반다이·세가 및 그 밖의 권리자와 아무 관계가 없습니다.
- 게임 디스크 이미지, BIOS, 에뮬레이터, `xdelta.exe` 는 이 저장소에 포함되지 않습니다.
- `font/` 의 Galmuri 글꼴은 quiple 의 저작물이며 SIL Open Font License 1.1 을 따릅니다([`LICENSES/Galmuri-OFL-1.1.txt`](LICENSES/Galmuri-OFL-1.1.txt)).
- 그 밖의 고지는 [NOTICE.md](NOTICE.md) 를 보세요.
