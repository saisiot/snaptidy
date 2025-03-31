# SnapTidy

<div align="center">
  
  <p align="center">
    <img src="logo.png" alt="SnapTidy logo" width="280"/>
  </p>
    
  **단 한 번의 명령으로 사진 라이브러리를 정리하세요.**
  
  [![라이선스: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
  [![Python 버전](https://img.shields.io/badge/python-3.7%2B-brightgreen)](https://www.python.org/downloads/)
  [![Homebrew](https://img.shields.io/badge/homebrew-available-orange)](https://brew.sh/)
  
</div>

## 🔍 SnapTidy란?

**SnapTidy**는 복잡한 디렉토리를 정리하고 중복 파일을 제거하는 강력한 CLI 도구입니다 - 특히 사진과 기타 미디어 파일에 특화되어 있습니다. 같은 사진을 여러 번 다운로드하거나 수십 개의 폴더에 분산된 사진들로 인해 고민이신가요? SnapTidy로 간편하게 정리하세요.

```bash
# 모든 파일을 하나의 디렉토리로 평탄화
snaptidy flatten

# 중복 사진 제거 (유사한 것도 함께!)
snaptidy dedup --sensitivity 0.9

# 촬영 날짜별로 사진 정리
snaptidy organize --date-format yearmonth
```

## ✨ 주요 기능

### 📁 디렉토리 평탄화
- 모든 하위 디렉토리의 파일을 현재 디렉토리로 이동
- 파일명 충돌을 스마트하게 자동 처리
- 복잡한 중첩 폴더 구조를 단 한 번의 명령으로 해결

### 🔍 스마트 중복 제거
- SHA256 해시 비교를 통한 정확한 중복 파일 찾기
- 크기가 조정되거나 약간 수정된 경우에도 유사한 사진 감지
- 시각적 유사성 감지를 위한 민감도 수준 조절 가능
- 항상 각 파일의 가장 높은 품질 버전 유지

### 📅 날짜 기반 정리
- EXIF 데이터 및 파일 메타데이터에서 생성 날짜 추출
- 년도 또는 년도+월별로 자동 폴더 정리
- 사진이 촬영된 시점을 기준으로 사진 컬렉션 정리

### ⚙️ 유연한 설정
- `--dry-run`으로 변경 사항을 적용하기 전에 미리보기
- 멀티스레딩 지원으로 성능 최적화
- 다양한 날짜 형식 옵션으로 맞춤형 정리

## 🚀 설치 방법

### Homebrew 사용 (권장)

```bash
brew tap yourname/tap
brew install snaptidy
```

### 소스에서 설치

```bash
git clone https://github.com/yourname/snaptidy.git
cd snaptidy
pip install .
```

## 📋 사용법

```bash
# 기본 사용법
snaptidy [명령어] [옵션]

# 도움말 보기
snaptidy --help
snaptidy [명령어] --help
```

### 기본 명령어

```bash
# 하위 디렉토리의 모든 파일을 현재 디렉토리로 평탄화
snaptidy flatten --path /path/to/folder

# 중복 파일 찾기 및 제거
snaptidy dedup --path /path/to/folder --sensitivity 0.9

# 촬영 날짜별로 파일 정리
snaptidy organize --path /path/to/folder --date-format yearmonth
```

### 옵션

| 옵션 | 설명 |
|--------|-------------|
| `--path` | 대상 디렉토리 (기본값: 현재 디렉토리) |
| `--dry-run` | 변경하지 않고 어떤 일이 일어날지 보여줌 |
| `--log` | 작업 로그를 파일에 저장 |
| `--sensitivity` | 시각적 유사성 임계값 (0.0-1.0) |
| `--threads` | 사용할 동시 스레드 수 |
| `--date-format` | 날짜별 정리 형식 (`year` 또는 `yearmonth`) |

## 📊 예시

### 정리 전:
```
Photos/
├── Download/
│   ├── IMG_0123.jpg
│   ├── IMG_0123 (1).jpg (중복)
│   └── vacation/
│       ├── IMG_0456.jpg
│       └── IMG_0789.jpg
├── Backup/
│   └── old_photos/
│       ├── IMG_0456.jpg (중복)
│       └── IMG_1010.jpg
└── IMG_2000.jpg
```

### 중복 제거 및 정리 후:
```
Photos/
├── 202101/
│   ├── IMG_0123.jpg
│   └── IMG_0789.jpg
├── 202102/
│   └── IMG_1010.jpg 
└── 202112/
    └── IMG_2000.jpg
```

## 🧩 기술 개요

SnapTidy는 Python으로 개발되었으며 다음과 같은 핵심 기술을 사용합니다:

- **파일 해싱**: 정확한 중복 검색을 위한 `hashlib`
- **이미지 분석**: 시각적 이미지 비교를 위한 `imagehash` 및 `Pillow`
- **비디오 처리**: 비디오 유사성을 위한 `opencv-python` 및 `ffmpeg`
- **메타데이터 추출**: 파일 정보 파싱을 위한 `exifread` 및 `hachoir`
- **성능 최적화**: 멀티스레딩을 위한 `concurrent.futures`

## 🤝 기여하기

기여는 언제나 환영합니다! [이슈 페이지](https://github.com/yourname/snaptidy/issues)에서 열린 작업을 확인하거나 여러분의 아이디어를 제출해 주세요.

## 📜 라이선스

SnapTidy는 MIT 라이선스 하에 제공됩니다 - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

---

<div align="center">
  <i>복잡한 사진 라이브러리를 싫어하는 사람들을 위해 ❤️로 만들었습니다</i>
</div>
