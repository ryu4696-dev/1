# APK build

This project is configured for Android 17 / API 37.

## GitHub Actions

The included `.github/workflows/build-apk.yml` installs:
- JDK 17
- Gradle 9.6.0
- Android SDK Platform 37
- Android Build Tools 36.0.0

It then runs `:app:assembleDebug` and publishes `FoldTrio-v0.1-debug.apk` as a workflow artifact.

AGP 9.4.0 requires Gradle 9.6.0 and supports API 37.
