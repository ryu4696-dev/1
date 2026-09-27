from pathlib import Path

root = Path("recipe-book")
java = root / "app/src/main/java/dev/ryu4696/recipebook/MainActivity.java"
s = java.read_text(encoding="utf-8")

if "import android.graphics.drawable.BitmapDrawable;" not in s:
    s = s.replace(
        "import android.graphics.drawable.GradientDrawable;\n",
        "import android.graphics.drawable.GradientDrawable;\nimport android.graphics.drawable.BitmapDrawable;\nimport android.graphics.drawable.Drawable;\n"
    )

old_colors = """    private static final int BG = Color.rgb(255, 248, 242);
    private static final int CARD = Color.WHITE;
    private static final int INK = Color.rgb(48, 38, 32);
    private static final int MUTED = Color.rgb(110, 96, 86);
    private static final int ACCENT = Color.rgb(122, 78, 52);
    private static final int ACCENT_LIGHT = Color.rgb(241, 226, 214);
    private static final int DANGER = Color.rgb(162, 54, 54);
    private static final int BORDER = Color.rgb(226, 214, 205);
"""
new_colors = """    private static final int BG = Color.rgb(6, 15, 35);
    private static final int CARD = Color.argb(232, 15, 34, 62);
    private static final int INK = Color.rgb(255, 248, 232);
    private static final int MUTED = Color.rgb(184, 198, 222);
    private static final int ACCENT = Color.rgb(235, 198, 114);
    private static final int ACCENT_LIGHT = Color.argb(235, 37, 54, 90);
    private static final int DANGER = Color.rgb(226, 126, 139);
    private static final int BORDER = Color.rgb(88, 111, 153);
    private static final int INPUT_BG = Color.argb(238, 10, 27, 52);
    private static final int GOLD_TEXT = Color.rgb(255, 232, 176);
    private static final int PRIMARY_INK = Color.rgb(29, 35, 53);
"""
if old_colors not in s:
    raise SystemExit("base color block not found")
s = s.replace(old_colors, new_colors, 1)

# Remove the explanatory copy the user explicitly asked to delete.
lead = """        TextView lead = text("菓子レシピと原価を、見る画面と入力画面を混ぜずに管理します。", 14, MUTED);
        lead.setPadding(0, 0, 0, dp(10));
        page.addView(lead);

"""
if lead in s:
    s = s.replace(lead, "", 1)

# Keep the exact layout, but show the illustrated image resource behind it.
s = s.replace("        page.setBackgroundColor(BG);\n", "        page.setBackgroundColor(Color.TRANSPARENT);\n", 1)
s = s.replace(
    "        s.setBackgroundColor(BG);\n",
    """        int bgRes = "home".equals(currentScreen)
                ? R.drawable.bg_mari_home
                : ("edit".equals(currentScreen) ? R.drawable.bg_mari_edit : R.drawable.bg_mari_screen);
        Drawable bg = getResources().getDrawable(bgRes);
        if (bg instanceof BitmapDrawable) {
            ((BitmapDrawable) bg).setGravity(Gravity.FILL);
        }
        s.setBackground(bg);
""",
    1
)

# Replace only the home title slot with a dedicated logo asset.
old_title = """        TextView t = text(title, 22, INK);
        t.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        t.setGravity(Gravity.START | Gravity.CENTER_VERTICAL);
        t.setSingleLine(true);
        t.setEllipsize(TextUtils.TruncateAt.END);
        t.setLayoutParams(new LinearLayout.LayoutParams(0, dp(52), 1f));
        bar.addView(t);
"""
new_title = """        if ("MariRecipe".equals(title)) {
            ImageView logo = new ImageView(this);
            logo.setImageResource(R.drawable.logo_marirecipe);
            logo.setScaleType(ImageView.ScaleType.CENTER_INSIDE);
            logo.setAdjustViewBounds(true);
            logo.setLayoutParams(new LinearLayout.LayoutParams(0, dp(52), 1f));
            bar.addView(logo);
        } else {
            TextView t = text(title, 22, INK);
            t.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
            t.setGravity(Gravity.START | Gravity.CENTER_VERTICAL);
            t.setSingleLine(true);
            t.setEllipsize(TextUtils.TruncateAt.END);
            t.setLayoutParams(new LinearLayout.LayoutParams(0, dp(52), 1f));
            bar.addView(t);
        }
"""
if old_title not in s:
    raise SystemExit("topbar title block not found")
s = s.replace(old_title, new_title, 1)

# Typography and controls.
s = s.replace("        TextView t = text(s, 19, INK);\n", "        TextView t = text(s, 19, GOLD_TEXT);\n", 1)
s = s.replace("        e.setHintTextColor(Color.rgb(160, 145, 136));\n", "        e.setHintTextColor(Color.rgb(137, 157, 190));\n", 1)
s = s.replace("        e.setBackground(round(Color.WHITE, 11, BORDER, 1));\n", "        e.setBackground(round(INPUT_BG, 11, BORDER, 1));\n", 1)
s = s.replace("        s.setBackground(round(Color.WHITE, 11, BORDER, 1));\n", "        s.setBackground(round(INPUT_BG, 11, BORDER, 1));\n", 1)

