from pathlib import Path

root = Path("recipe-book")

manifest = root / "app/src/main/AndroidManifest.xml"
m = manifest.read_text(encoding="utf-8")
if 'android:label="Recipe Stock"' not in m:
    raise SystemExit("hardcoded launcher label not found")
m = m.replace('android:label="Recipe Stock"', 'android:label="@string/app_name"')
manifest.write_text(m, encoding="utf-8")

gradle = root / "app/build.gradle"
g = gradle.read_text(encoding="utf-8")
old_v = "versionCode 10\n        versionName '1.1.6'"
new_v = "versionCode 11\n        versionName '1.1.7'"
if old_v not in g:
    raise SystemExit("v1.1.6 version marker not found")
g = g.replace(old_v, new_v)
gradle.write_text(g, encoding="utf-8")
