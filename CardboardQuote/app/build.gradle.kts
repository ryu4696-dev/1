plugins { id("com.android.application"); id("org.jetbrains.kotlin.android") }
android {
    namespace = "jp.co.kobayashi.cardboardquote"
    compileSdk = 34
    defaultConfig { applicationId = "jp.co.kobayashi.cardboardquote"; minSdk = 26; targetSdk = 34; versionCode = 6; versionName = "1.6.0" }
    compileOptions { sourceCompatibility = JavaVersion.VERSION_17; targetCompatibility = JavaVersion.VERSION_17 }
    kotlinOptions { jvmTarget = "17" }
}
