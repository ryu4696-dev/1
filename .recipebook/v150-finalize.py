from pathlib import Path

root = Path("recipe-book")
gradle = root / "app/build.gradle"
g = gradle.read_text(encoding="utf-8")
g = g.replace("versionCode 15\n        versionName '1.4.0'", "versionCode 16\n        versionName '1.5.0'")
gradle.write_text(g, encoding="utf-8")

java = root / "app/src/main/java/dev/ryu4696/recipebook/MainActivity.java"
s = java.read_text(encoding="utf-8")
s = s.replace("getWindow().setStatusBarColor(BG);", "getWindow().setStatusBarColor(Color.rgb(2, 7, 19));")
s = s.replace("getWindow().setNavigationBarColor(BG);", "getWindow().setNavigationBarColor(Color.rgb(9, 39, 71));")
java.write_text(s, encoding="utf-8")