s = s.replace(
    """        b.setTextColor(ACCENT);
        b.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        b.setBackground(round(ACCENT_LIGHT, 11, ACCENT, 2));
""",
    """        b.setTextColor(GOLD_TEXT);
        b.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        b.setBackground(round(ACCENT_LIGHT, 11, ACCENT, 2));
""",
    1
)
s = s.replace(
    """        b.setTextColor(Color.WHITE);
        b.setBackground(round(ACCENT, 11));
""",
    """        b.setTextColor(PRIMARY_INK);
        b.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        GradientDrawable gold = new GradientDrawable(
                GradientDrawable.Orientation.TL_BR,
                new int[]{Color.rgb(255, 224, 153), Color.rgb(221, 177, 88)});
        gold.setCornerRadius(dp(11));
        gold.setStroke(dp(1), Color.rgb(255, 236, 185));
        b.setBackground(gold);
""",
    1
)
s = s.replace(
    """        b.setTextColor(ACCENT);
        b.setBackground(round(Color.WHITE, 11, ACCENT, 1));
""",
    """        b.setTextColor(GOLD_TEXT);
        GradientDrawable secondary = new GradientDrawable(
                GradientDrawable.Orientation.TL_BR,
                new int[]{Color.argb(238, 26, 51, 88), Color.argb(242, 11, 29, 55)});
        secondary.setCornerRadius(dp(11));
        secondary.setStroke(dp(1), ACCENT);
        b.setBackground(secondary);
""",
    1
)
s = s.replace(
    """        b.setTextColor(DANGER);
        b.setBackground(round(Color.WHITE, 11, DANGER, 1));
""",
    """        b.setTextColor(Color.rgb(255, 214, 219));
        b.setBackground(round(INPUT_BG, 11, DANGER, 1));
""",
    1
)

# Cards become slightly translucent so the illustration reads through without hurting legibility.
s = s.replace("        c.setBackground(round(CARD, 15, BORDER, 1));\n", "        c.setBackground(nightCard(15));\n", 1)
s = s.replace("        c.setBackground(round(CARD, 12, BORDER, 1));\n", "        c.setBackground(nightCard(12));\n", 1)
s = s.replace("        image.setBackgroundColor(Color.rgb(238, 234, 231));\n", "        image.setBackgroundColor(Color.rgb(16, 36, 64));\n", 1)

marker = """    private GradientDrawable round(int fill, int radiusDp) {
"""
helper = """    private GradientDrawable nightCard(int radiusDp) {
        GradientDrawable g = new GradientDrawable(
                GradientDrawable.Orientation.TL_BR,
                new int[]{Color.argb(235, 28, 53, 91), Color.argb(238, 13, 29, 55)});
        g.setCornerRadius(dp(radiusDp));
        g.setStroke(dp(1), BORDER);
        return g;
    }

"""
if marker not in s:
    raise SystemExit("round helper marker not found")
s = s.replace(marker, helper + marker, 1)

java.write_text(s, encoding="utf-8")

# Dark system chrome.
styles = root / "app/src/main/res/values/styles.xml"
st = styles.read_text(encoding="utf-8")
st = st.replace('parent="android:style/Theme.Material.Light.NoActionBar"', 'parent="android:style/Theme.Material.NoActionBar"')
st = st.replace('<item name="android:windowLightStatusBar">true</item>', '<item name="android:windowLightStatusBar">false</item>')
if '<item name="android:windowLightNavigationBar">' not in st:
    st = st.replace(
        '<item name="android:windowLightStatusBar">false</item>',
        '<item name="android:windowLightStatusBar">false</item>\n        <item name="android:windowLightNavigationBar">false</item>'
    )
st = st.replace('#FFF8F2', '#061023').replace('#7A4E34', '#EBC672')
styles.write_text(st, encoding="utf-8")

# Use the dedicated raster icon.
manifest = root / "app/src/main/AndroidManifest.xml"
m = manifest.read_text(encoding="utf-8")
m = m.replace('android:icon="@drawable/ic_launcher_recipe"', 'android:icon="@drawable/ic_mari"')
manifest.write_text(m, encoding="utf-8")

gradle = root / "app/build.gradle"
g = gradle.read_text(encoding="utf-8")
old_v = "versionCode 11\n        versionName '1.1.7'"
new_v = "versionCode 15\n        versionName '1.4.0'"
if old_v not in g:
    raise SystemExit("v1.1.7 version marker not found")
gradle.write_text(g.replace(old_v, new_v), encoding="utf-8")
