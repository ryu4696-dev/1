from pathlib import Path
import re

root = Path("recipe-book")
java = root / "app/src/main/java/dev/ryu4696/recipebook/MainActivity.java"
s = java.read_text(encoding="utf-8")

# Drawing imports for a lightweight starry-night background. No layout changes.
imports = {
    "import android.graphics.Color;\n": """import android.graphics.Color;
import android.graphics.Canvas;
import android.graphics.LinearGradient;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.RectF;
import android.graphics.Shader;
""",
    "import android.graphics.drawable.GradientDrawable;\n": """import android.graphics.drawable.GradientDrawable;
import android.graphics.drawable.Drawable;
"""
}
for old, new in imports.items():
    if old in s and new not in s:
        s = s.replace(old, new, 1)

old_colors = """    private static final int BG = Color.rgb(255, 248, 242);
    private static final int CARD = Color.WHITE;
    private static final int INK = Color.rgb(48, 38, 32);
    private static final int MUTED = Color.rgb(110, 96, 86);
    private static final int ACCENT = Color.rgb(122, 78, 52);
    private static final int ACCENT_LIGHT = Color.rgb(241, 226, 214);
    private static final int DANGER = Color.rgb(162, 54, 54);
    private static final int BORDER = Color.rgb(226, 214, 205);
"""
new_colors = """    // MariRecipe Night theme: layout is unchanged; only visual language is replaced.
    private static final int BG = Color.rgb(6, 18, 39);
    private static final int CARD = Color.rgb(14, 38, 72);
    private static final int INPUT_BG = Color.rgb(10, 31, 61);
    private static final int INK = Color.rgb(249, 239, 215);
    private static final int MUTED = Color.rgb(174, 190, 216);
    private static final int ACCENT = Color.rgb(242, 198, 105);
    private static final int ACCENT_LIGHT = Color.rgb(35, 55, 92);
    private static final int DANGER = Color.rgb(224, 118, 128);
    private static final int BORDER = Color.rgb(68, 91, 132);
    private static final int PRIMARY_INK = Color.rgb(22, 31, 51);
"""
if old_colors not in s:
    raise SystemExit("color block not found")
s = s.replace(old_colors, new_colors, 1)

# Let the ScrollView's illustrated background show through without changing spacing/layout.
s = s.replace("        page.setBackgroundColor(BG);\n", "        page.setBackgroundColor(Color.TRANSPARENT);\n", 1)
s = s.replace("        s.setBackgroundColor(BG);\n", "        s.setBackground(new NightSkyDrawable());\n", 1)

# Dark-night form controls.
s = s.replace("        e.setHintTextColor(Color.rgb(160, 145, 136));\n",
              "        e.setHintTextColor(Color.rgb(116, 139, 176));\n", 1)
s = s.replace("        e.setBackground(round(Color.WHITE, 11, BORDER, 1));\n",
              "        e.setBackground(round(INPUT_BG, 11, BORDER, 1));\n", 1)
s = s.replace("        s.setBackground(round(Color.WHITE, 11, BORDER, 1));\n",
              "        s.setBackground(round(INPUT_BG, 11, BORDER, 1));\n", 1)

# Buttons: moon-gold primary, navy secondary, lavender/red danger.
s = s.replace("        b.setTextColor(Color.WHITE);\n        b.setBackground(round(ACCENT, 11));\n",
              "        b.setTextColor(PRIMARY_INK);\n        b.setTypeface(Typeface.DEFAULT, Typeface.BOLD);\n        b.setBackground(round(ACCENT, 11, Color.rgb(255, 225, 158), 1));\n", 1)
s = s.replace("        b.setBackground(round(Color.WHITE, 11, ACCENT, 1));\n",
              "        b.setBackground(round(INPUT_BG, 11, ACCENT, 1));\n", 1)
s = s.replace("        b.setBackground(round(Color.WHITE, 11, DANGER, 1));\n",
              "        b.setBackground(round(INPUT_BG, 11, DANGER, 1));\n", 1)

