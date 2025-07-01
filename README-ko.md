# SnapTidy

<div align="center">
  
  <p align="center">
    <img src="logo.png" alt="SnapTidy logo" width="280"/>
  </p>

  **단 한 번의 명령으로 사진 라이브러리를 정리하세요.**
  
  [![라이선스: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
  [![Python 버전](https://img.shields.io/badge/python-3.7%2B-brightgreen)](https://www.python.org/downloads/)
  [![Homebrew](https://img.shields.io/badge/homebrew-available-orange)](https://brew.sh/)

  [🇺🇸 English](README.md) | [🇰🇷 한국어](README-ko.md)
</div>

## 🔍 SnapTidy란?

**SnapTidy**는 복잡한 디렉토리를 정리하고 중복 파일을 제거하는 강력한 CLI 및 GUI 도구입니다 - 특히 사진과 기타 미디어 파일에 특화되어 있습니다. 같은 사진을 여러 번 다운로드하거나 수십 개의 폴더에 분산된 사진들로 인해 고민이신가요? SnapTidy로 간편하게 정리하세요.

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
- **옵션: 모든 파일을 별도의 'flattened' 폴더에 복사할 수도 있음**
- 파일명 충돌을 스마트하게 자동 처리
- 복잡한 중첩 폴더 구조를 단 한 번의 명령으로 해결

#### 새로운 옵션
| 옵션        | 설명 |
|-------------|-------------|
| `--copy`    | 파일을 이동하지 않고 복사합니다. 모든 파일이 새로운 폴더(기본: `<path>/flattened`)에 복사됩니다. |
| `--output`  | 복사된 파일이 저장될 폴더 경로 (`--copy`와 함께 사용, 기본: `<path>/flattened`) |

#### 디스크 용량 안전장치
- `--copy` 옵션 사용 시, SnapTidy는 복사 전에 디스크의 남은 용량을 확인합니다. 용량이 부족하면 작업을 중단하고 경고를 출력합니다.

#### 사용 예시
```bash
# 모든 파일을 현재 디렉토리로 이동(기본)
snaptidy flatten --path /path/to/folder

# 모든 파일을 새로운 'flattened' 폴더에 복사(하드 용량이 넉넉할 때 추천)
snaptidy flatten --path /path/to/folder --copy

# 모든 파일을 지정한 폴더에 복사
snaptidy flatten --path /path/to/folder --copy --output /path/to/output_folder
```

### 🔍 스마트 중복 제거
- SHA256 해시 비교를 통한 정확한 중복 파일 찾기
- 크기가 조정되거나 약간 수정된 경우에도 유사한 사진 감지
- 시각적 유사성 감지를 위한 민감도 수준 조절 가능
- 항상 각 파일의 가장 높은 품질 버전 유지
- **새로운 기능: 중복 파일을 삭제하지 않고 폴더로 이동**

#### 중복 파일 처리 옵션
```bash
# 중복 파일 삭제 (기본)
snaptidy dedup --path /path/to/folder

# 중복 파일을 지정한 폴더로 이동
snaptidy dedup --path /path/to/folder --duplicates-folder /path/to/duplicates
```

### 📅 날짜 기반 정리
- EXIF 데이터 및 파일 메타데이터에서 생성 날짜 추출
- 년도 또는 년도+월별로 자동 폴더 정리
- 사진이 촬영된 시점을 기준으로 사진 컬렉션 정리
- **새로운 기능: 날짜 메타데이터가 없는 파일 처리**

#### 분류되지 않은 파일 처리
```bash
# 날짜 메타데이터가 없는 파일을 'unclassified' 폴더로 이동
snaptidy organize --path /path/to/folder --unclassified-folder /path/to/unclassified
```

### 🔄 복구 시스템
- **완전한 작업 로깅** CSV 파일로 전체 복구 가능
- **복구 스크립트 생성** 파일을 원래 위치로 복원
- **안전 모드** 파일 삭제를 방지하고 이동 작업만 허용
- **자동 복구 버튼** GUI에서 로그 파일이 있을 때 활성화

### ⚙️ 유연한 설정
- `--dry-run`으로 변경 사항을 적용하기 전에 미리보기
- 멀티스레딩 지원으로 성능 최적화
- 다양한 날짜 형식 옵션으로 맞춤형 정리
- **새로운 기능: 완전한 작업 추적을 위한 로깅 모드**

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

### 고급 옵션

| 옵션 | 설명 |
|--------|-------------|
| `--path` | 대상 디렉토리 (기본값: 현재 디렉토리) |
| `--dry-run` | 변경하지 않고 어떤 일이 일어날지 보여줌 |
| `--log` | 작업 로그를 파일에 저장 |
| `--logging` | 복구를 위한 CSV 로깅 활성화 |
| `--sensitivity` | 시각적 유사성 임계값 (0.0-1.0) |
| `--threads` | 사용할 동시 스레드 수 |
| `--date-format` | 날짜별 정리 형식 (`year` 또는 `yearmonth`) |
| `--copy` | 파일을 이동하지 않고 복사 (flatten만 해당) |
| `--output` | 복사된 파일의 출력 디렉토리 (flatten만 해당) |
| `--duplicates-folder` | 중복 파일을 삭제하지 않고 이 폴더로 이동 |
| `--unclassified-folder` | 날짜 메타데이터가 없는 파일을 이 폴더로 이동 |

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
├── 202112/
│   └── IMG_2000.jpg
└── duplicates/
    ├── IMG_0123 (1).jpg
    └── IMG_0456.jpg
```

## 🧩 기술 개요

SnapTidy는 Python으로 개발되었으며 다음과 같은 핵심 기술을 사용합니다:

- **파일 해싱**: 정확한 중복 검색을 위한 `hashlib`
- **이미지 분석**: 시각적 이미지 비교를 위한 `imagehash` 및 `Pillow`
- **비디오 처리**: 비디오 유사성을 위한 `opencv-python` 및 `ffmpeg`
- **메타데이터 추출**: 파일 정보 파싱을 위한 `exifread` 및 `hachoir`
- **성능 최적화**: 멀티스레딩을 위한 `concurrent.futures`
- **GUI 프레임워크**: 현대적인 크로스 플랫폼 인터페이스를 위한 `PyQt6`

## 🤝 기여하기

기여는 언제나 환영합니다! [이슈 페이지](https://github.com/yourname/snaptidy/issues)에서 열린 작업을 확인하거나 여러분의 아이디어를 제출해 주세요.

## 📜 라이선스

SnapTidy는 MIT 라이선스 하에 제공됩니다 - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

---

<div align="center">
  <i>복잡한 사진 라이브러리를 싫어하는 사람들을 위해 ❤️로 만들었습니다</i>
</div>

## 🖥️ GUI 버전

SnapTidy는 이제 아름답고 직관적인 GUI 애플리케이션을 포함합니다!

### 기능
- **모던 인터페이스**: 드래그앤드롭을 지원하는 깔끔하고 전문적인 디자인
- **시각적 진행률**: 실시간 진행률 바와 상태 업데이트
- **쉬운 설정**: 모든 SnapTidy 옵션을 위한 직관적인 컨트롤
- **크로스 플랫폼**: Windows, macOS, Linux에서 작동
- **복구 시스템**: 로그 파일이 있을 때 내장된 복구 버튼
- **스크롤 지원**: 작은 창 크기도 우아하게 처리

### GUI 실행
```bash
snaptidy-gui
```

### GUI 스크린샷
- **메인 인터페이스**: 폴더 선택, 설정 패널, 액션 버튼
- **진행률 추적**: 상세한 상태 메시지와 실시간 진행률
- **결과 표시**: 작업 완료에 대한 명확한 피드백
- **복구 버튼**: 로그 파일이 있을 때 자동으로 활성화

### GUI 기능
- 📁 **드래그앤드롭**: 폴더를 인터페이스에 간단히 드래그
- ⚙️ **시각적 설정**: 슬라이더로 민감도, 스레드, 옵션 조정
- 📊 **실시간 진행률**: 작업 중 정확히 무슨 일이 일어나는지 확인
- 🎨 **모던 디자인**: OS에 맞는 전문적인 외관
- 🔄 **복구 시스템**: 원클릭 복구 스크립트 생성
- 📋 **로깅 모드**: 완전한 복구 기능이 있는 안전한 작업
- 📱 **반응형 UI**: 작은 창을 위한 스크롤 지원

### 복구 워크플로우
1. **로깅 모드 활성화**: GUI에서 "📋 작업 로그 기록 (복구 가능)" 체크
2. **작업 실행**: flatten, dedup, organize 작업 실행
3. **복구 스크립트 생성**: "🔄 복구" 버튼 클릭 (사용 가능할 때)
4. **복구 실행**: 생성된 `snaptidy_recovery.py` 스크립트 실행

### 안전 기능
- **완전한 복구 가능성**: 로깅 모드에서 모든 작업이 기록됨
- **데이터 손실 방지**: 로깅 모드에서 파일 삭제 비활성화
- **스마트 복구**: 사용 가능한 로그 파일 자동 감지
- **사용자 확인**: 파괴적인 작업 전 명확한 경고 및 확인
