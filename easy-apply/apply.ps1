#requires -version 3
# 기렌의 야망 (SS) 한글패치 v1.0.1 적용 엔진
# 이 스크립트는 "한글패치 적용하기.bat" 이 자동으로 실행합니다.
# (직접 실행하려면 원본 Track 1 .bin 을 인자로 넘기거나 같은 폴더에 두세요.)

$ErrorActionPreference = 'Stop'

$root   = $PSScriptRoot
$xdelta = Join-Path $root 'xdelta.exe'
$patch  = Join-Path $root 'gihren-no-yabou-ss-korean-v1.0.1.xdelta'

$T1NAME  = 'Kidou Senshi Gundam - Gihren no Yabou (Japan) (Track 1).bin'
$OUTNAME = 'Kidou Senshi Gundam - Gihren no Yabou Korean v1.0.1 (Track 1).bin'
$CUENAME = 'Kidou Senshi Gundam - Gihren no Yabou Korean v1.0.1.cue'

$EXP_SRC   = 'a27adec617d05787bbf6fd440176b71cc303d2edb40f1b5527bedbf044de7899'
$EXP_OUT   = '831d4a50cdc4eb121fd04595494777bf9ed20426e9cc1b55d8a5c58570fc6dc4'
$EXP_PATCH = '7ee1611a76de9315928adc6e3168bf22f689d91e1b4c9b610751e808b49924b9'
$EXP_TRK2  = 'e0975d00e307925b56cbee433c7844edc90f17fe3cf8bd4057ec4788a858a3ec'

