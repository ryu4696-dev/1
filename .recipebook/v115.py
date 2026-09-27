from pathlib import Path

root = Path("recipe-book")
java = root / "app/src/main/java/dev/ryu4696/recipebook/MainActivity.java"
s = java.read_text(encoding="utf-8")

field_old = """    private final Map<Integer, Integer> lastStepPageBySection = new HashMap<>();
"""
field_new = """    private final Map<Integer, Integer> lastStepPageBySection = new HashMap<>();
    private ScrollView activeScrollView;
"""
if field_old not in s:
    raise SystemExit("field marker not found")
s = s.replace(field_old, field_new, 1)

old_edit = """        // 入力中だけ、フォーカス欄をIMEの上へ見える位置まで寄せる。
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
"""
new_edit = """        // 入力欄をタップしたら、ユーザーに手動スクロールを要求せず
        // 対象（工程本文ならSTEPカード）をキーボード上へ自動配置する。
        e.setOnFocusChangeListener((v, hasFocus) -> {
            if (!hasFocus) return;
            boolean stepBody = hint != null && hint.contains("工程");
            Runnable reveal = () -> revealEditor(v, stepBody);
            v.postDelayed(reveal, 100);
            v.postDelayed(reveal, 280);
            v.postDelayed(reveal, 520);
        });
"""
if old_edit not in s:
    raise SystemExit("edit focus block not found")
s = s.replace(old_edit, new_edit, 1)

marker = """    private ScrollView scroll(View child) {
"""
helper = """    private void revealEditor(View focused, boolean wholeCard) {
        ScrollView sv = activeScrollView;
        if (sv == null || focused == null) return;

        View anchor = focused;
        if (wholeCard && focused.getParent() instanceof View) {
            anchor = (View) focused.getParent();
        }

        Rect rect = new Rect();
        anchor.getDrawingRect(rect);
        sv.offsetDescendantRectToMyCoords(anchor, rect);

        // STEPカードは上から約20dp、通常の入力欄は少し余裕を持って配置。
        int marginTop = wholeCard ? dp(20) : dp(72);
        int targetY = Math.max(0, rect.top - marginTop);
        sv.smoothScrollTo(0, targetY);
    }

    private ScrollView scroll(View child) {
"""
if marker not in s:
    raise SystemExit("scroll marker not found")
s = s.replace(marker, helper, 1)

old_scroll_start = """        ScrollView s = new ScrollView(this);
        s.setFillViewport(true);
"""
new_scroll_start = """        ScrollView s = new ScrollView(this);
        activeScrollView = s;
        s.setFillViewport(true);
"""
if old_scroll_start not in s:
    raise SystemExit("scroll start not found")
s = s.replace(old_scroll_start, new_scroll_start, 1)

old_insets = """            if (imeVisible) {
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
"""
new_insets = """            if (imeVisible) {
                Runnable revealFocused = () -> {
                    View focused = getCurrentFocus();
                    if (focused == null || focused == v) return;
                    boolean stepBody = focused instanceof EditText
                            && ((EditText) focused).getHint() != null
                            && ((EditText) focused).getHint().toString().contains("工程");
                    revealEditor(focused, stepBody);
                };
                v.postDelayed(revealFocused, 80);
                v.postDelayed(revealFocused, 260);
            }
"""
if old_insets not in s:
    raise SystemExit("insets reveal block not found")
s = s.replace(old_insets, new_insets, 1)

java.write_text(s, encoding="utf-8")

gradle = root / "app/build.gradle"
g = gradle.read_text(encoding="utf-8")
old_v = "versionCode 8\n        versionName '1.1.4'"
new_v = "versionCode 9\n        versionName '1.1.5'"
if old_v not in g:
    raise SystemExit("v1.1.4 version marker not found")
g = g.replace(old_v, new_v)
gradle.write_text(g, encoding="utf-8")