# Selected tabs read as selected without looking like an action button.
s = s.replace("        b.setTextColor(ACCENT);\n        b.setTypeface(Typeface.DEFAULT, Typeface.BOLD);\n        b.setBackground(round(ACCENT_LIGHT, 11, ACCENT, 2));\n",
              "        b.setTextColor(Color.rgb(255, 232, 176));\n        b.setTypeface(Typeface.DEFAULT, Typeface.BOLD);\n        b.setBackground(round(ACCENT_LIGHT, 11, ACCENT, 2));\n", 1)

s = s.replace("        image.setBackgroundColor(Color.rgb(238, 234, 231));\n",
              "        image.setBackgroundColor(Color.rgb(16, 39, 69));\n", 1)

# Insert a subtle, deterministic night-sky + crescent + cat line-art background.
marker = """    private LinearLayout page() {
"""
night_drawable = r'''    private class NightSkyDrawable extends Drawable {
        private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
        private final Paint line = new Paint(Paint.ANTI_ALIAS_FLAG);

        @Override
        public void draw(Canvas canvas) {
            android.graphics.Rect b = getBounds();
            float w = Math.max(1, b.width());
            float h = Math.max(1, b.height());

            paint.setShader(new LinearGradient(
                    0, 0, 0, h,
                    new int[] {
                            Color.rgb(4, 15, 34),
                            Color.rgb(8, 28, 58),
                            Color.rgb(11, 34, 66)
                    },
                    new float[] {0f, 0.52f, 1f},
                    Shader.TileMode.CLAMP));
            canvas.drawRect(b, paint);
            paint.setShader(null);

            // Tiny stars. Formula is deterministic so the pattern does not jump between frames.
            for (int i = 0; i < 86; i++) {
                float x = ((i * 37 + 11) % 101) / 101f * w;
                float y = ((i * 61 + 17) % 127) / 127f * h;
                float r = (i % 11 == 0 ? 2.2f : (i % 4 == 0 ? 1.3f : 0.75f)) * getResources().getDisplayMetrics().density;
                int alpha = i % 11 == 0 ? 185 : (i % 4 == 0 ? 125 : 78);
                paint.setColor(Color.argb(alpha, 255, 232, 178));
                canvas.drawCircle(x, y, r, paint);
            }

            // Faint crescent watermark in the upper-right. Decorative only, never changes layout.
            line.setStyle(Paint.Style.STROKE);
            line.setStrokeCap(Paint.Cap.ROUND);
            line.setStrokeWidth(2.2f * getResources().getDisplayMetrics().density);
            line.setColor(Color.argb(92, 244, 201, 112));
            RectF moon = new RectF(w * 0.72f, h * 0.035f, w * 0.98f, h * 0.19f);
            canvas.drawArc(moon, 72, 222, false, line);
            RectF moonInner = new RectF(w * 0.755f, h * 0.047f, w * 0.985f, h * 0.178f);
            line.setColor(Color.argb(55, 244, 201, 112));
            canvas.drawArc(moonInner, 82, 202, false, line);

            // Minimal cat line-art seated by the crescent.
            float ox = w * 0.805f;
            float oy = h * 0.115f;
            float sc = Math.min(w / 420f, h / 900f);
            Path cat = new Path();
            cat.moveTo(ox, oy);
            cat.cubicTo(ox - 10*sc, oy - 7*sc, ox - 10*sc, oy - 18*sc, ox - 4*sc, oy - 24*sc);
            cat.lineTo(ox - 6*sc, oy - 34*sc);
            cat.lineTo(ox + 3*sc, oy - 28*sc);
            cat.lineTo(ox + 11*sc, oy - 35*sc);
            cat.lineTo(ox + 12*sc, oy - 24*sc);
            cat.cubicTo(ox + 20*sc, oy - 18*sc, ox + 19*sc, oy - 7*sc, ox + 12*sc, oy);
            cat.cubicTo(ox + 22*sc, oy + 10*sc, ox + 23*sc, oy + 31*sc, ox + 17*sc, oy + 43*sc);
            cat.cubicTo(ox + 4*sc, oy + 49*sc, ox - 9*sc, oy + 43*sc, ox - 11*sc, oy + 30*sc);
            cat.cubicTo(ox - 12*sc, oy + 18*sc, ox - 7*sc, oy + 7*sc, ox, oy);
            cat.moveTo(ox - 8*sc, oy + 34*sc);
            cat.cubicTo(ox - 23*sc, oy + 34*sc, ox - 29*sc, oy + 47*sc, ox - 22*sc, oy + 56*sc);
            cat.cubicTo(ox - 15*sc, oy + 64*sc, ox - 3*sc, oy + 58*sc, ox + 1*sc, oy + 50*sc);

            line.setStrokeWidth(1.5f * getResources().getDisplayMetrics().density);
            line.setColor(Color.argb(68, 255, 239, 202));
            canvas.drawPath(cat, line);
        }

        @Override public void setAlpha(int alpha) { }
        @Override public void setColorFilter(android.graphics.ColorFilter colorFilter) { }
        @Override public int getOpacity() { return android.graphics.PixelFormat.OPAQUE; }
    }

'''
if marker not in s:
    raise SystemExit("page marker not found")