function Get-Sha256([string]$p) {
    return (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLower()
}
function Close-Window([int]$code) {
    Write-Host ''
    Write-Host '  이 창을 닫으려면 아무 키나 누르세요...' -ForegroundColor DarkGray
    exit $code
}
function Fail([string]$msg) {
    Write-Host ''
    Write-Host "  [오류] $msg" -ForegroundColor Red
    Close-Window 1
}

try {
    Write-Host ''
    Write-Host '============================================================'
    Write-Host '   기렌의 야망 (SS) 한글패치 v1.0.1'
    Write-Host '============================================================'
    Write-Host ''

    if (-not (Test-Path -LiteralPath $xdelta)) { Fail "xdelta.exe 가 없습니다. 압축을 푼 폴더의 파일을 모두 한곳에 두세요." }
    if (-not (Test-Path -LiteralPath $patch))  { Fail "gihren-no-yabou-ss-korean-v1.0.1.xdelta 가 없습니다." }

    # --- 원본 Track 1 찾기: 드래그앤드롭 인자 > 스크립트 폴더 > 현재 폴더 ---
    $src = $null
    if ($args.Count -ge 1 -and $args[0] -and (Test-Path -LiteralPath $args[0])) {
        $src = (Resolve-Path -LiteralPath $args[0]).Path
    }
    elseif (Test-Path -LiteralPath (Join-Path $root $T1NAME)) {
        $src = (Resolve-Path -LiteralPath (Join-Path $root $T1NAME)).Path
    }
    elseif (Test-Path -LiteralPath (Join-Path (Get-Location).Path $T1NAME)) {
        $src = (Resolve-Path -LiteralPath (Join-Path (Get-Location).Path $T1NAME)).Path
    }
    if (-not $src) {
        Write-Host "  원본 게임 파일을 찾을 수 없습니다:" -ForegroundColor Yellow
        Write-Host "     $T1NAME"
        Write-Host ''
        Write-Host "   방법 1) 원본 Track 1, Track 2 를 이 폴더에 복사한 뒤 다시 실행"
        Write-Host "   방법 2) 원본 Track 1 .bin 을 '한글패치 적용하기.bat' 아이콘 위로 끌어다 놓기"
        Close-Window 1
    }

    $srcdir = Split-Path -Parent $src
    $out = Join-Path $srcdir $OUTNAME
    $cue = Join-Path $srcdir $CUENAME

    Write-Host "  원본: $src"
    Write-Host ''
    Write-Host '  [1/5] 패치 파일 검증...'
    if ((Get-Sha256 $patch) -ne $EXP_PATCH) { Fail "패치 파일이 손상되었습니다. 다시 내려받으세요." }

    Write-Host '  [2/5] 원본 디스크 검증... (수십 초 걸립니다)'
    $sh = Get-Sha256 $src
    if ($sh -ne $EXP_SRC) {
        Fail ("지원하지 않는 원본입니다 (SHA-256 불일치).`n" +
              "         일본판 기동전사 건담 기렌의 야망(T-13327G)을 2352바이트 raw 로 뜬`n" +
              "         Track 1 .bin 이 맞는지 확인하세요.`n" +
              "         현재값: $sh")
    }

    Write-Host '  [3/5] 오디오 트랙 확인...'
    $t2 = $null
    foreach ($cand in @(Get-ChildItem -LiteralPath $srcdir -Filter '*Track 2*.bin' -File -ErrorAction SilentlyContinue)) {
        if ((Get-Sha256 $cand.FullName) -eq $EXP_TRK2) { $t2 = $cand.Name; break }
    }
    if (-not $t2) {
        Write-Host '        원본 Track 2 를 찾지 못했습니다. 음악이 나오지 않을 수 있습니다.' -ForegroundColor Yellow
        $t2 = 'Kidou Senshi Gundam - Gihren no Yabou (Japan) (Track 2).bin'
    } else {
        Write-Host "        $t2"
    }

    $needPatch = $true
    if (Test-Path -LiteralPath $out) {
        if ((Get-Sha256 $out) -eq $EXP_OUT) {
            Write-Host '  이미 패치가 적용되어 있습니다. CUE 파일만 새로 만듭니다.'
            $needPatch = $false
        } else {
            Remove-Item -LiteralPath $out -Force
        }
    }

    if ($needPatch) {
        Write-Host '  [4/5] 한글패치 적용 중... (1~2분 소요, 원본보다 약 3.0MB 커집니다)'
        & $xdelta -d -f -s $src $patch $out
        if ($LASTEXITCODE -ne 0) {
            if (Test-Path -LiteralPath $out) { Remove-Item -LiteralPath $out -Force }
            Fail "xdelta 적용이 실패했습니다 (종료 코드 $LASTEXITCODE)."
        }
        Write-Host '  [5/5] 결과 검증...'
        $oh = Get-Sha256 $out
        if ($oh -ne $EXP_OUT) {
            Remove-Item -LiteralPath $out -Force
            Fail ("결과 검증 실패 (SHA-256 불일치). 출력 파일을 삭제했습니다.`n         현재값: $oh")
        }
    }

    $cueLines = @(
        ('FILE "{0}" BINARY' -f $OUTNAME),
        '  TRACK 01 MODE1/2352',
        '    INDEX 01 00:00:00',
        ('FILE "{0}" BINARY' -f $t2),
        '  TRACK 02 AUDIO',
        '    INDEX 00 00:00:00',
        '    INDEX 01 00:02:00'
    )
    Set-Content -LiteralPath $cue -Value $cueLines -Encoding ascii

    Write-Host ''
    Write-Host '============================================================' -ForegroundColor Green
    Write-Host '   완료되었습니다!' -ForegroundColor Green
    Write-Host '============================================================' -ForegroundColor Green
    Write-Host ''
    Write-Host '  새턴 에뮬레이터(Ymir, Mednafen, SSF 등)에서 아래 CUE 파일을 여세요:'
    Write-Host ''
    Write-Host "     $cue" -ForegroundColor Cyan
    Write-Host ''
    Write-Host '  * 원본 파일은 그대로 보존됩니다.'
    Write-Host '  * 반드시 .cue 파일로 여세요 (.bin 을 직접 열지 마세요).'
    Close-Window 0
}
catch {
    Fail $_.Exception.Message
}
