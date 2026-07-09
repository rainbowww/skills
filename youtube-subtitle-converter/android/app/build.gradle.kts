plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "kr.rainbowww.subtitle"
    compileSdk = 34

    defaultConfig {
        applicationId = "kr.rainbowww.subtitle"
        minSdk = 26
        targetSdk = 34
        versionCode = 1
        versionName = "0.1"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.13.1")
    implementation("androidx.appcompat:appcompat:1.7.0")
    implementation("com.google.android.material:material:1.12.0")

    // 2단계: 폰에서 유튜브 오디오 스트림 추출 (NewPipeExtractor + OkHttp 다운로더)
    implementation("com.github.TeamNewPipe:NewPipeExtractor:v0.24.3")
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
}