s = s.replace(marker, night_drawable + marker, 1)

java.write_text(s, encoding="utf-8")

# Dark system chrome. Keep the exact same app layout.
styles = root / "app/src/main/res/values/styles.xml"
st = styles.read_text(encoding="utf-8")
st = st.replace('parent="android:style/Theme.Material.Light.NoActionBar"',
                'parent="android:style/Theme.Material.NoActionBar"')
st = st.replace('<item name="android:windowLightStatusBar">true</item>',
                '<item name="android:windowLightStatusBar">false</item>')
if '<item name="android:windowLightNavigationBar">' not in st:
    st = st.replace('<item name="android:windowLightStatusBar">false</item>',
                    '<item name="android:windowLightStatusBar">false</item>\n        <item name="android:windowLightNavigationBar">false</item>')
st = st.replace('#FFF8F2', '#061227')
st = st.replace('#7A4E34', '#F2C669')
styles.write_text(st, encoding="utf-8")

# Replace launcher art with a simple moon + cat vector in the same palette.
icon = root / "app/src/main/res/drawable/ic_launcher_recipe.xml"
icon.write_text(r'''<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">

    <path
        android:fillColor="#07162D"
        android:pathData="M0,0h108v108h-108z"/>

    <!-- stars -->
    <path android:fillColor="#F7D889" android:pathData="M18,18l2,5 5,2 -5,2 -2,5 -2,-5 -5,-2 5,-2z"/>
    <path android:fillColor="#FFF0C4" android:pathData="M88,20l1.5,3.5 3.5,1.5 -3.5,1.5 -1.5,3.5 -1.5,-3.5 -3.5,-1.5 3.5,-1.5z"/>
    <path android:fillColor="#F7D889" android:pathData="M22,76l1.2,3 3,1.2 -3,1.2 -1.2,3 -1.2,-3 -3,-1.2 3,-1.2z"/>

    <!-- crescent: gold disc with navy cutout -->
    <path
        android:fillColor="#F2C669"
        android:pathData="M67,14 A38,38 0,1 0,67,94 A38,38 0,1 0,67,14 Z"/>
    <path
        android:fillColor="#07162D"
        android:pathData="M78,19 A34,34 0,1 0,78,89 A34,34 0,1 0,78,19 Z"/>

    <!-- seated cat line art -->
    <path
        android:fillColor="@android:color/transparent"
        android:strokeColor="#FFF0C4"
        android:strokeWidth="2.2"
        android:strokeLineCap="round"
        android:strokeLineJoin="round"
        android:pathData="M43,64 C38,59 38,51 42,47 L41,37 L49,43 L55,37 L56,47 C62,51 62,59 57,64 C63,69 65,77 62,84 C53,89 43,87 39,80 C36,74 38,68 43,64 M40,79 C31,79 28,86 32,92 C36,97 45,94 48,88"/>
</vector>
''', encoding="utf-8")

# Version bump for visual redesign.
gradle = root / "app/build.gradle"
g = gradle.read_text(encoding="utf-8")
old_v = "versionCode 11\n        versionName '1.1.7'"
new_v = "versionCode 12\n        versionName '1.2.0'"
if old_v not in g:
    raise SystemExit("v1.1.7 version marker not found")
g = g.replace(old_v, new_v)
gradle.write_text(g, encoding="utf-8")
