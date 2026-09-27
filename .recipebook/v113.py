from pathlib import Path

root = Path("recipe-book")
java = root / "app/src/main/java/dev/ryu4696/recipebook/MainActivity.java"
s = java.read_text(encoding="utf-8")

if "import android.graphics.Rect;" not in s:
    s = s.replace("import android.graphics.Color;\n", "import android.graphics.Color;\nimport android.graphics.Rect;\n")

old = """    private EditText edit(String hint, boolean number) {
        EditText e = new EditText(this);
        e.setHint(hint);
        e.setTextColor(INK);
        e.setHintTextColor(Color.rgb(160, 145, 136));
        e.setTextSize(16);
        e.setPadding(dp(12), 0, dp(12), 0);
        e.setBackground(round(Color.WHITE, 11, BORDER, 1));
        e.setLayoutParams(new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(48)));
        if (number) e.setInputType(InputType.TYPE_CLASS_NUMBER | InputType.TYPE_NUMBER_FLAG_DECIMAL);
        return e;
    }
"""
new = """    private EditText edit(String hint, boolean number) {
        EditText e = new EditText(this);
        e.setHint(hint);
        e.setTextColor(INK);
        e.setHintTextColor(Color.rgb(160, 145, 136));
        e.setTextSize(16);
        e.setPadding(dp(12), 0, dp(12), 0);
        e.setBackground(round(Color.WHITE, 11, BORDER, 1));
        e.setLayoutParams(new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(48)));
        if (number) e.setInputType(InputType.TYPE_CLASS_NUMBER | InputType.TYPE_NUMBER_FLAG_DECIMAL);

        // 入力中だけ、フォーカス欄をIMEの上へ見える位置まで寄せる。
        // 常設の下余白は増やさない。
        e.setOnFocusChangeListener((v, hasFocus) -> {
            if (!hasFocus) return;
            Runnable reveal = () -> {
                Rect rect = new Rect();
                v.getDrawingRect(rect);
                rect.top -= dp(12);
                rect.bottom += dp(24);
                v.requestRectangleOnScreen(rect, true);
            };
            v.postDelayed(reveal, 120);
            v.postDelayed(reveal, 360);
        });
        return e;
    }
"""
if old not in s:
    raise SystemExit("edit() block not found")
s = s.replace(old, new)
java.write_text(s, encoding="utf-8")

manifest = root / "app/src/main/AndroidManifest.xml"
m = manifest.read_text(encoding="utf-8")
needle = """        <activity
            android:name="dev.ryu4696.recipebook.MainActivity"
            android:screenOrientation="unspecified"
            android:exported="true">"""
replacement = """        <activity
            android:name="dev.ryu4696.recipebook.MainActivity"
            android:screenOrientation="unspecified"
            android:windowSoftInputMode="adjustResize"
            android:exported="true">"""
if needle not in m:
    raise SystemExit("activity manifest block not found")
m = m.replace(needle, replacement)
manifest.write_text(m, encoding="utf-8")

gradle = root / "app/build.gradle"
g = gradle.read_text(encoding="utf-8")
old_v = "versionCode 6\n        versionName '1.1.2'"
new_v = "versionCode 7\n        versionName '1.1.3'"
if old_v not in g:
    raise SystemExit("v1.1.2 version marker not found")
g = g.replace(old_v, new_v)
gradle.write_text(g, encoding="utf-8")
