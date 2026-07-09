# 자막 변환기 — 독립 안드로이드 앱 (APK)

**폰만으로 동작하는 진짜 설치형 앱**을 목표로 합니다. PWA(홈 화면 추가)와 달리
PC가 필요 없습니다. 유튜브 오디오 추출 + 한국어 음성 인식을 **폰 안에서** 합니다.

## 어디서 내려받나요? (APK 파일)

이 저장소는 안드로이드 SDK가 없어 여기서는 APK를 못 만듭니다. 대신 **GitHub
Actions가 APK를 빌드**합니다(러너에 SDK 내장).

- **최신 빌드 내려받기:** 저장소 **Actions → “Android APK (subtitle converter)”**
  → 최근 실행 → 아래 **Artifacts**의 `subtitle-converter-apk` 를 내려받아 압축을
  풀면 `subtitle-converter.apk` 가 나옵니다.
- **릴리스로 받기:** `v*` 태그를 밀면 Releases에 `.apk` 가 첨부됩니다(폰에서 바로 클릭 설치).

설치 시 “알 수 없는 출처(출처를 알 수 없는 앱) 허용”을 한 번 켜야 할 수 있어요.

## 개발 단계 (한 번 만들면 계속 개선)

- [x] **1단계** — 설치되는 진짜 APK + 화면 + 유튜브 주소 인식 (CI 빌드/설치 검증)
- [ ] **2단계** — NewPipeExtractor 로 폰에서 오디오 추출
- [ ] **3단계** — whisper.cpp 온디바이스 한국어 음성 인식 → 자막 + TXT 저장
- [ ] **4단계** — 타임스탬프·검색·글자 크기 등 웹앱 기능 이식

## 로컬에서 직접 빌드하려면 (안드로이드 스튜디오 있는 PC)

```bash
# 대상(실행 위치): 🟩 Android SDK 설치된 Linux·macOS 터미널
cd youtube-subtitle-converter/android
gradle :app:assembleDebug        # 또는 Android Studio에서 열고 Run
# 결과: app/build/outputs/apk/debug/app-debug.apk
```

구조: `app/`(단일 모듈), 언어 Kotlin, `minSdk 26`, `compileSdk 34`.
동작은 웹앱과 일치시키려 `parse_video_id` 정규식을 그대로 옮겼습니다.
