// 자막 변환기 — 독립 안드로이드 앱(폰만으로 동작 목표). CI(GitHub Actions)가 APK 빌드.
pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
        maven { url = uri("https://jitpack.io") } // NewPipeExtractor 등 (다음 단계)
    }
}
rootProject.name = "SubtitleConverter"
include(":app")
