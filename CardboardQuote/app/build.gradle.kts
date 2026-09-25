plugins { id("com.android.application"); id("org.jetbrains.kotlin.android") }
android {
    namespace = "jp.co.kobayashi.cardboardquote"
    compileSdk = 34
    defaultConfig { applicationId = "jp.co.kobayashi.cardboardquote"; minSdk = 26; targetSdk = 34; versionCode = 7; versionName = "1.7.0" }
    compileOptions { sourceCompatibility = JavaVersion.VERSION_17; targetCompatibility = JavaVersion.VERSION_17 }
    kotlinOptions { jvmTarget = "17" }
}
