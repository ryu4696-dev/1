from pathlib import Path

main = Path("recipe-book/app/src/main/java/dev/ryu4696/recipebook/MainActivity.java")
s = main.read_text(encoding="utf-8")
if "import android.os.Build;" not in s:
    s = s.replace("import android.os.Bundle;\n", "import android.os.Bundle;\nimport android.os.Build;\n")
if "import android.view.WindowInsets;" not in s:
    s = s.replace("import android.view.Gravity;\n", "import android.view.Gravity;\nimport android.view.WindowInsets;\n")

old = """    private ScrollView scroll(View child) {
        ScrollView s = new ScrollView(this);
        s.setFillViewport(true);
        s.setBackgroundColor(BG);
        s.addView(child);
        return s;
    }
"""
new = """    private ScrollView scroll(View child) {
        ScrollView s = new ScrollView(this);
        s.setFillViewport(true);
        s.setBackgroundColor(BG);
        s.addView(child);

        s.setOnApplyWindowInsetsListener((v, insets) -> {
            int top;
            int bottom;
            if (Build.VERSION.SDK_INT >= 30) {
                android.graphics.Insets safe = insets.getInsets(
                        WindowInsets.Type.systemBars() | WindowInsets.Type.displayCutout());
                top = safe.top;
                bottom = safe.bottom;
            } else {
                top = insets.getSystemWindowInsetTop();
                bottom = insets.getSystemWindowInsetBottom();
            }
            v.setPadding(0, top, 0, bottom);
            return insets;
        });
        s.requestApplyInsets();
        return s;
    }
"""
if old not in s and "WindowInsets.Type.systemBars()" not in s:
    raise SystemExit("scroll() block not found")
s = s.replace(old, new)
main.write_text(s, encoding="utf-8")

gradle = Path("recipe-book/app/build.gradle")
g = gradle.read_text(encoding="utf-8")
g = g.replace("versionCode 1\n        versionName '1.0.0'", "versionCode 2\n        versionName '1.0.1'")
gradle.write_text(g, encoding="utf-8")
