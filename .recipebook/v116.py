from pathlib import Path
import re

root = Path("recipe-book")

# Launcher / Android app label
strings = root / "app/src/main/res/values/strings.xml"
s = strings.read_text(encoding="utf-8")
if re.search(r'<string name="app_name">.*?</string>', s):
    s = re.sub(r'<string name="app_name">.*?</string>',
               '<string name="app_name">MariRecipe</string>', s)
else:
    raise SystemExit("app_name string not found")
strings.write_text(s, encoding="utf-8")

# In-app visible product name
java = root / "app/src/main/java/dev/ryu4696/recipebook/MainActivity.java"
j = java.read_text(encoding="utf-8")
for old in ["Recipe Stock", "RecipeStock", "レシピストック"]:
    j = j.replace(old, "MariRecipe")
java.write_text(j, encoding="utf-8")

# Version bump only
gradle = root / "app/build.gradle"
g = gradle.read_text(encoding="utf-8")
old_v = "versionCode 9\n        versionName '1.1.5'"
new_v = "versionCode 10\n        versionName '1.1.6'"
if old_v not in g:
    raise SystemExit("v1.1.5 version marker not found")
g = g.replace(old_v, new_v)
gradle.write_text(g, encoding="utf-8")
