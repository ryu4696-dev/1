from pathlib import Path

p = Path("recipe-book/app/src/main/java/dev/ryu4696/recipebook/MainActivity.java")
s = p.read_text(encoding="utf-8")

if "import dev.ryu4696.recipestock.R;" not in s:
    s = s.replace(
        "import org.json.JSONException;\n",
        "import org.json.JSONException;\n\nimport dev.ryu4696.recipestock.R;\n"
    )

p.write_text(s, encoding="utf-8")
