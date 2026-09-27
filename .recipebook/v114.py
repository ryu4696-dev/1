from pathlib import Path

root = Path("recipe-book")
java = root / "app/src/main/java/dev/ryu4696/recipebook/MainActivity.java"
s = java.read_text(encoding="utf-8")

old = """    private ScrollView scroll(View child) {
        ScrollView s = new ScrollView(this);
        s.setFillViewport(true);
        s.setBackgroundColor(BG);
        s.addView(child);

        // Android 15/16 は edge-to-edge が標準化されているため、
        // ステータスバーやパンチホールの高さを端末ごとに取得して内容を安全領域へ移す。
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

new = """    private ScrollView scroll(View child) {
        ScrollView s = new ScrollView(this);
        s.setFillViewport(true);
        s.setBackgroundColor(BG);
        s.addView(child);

        // 通常時はシステムバー分だけ。
        // キーボード表示中だけIMEの高さを下側paddingへ足し、
        // ScrollViewが入力欄まで確実にスクロールできる距離を作る。
        s.setOnApplyWindowInsetsListener((v, insets) -> {
            int top;
            int bottom;
            boolean imeVisible = false;

            if (Build.VERSION.SDK_INT >= 30) {
                android.graphics.Insets safe = insets.getInsets(
                        WindowInsets.Type.systemBars() | WindowInsets.Type.displayCutout());
                top = safe.top;

                imeVisible = insets.isVisible(WindowInsets.Type.ime());
                android.graphics.Insets ime = insets.getInsets(WindowInsets.Type.ime());
                bottom = imeVisible
                        ? Math.max(safe.bottom, ime.bottom + dp(16))
                        : safe.bottom;
            } else {
                top = insets.getSystemWindowInsetTop();
                bottom = insets.getSystemWindowInsetBottom();
            }

            v.setPadding(0, top, 0, bottom);

            if (imeVisible) {
                Runnable revealFocused = () -> {
                    View focused = getCurrentFocus();
                    if (focused == null || focused == v) return;

                    Rect rect = new Rect();
                    focused.getDrawingRect(rect);
                    rect.top -= dp(12);
                    rect.bottom += dp(32);
                    focused.requestRectangleOnScreen(rect, true);
                };
                v.post(revealFocused);
                v.postDelayed(revealFocused, 180);
            }

            return insets;
        });
        s.requestApplyInsets();
        return s;
    }
"""

if old not in s:
    raise SystemExit("scroll() block not found")
s = s.replace(old, new)
java.write_text(s, encoding="utf-8")

gradle = root / "app/build.gradle"
g = gradle.read_text(encoding="utf-8")
old_v = "versionCode 7\n        versionName '1.1.3'"
new_v = "versionCode 8\n        versionName '1.1.4'"
if old_v not in g:
    raise SystemExit("v1.1.3 version marker not found")
g = g.replace(old_v, new_v)
gradle.write_text(g, encoding="utf-8")
