# GitHub Actions를 사용한 자동 빌드

GitHub Actions를 사용하면 Windows 머신 없이도 자동으로 Windows 실행 파일을 빌드할 수 있습니다.

## 워크플로우 종류

### 1. 자동 릴리스 빌드 (`build.yml`)
- **트리거**: 태그 푸시 시 자동 실행
- **기능**: macOS와 Windows 모두 빌드 후 GitHub 릴리스 자동 생성
- **사용법**: `git tag v0.1.0b1 && git push origin v0.1.0b1`

### 2. 수동 빌드 (`manual-build.yml`)
- **트리거**: GitHub 웹에서 수동 실행
- **기능**: 원하는 플랫폼만 선택해서 빌드
- **사용법**: GitHub Actions 탭에서 "Run workflow" 클릭

## 사용 방법

### 자동 릴리스 빌드

1. **태그 생성 및 푸시**:
   ```bash
   git tag v0.1.0b1
   git push origin v0.1.0b1
   ```

2. **GitHub Actions 확인**:
   - GitHub 저장소 → Actions 탭
   - "Build SnapTidy" 워크플로우 실행 확인

3. **릴리스 확인**:
   - GitHub 저장소 → Releases 탭
   - 자동으로 생성된 릴리스와 다운로드 파일들 확인

### 수동 빌드

1. **GitHub 웹에서 실행**:
   - GitHub 저장소 → Actions 탭
   - "Manual Build" 워크플로우 선택
   - "Run workflow" 클릭
   - 플랫폼 선택 (windows/macos/all)
   - "Run workflow" 클릭

2. **아티팩트 다운로드**:
   - 빌드 완료 후 "Artifacts" 섹션에서 다운로드

## 빌드 결과물

### macOS
- `snaptidy-gui` - GUI 실행 파일
- `snaptidy` - CLI 실행 파일

### Windows
- `snaptidy-gui.exe` - GUI 실행 파일
- `snaptidy.exe` - CLI 실행 파일

## 주의사항

1. **빌드 시간**: Windows 빌드는 약 10-15분 소요
2. **용량 제한**: GitHub Actions 아티팩트는 500MB 제한
3. **릴리스 권한**: GitHub 저장소에 릴리스 권한이 필요

## 문제 해결

### 빌드 실패 시
1. GitHub Actions 로그 확인
2. 의존성 문제인지 확인
3. PyInstaller 설정 파일 점검

### 아티팩트 다운로드 실패 시
1. 빌드 완료 후 90일 이내에 다운로드
2. 파일 크기가 500MB 이하인지 확인

## 로컬 테스트

빌드된 실행 파일을 로컬에서 테스트하려면:

```bash
# macOS
chmod +x snaptidy-gui
./snaptidy-gui

# Windows
snaptidy-gui.exe
```

## 다음 단계

1. GitHub 저장소에 푸시
2. 태그 생성 및 푸시
3. GitHub Actions 실행 확인
4. 릴리스 다운로드 및 테스트 