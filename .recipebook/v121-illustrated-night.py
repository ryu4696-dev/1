from pathlib import Path

root = Path("recipe-book")
java = root / "app/src/main/java/dev/ryu4696/recipebook/MainActivity.java"
s = java.read_text(encoding="utf-8")

# Drawing imports for the illustrated night background.
if "import android.graphics.Canvas;" not in s:
    s = s.replace(
        "import android.graphics.Color;\n",
        "import android.graphics.Color;\n"
        "import android.graphics.Canvas;\n"
        "import android.graphics.LinearGradient;\n"
        "import android.graphics.Paint;\n"
        "import android.graphics.Path;\n"
        "import android.graphics.RectF;\n"
        "import android.graphics.Shader;\n"
    )
if "import android.graphics.drawable.Drawable;" not in s:
    s = s.replace(
        "import android.graphics.drawable.GradientDrawable;\n",
        "import android.graphics.drawable.GradientDrawable;\n"
        "import android.graphics.drawable.Drawable;\n"
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
new_colors = """    // MariRecipe - illustrated moonlit night palette.
    private static final int BG = Color.rgb(8, 16, 38);
    private static final int CARD = Color.rgb(18, 38, 70);
    private static final int CARD_2 = Color.rgb(24, 47, 82);
    private static final int INPUT_BG = Color.rgb(12, 29, 55);
    private static final int INK = Color.rgb(255, 248, 231);
    private static final int MUTED = Color.rgb(184, 198, 222);
    private static final int ACCENT = Color.rgb(235, 198, 114);
    private static final int ACCENT_LIGHT = Color.rgb(38, 55, 91);
    private static final int DANGER = Color.rgb(224, 124, 136);
    private static final int BORDER = Color.rgb(83, 104, 145);
    private static final int GOLD_TEXT = Color.rgb(255, 232, 176);
    private static final int PRIMARY_INK = Color.rgb(28, 34, 51);
"""
if old_colors not in s:
    raise SystemExit("base color block not found")
s = s.replace(old_colors, new_colors, 1)

# Keep every layout/spacing rule intact. Only visual surfaces change.
s = s.replace("        page.setBackgroundColor(BG);\n", "        page.setBackgroundColor(Color.TRANSPARENT);\n", 1)
s = s.replace("        s.setBackgroundColor(BG);\n", "        s.setBackground(new NightSkyDrawable());\n", 1)

# Inputs / spinner.
s = s.replace(
    "        e.setHintTextColor(Color.rgb(160, 145, 136));\n",
    "        e.setHintTextColor(Color.rgb(140, 158, 190));\n",
    1
)
s = s.replace(
    "        e.setBackground(round(Color.WHITE, 11, BORDER, 1));\n",
    "        e.setBackground(round(INPUT_BG, 11, BORDER, 1));\n",
    1
)
s = s.replace(
    "        s.setBackground(round(Color.WHITE, 11, BORDER, 1));\n",
    "        s.setBackground(round(INPUT_BG, 11, BORDER, 1));\n",
    1
)

# Buttons.
old_selected = """        b.setTextColor(ACCENT);
        b.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        b.setBackground(round(ACCENT_LIGHT, 11, ACCENT, 2));
"""
new_selected = """        b.setTextColor(GOLD_TEXT);
        b.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        b.setBackground(round(ACCENT_LIGHT, 11, ACCENT, 2));
"""
s = s.replace(old_selected, new_selected, 1)

old_primary = """        b.setTextColor(Color.WHITE);
        b.setBackground(round(ACCENT, 11));
"""
new_primary = """        b.setTextColor(PRIMARY_INK);
        b.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        b.setBackground(round(ACCENT, 11, Color.rgb(255, 229, 166), 1));
"""
s = s.replace(old_primary, new_primary, 1)

old_button = """        b.setTextColor(ACCENT);
        b.setBackground(round(Color.WHITE, 11, ACCENT, 1));
"""
new_button = """        b.setTextColor(GOLD_TEXT);
        b.setBackground(round(INPUT_BG, 11, ACCENT, 1));
"""
s = s.replace(old_button, new_button, 1)

old_danger = """        b.setTextColor(DANGER);
        b.setBackground(round(Color.WHITE, 11, DANGER, 1));
"""
new_danger = """        b.setTextColor(Color.rgb(255, 211, 217));
        b.setBackground(round(INPUT_BG, 11, DANGER, 1));
"""
s = s.replace(old_danger, new_danger, 1)

# Home brand title: same position, only typography/color changes.
needle = """        t.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        t.setGravity(Gravity.START | Gravity.CENTER_VERTICAL);
"""
replacement = """        if ("MariRecipe".equals(title)) {
            t.setTypeface(Typeface.SERIF, Typeface.BOLD_ITALIC);
            t.setTextColor(GOLD_TEXT);
            t.setTextSize(27);
        } else {
            t.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        }
        t.setGravity(Gravity.START | Gravity.CENTER_VERTICAL);
"""
if needle not in s:
    raise SystemExit("topBar title styling marker not found")
s = s.replace(needle, replacement, 1)

# Cards get a richer deep-blue gradient, still same dimensions/padding.
s = s.replace("        c.setBackground(round(CARD, 15, BORDER, 1));\n", "        c.setBackground(nightCard(15));\n", 1)
s = s.replace("        c.setBackground(round(CARD, 12, BORDER, 1));\n", "        c.setBackground(nightCard(12));\n", 1)

# Step image placeholder.
s = s.replace(
    "        image.setBackgroundColor(Color.rgb(238, 234, 231));\n",
    "        image.setBackgroundColor(Color.rgb(16, 35, 63));\n",
    1
)

marker = """    private LinearLayout page() {
"""
night_code = r'''    private GradientDrawable nightCard(int radiusDp) {
        GradientDrawable g = new GradientDrawable(
                GradientDrawable.Orientation.TL_BR,
                new int[]{CARD_2, CARD});
        g.setCornerRadius(dp(radiusDp));
        g.setStroke(dp(1), BORDER);
        return g;
    }

    private class NightSkyDrawable extends Drawable {
        private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
        private final Paint line = new Paint(Paint.ANTI_ALIAS_FLAG);

        @Override
        public void draw(Canvas canvas) {
            android.graphics.Rect b = getBounds();
            float w = Math.max(1f, b.width());
            float h = Math.max(1f, b.height());
            float density = getResources().getDisplayMetrics().density;

            // Deep indigo to star-blue vertical night sky.
            paint.setShader(new LinearGradient(
                    0, 0, 0, h,
                    new int[]{
                            Color.rgb(5, 13, 31),
                            Color.rgb(10, 25, 53),
                            Color.rgb(16, 37, 69)
                    },
                    new float[]{0f, 0.56f, 1f},
                    Shader.TileMode.CLAMP));
            canvas.drawRect(b, paint);
            paint.setShader(null);

            // Soft illustrated cloud/mist masses, deliberately subtle behind UI.
            paint.setColor(Color.argb(18, 120, 145, 205));
            canvas.drawCircle(w * 0.11f, h * 0.18f, w * 0.24f, paint);
            canvas.drawCircle(w * 0.30f, h * 0.20f, w * 0.19f, paint);
            canvas.drawCircle(w * 0.82f, h * 0.31f, w * 0.30f, paint);
            paint.setColor(Color.argb(12, 180, 150, 210));
            canvas.drawCircle(w * 0.60f, h * 0.72f, w * 0.34f, paint);

            // Star field: mostly tiny, with a few warm luminous stars.
            for (int i = 0; i < 132; i++) {
                float x = ((i * 53 + 17) % 223) / 223f * w;
                float y = ((i * 79 + 23) % 337) / 337f * h;
                boolean hero = i % 17 == 0;
                boolean medium = i % 7 == 0;
                float r = (hero ? 1.8f : (medium ? 1.05f : 0.55f)) * density;
                int alpha = hero ? 190 : (medium ? 115 : 66);
                paint.setColor(Color.argb(alpha, 255, 238, 196));
                canvas.drawCircle(x, y, r, paint);

                if (hero) {
                    line.setColor(Color.argb(105, 255, 232, 175));
                    line.setStrokeWidth(0.8f * density);
                    canvas.drawLine(x - 4*density, y, x + 4*density, y, line);
                    canvas.drawLine(x, y - 4*density, x, y + 4*density, line);
                }
            }

            // Fine gold shooting-star arc inspired by the reference image.
            line.setStyle(Paint.Style.STROKE);
            line.setStrokeCap(Paint.Cap.ROUND);
            line.setStrokeWidth(1.0f * density);
            line.setColor(Color.argb(86, 245, 211, 137));
            Path arc = new Path();
            arc.moveTo(w * 0.16f, h * 0.13f);
            arc.quadTo(w * 0.43f, h * 0.075f, w * 0.68f, h * 0.16f);
            canvas.drawPath(arc, line);

            // Elegant crescent watermark in upper-right.
            line.setStrokeWidth(2.2f * density);
            line.setColor(Color.argb(92, 241, 198, 111));
            RectF moon = new RectF(w * 0.74f, h * 0.055f, w * 0.96f, h * 0.18f);
            canvas.drawArc(moon, 72, 220, false, line);

            // Minimal seated cat line-art paired with the moon.
            float ox = w * 0.835f;
            float oy = h * 0.135f;
            float sc = Math.max(0.85f, Math.min(w / 440f, h / 900f));
            Path cat = new Path();
            cat.moveTo(ox, oy);
            cat.cubicTo(ox - 8*sc, oy - 6*sc, ox - 8*sc, oy - 17*sc, ox - 2*sc, oy - 23*sc);
            cat.lineTo(ox - 4*sc, oy - 33*sc);
            cat.lineTo(ox + 4*sc, oy - 27*sc);
            cat.lineTo(ox + 12*sc, oy - 34*sc);
            cat.lineTo(ox + 12*sc, oy - 23*sc);
            cat.cubicTo(ox + 20*sc, oy - 17*sc, ox + 20*sc, oy - 6*sc, ox + 13*sc, oy + 1*sc);
            cat.cubicTo(ox + 22*sc, oy + 10*sc, ox + 22*sc, oy + 31*sc, ox + 16*sc, oy + 42*sc);
            cat.cubicTo(ox + 4*sc, oy + 48*sc, ox - 8*sc, oy + 43*sc, ox - 10*sc, oy + 30*sc);
            cat.cubicTo(ox - 11*sc, oy + 18*sc, ox - 7*sc, oy + 7*sc, ox, oy);
            cat.moveTo(ox - 8*sc, oy + 33*sc);
            cat.cubicTo(ox - 22*sc, oy + 34*sc, ox - 28*sc, oy + 47*sc, ox - 21*sc, oy + 56*sc);
            cat.cubicTo(ox - 14*sc, oy + 63*sc, ox - 4*sc, oy + 58*sc, ox + 1*sc, oy + 50*sc);
            line.setStrokeWidth(1.35f * density);
            line.setColor(Color.argb(72, 255, 242, 213));
            canvas.drawPath(cat, line);

            // Faint distant city silhouette near the bottom to echo the reference artwork.
            paint.setColor(Color.argb(72, 5, 10, 24));
            Path city = new Path();
            city.moveTo(0, h);
            city.lineTo(0, h * 0.91f);
            float[] xs = {0.04f,0.09f,0.14f,0.20f,0.27f,0.33f,0.39f,0.46f,0.53f,0.61f,0.68f,0.75f,0.82f,0.89f,0.95f,1f};
            float[] ys = {0.89f,0.82f,0.90f,0.86f,0.91f,0.79f,0.87f,0.84f,0.92f,0.83f,0.88f,0.80f,0.90f,0.85f,0.91f,0.87f};
            for (int i = 0; i < xs.length; i++) city.lineTo(w * xs[i], h * ys[i]);
            city.lineTo(w, h);
            city.close();
            canvas.drawPath(city, paint);
        }

        @Override public void setAlpha(int alpha) { }
        @Override public void setColorFilter(android.graphics.ColorFilter colorFilter) { }
        @Override public int getOpacity() { return android.graphics.PixelFormat.OPAQUE; }
    }

'''
if marker not in s:
    raise SystemExit("page() marker not found")
s = s.replace(marker, night_code + marker, 1)

java.write_text(s, encoding="utf-8")

# Dark system chrome.
styles = root / "app/src/main/res/values/styles.xml"
st = styles.read_text(encoding="utf-8")
st = st.replace('parent="android:style/Theme.Material.Light.NoActionBar"',
                'parent="android:style/Theme.Material.NoActionBar"')
st = st.replace('<item name="android:windowLightStatusBar">true</item>',
                '<item name="android:windowLightStatusBar">false</item>')
if '<item name="android:windowLightNavigationBar">' not in st:
    st = st.replace(
        '<item name="android:windowLightStatusBar">false</item>',
        '<item name="android:windowLightStatusBar">false</item>\n'
        '        <item name="android:windowLightNavigationBar">false</item>'
    )
st = st.replace('#FFF8F2', '#081026')
st = st.replace('#7A4E34', '#EBC672')
styles.write_text(st, encoding="utf-8")

# App icon: crescent + seated cat, softer and more refined than the previous version.
icon = root / "app/src/main/res/drawable/ic_launcher_recipe.xml"
icon.write_text(r'''<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <path android:fillColor="#081026" android:pathData="M0,0h108v108h-108z"/>
    <path android:fillColor="#F8E5AD" android:pathData="M17,17l1.8,4.2 4.2,1.8 -4.2,1.8 -1.8,4.2 -1.8,-4.2 -4.2,-1.8 4.2,-1.8z"/>
    <path android:fillColor="#F8E5AD" android:pathData="M89,25l1.2,2.9 2.9,1.2 -2.9,1.2 -1.2,2.9 -1.2,-2.9 -2.9,-1.2 2.9,-1.2z"/>
    <path android:fillColor="#EBC672" android:pathData="M65,12 A35,35 0,1 0,65,96 A35,35 0,1 0,65,12 Z"/>
    <path android:fillColor="#081026" android:pathData="M75,16 A31,31 0,1 0,75,92 A31,31 0,1 0,75,16 Z"/>
    <path
        android:fillColor="@android:color/transparent"
        android:strokeColor="#FFF5D8"
        android:strokeWidth="2.1"
        android:strokeLineCap="round"
        android:strokeLineJoin="round"
        android:pathData="M42,62 C37,57 37,49 41,45 L40,36 L48,42 L54,36 L55,45 C61,50 61,58 56,63 C62,68 64,76 61,83 C52,88 43,86 39,79 C36,73 37,67 42,62 M39,79 C30,80 27,87 31,92 C35,97 44,95 47,88"/>
</vector>
''', encoding="utf-8")

# Version above the already-shipped v1.2.0.
gradle = root / "app/build.gradle"
g = gradle.read_text(encoding="utf-8")
old_v = "versionCode 11\n        versionName '1.1.7'"
new_v = "versionCode 13\n        versionName '1.2.1'"
if old_v not in g:
    raise SystemExit("v1.1.7 version marker not found")
g = g.replace(old_v, new_v)
gradle.write_text(g, encoding="utf-8")
