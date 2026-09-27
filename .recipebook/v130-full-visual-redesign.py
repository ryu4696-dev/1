from pathlib import Path

root = Path("recipe-book")
java = root / "app/src/main/java/dev/ryu4696/recipebook/MainActivity.java"
s = java.read_text(encoding="utf-8")

# ---------- imports ----------
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

# ---------- palette ----------
old_colors = """    private static final int BG = Color.rgb(255, 248, 242);
    private static final int CARD = Color.WHITE;
    private static final int INK = Color.rgb(48, 38, 32);
    private static final int MUTED = Color.rgb(110, 96, 86);
    private static final int ACCENT = Color.rgb(122, 78, 52);
    private static final int ACCENT_LIGHT = Color.rgb(241, 226, 214);
    private static final int DANGER = Color.rgb(162, 54, 54);
    private static final int BORDER = Color.rgb(226, 214, 205);
"""
new_colors = """    // MariRecipe illustrated-night palette.
    private static final int BG = Color.rgb(7, 15, 34);
    private static final int CARD = Color.rgb(17, 37, 68);
    private static final int CARD_2 = Color.rgb(24, 48, 83);
    private static final int INPUT_BG = Color.rgb(12, 28, 52);
    private static final int INK = Color.rgb(255, 248, 232);
    private static final int MUTED = Color.rgb(186, 199, 222);
    private static final int ACCENT = Color.rgb(234, 195, 108);
    private static final int ACCENT_2 = Color.rgb(197, 177, 219);
    private static final int ACCENT_LIGHT = Color.rgb(37, 54, 90);
    private static final int DANGER = Color.rgb(226, 126, 139);
    private static final int BORDER = Color.rgb(82, 104, 145);
    private static final int GOLD_TEXT = Color.rgb(255, 232, 176);
    private static final int PRIMARY_INK = Color.rgb(29, 35, 53);
"""
if old_colors not in s:
    raise SystemExit("base color block not found")
s = s.replace(old_colors, new_colors, 1)

# ---------- home copy ----------
old_lead = """        TextView lead = text("菓子レシピと原価を、見る画面と入力画面を混ぜずに管理します。", 14, MUTED);
        lead.setPadding(0, 0, 0, dp(10));
        page.addView(lead);

"""
if old_lead not in s:
    raise SystemExit("home lead copy block not found")
s = s.replace(old_lead, "", 1)

# ---------- page/background ----------
s = s.replace("        page.setBackgroundColor(BG);\n", "        page.setBackgroundColor(Color.TRANSPARENT);\n", 1)
s = s.replace("        s.setBackgroundColor(BG);\n", "        s.setBackground(new NightSkyDrawable(currentScreen));\n", 1)

# ---------- top bar branding ----------
old_top_title = """        TextView t = text(title, 22, INK);
        t.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        t.setGravity(Gravity.START | Gravity.CENTER_VERTICAL);
        t.setSingleLine(true);
        t.setEllipsize(TextUtils.TruncateAt.END);
        t.setLayoutParams(new LinearLayout.LayoutParams(0, dp(52), 1f));
        bar.addView(t);
"""
new_top_title = """        TextView t;
        if ("MariRecipe".equals(title)) {
            t = new BrandTitleView();
            t.setText(title);
        } else {
            t = text(title, 22, INK);
            t.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        }
        t.setGravity(Gravity.START | Gravity.CENTER_VERTICAL);
        t.setSingleLine(true);
        t.setEllipsize(TextUtils.TruncateAt.END);
        t.setLayoutParams(new LinearLayout.LayoutParams(0, dp(52), 1f));
        bar.addView(t);
"""
if old_top_title not in s:
    raise SystemExit("topBar title block not found")
s = s.replace(old_top_title, new_top_title, 1)

# ---------- headings ----------
old_section = """    private TextView sectionTitle(String s) {
        TextView t = text(s, 19, INK);
        t.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        t.setPadding(0, dp(2), 0, dp(8));
        return t;
    }
"""
new_section = """    private TextView sectionTitle(String s) {
        TextView t = text(s, 19, GOLD_TEXT);
        t.setTypeface(Typeface.SERIF, Typeface.BOLD);
        t.setPadding(0, dp(2), 0, dp(8));
        return t;
    }
"""
if old_section not in s:
    raise SystemExit("sectionTitle block not found")
s = s.replace(old_section, new_section, 1)

# ---------- inputs ----------
s = s.replace(
    "        e.setHintTextColor(Color.rgb(160, 145, 136));\n",
    "        e.setHintTextColor(Color.rgb(137, 157, 190));\n",
    1
)
s = s.replace(
    "        e.setBackground(round(Color.WHITE, 11, BORDER, 1));\n",
    "        e.setBackground(new NightInputDrawable());\n",
    1
)

old_spinner = """    private Spinner spinner(String[] values) {
        Spinner s = new Spinner(this);
        ArrayAdapter<String> a = new ArrayAdapter<>(this, android.R.layout.simple_spinner_dropdown_item, values);
        s.setAdapter(a);
        s.setBackground(round(Color.WHITE, 11, BORDER, 1));
        s.setPadding(dp(8), 0, dp(8), 0);
        s.setLayoutParams(new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(48)));
        return s;
    }
"""
new_spinner = """    private Spinner spinner(String[] values) {
        Spinner s = new Spinner(this);
        ArrayAdapter<String> a = new ArrayAdapter<String>(this, android.R.layout.simple_spinner_dropdown_item, values) {
            @Override
            public View getView(int position, View convertView, ViewGroup parent) {
                TextView v = (TextView) super.getView(position, convertView, parent);
                v.setTextColor(INK);
                v.setTextSize(16);
                return v;
            }

            @Override
            public View getDropDownView(int position, View convertView, ViewGroup parent) {
                TextView v = (TextView) super.getDropDownView(position, convertView, parent);
                v.setTextColor(INK);
                v.setBackgroundColor(CARD_2);
                v.setPadding(dp(12), dp(10), dp(12), dp(10));
                return v;
            }
        };
        s.setAdapter(a);
        s.setBackground(new NightInputDrawable());
        s.setPadding(dp(8), 0, dp(8), 0);
        s.setLayoutParams(new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(48)));
        return s;
    }
"""
if old_spinner not in s:
    raise SystemExit("spinner block not found")
s = s.replace(old_spinner, new_spinner, 1)

# ---------- buttons ----------
old_selected = """        b.setTextColor(ACCENT);
        b.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        b.setBackground(round(ACCENT_LIGHT, 11, ACCENT, 2));
"""
new_selected = """        b.setTextColor(GOLD_TEXT);
        b.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        b.setBackground(new NightButtonDrawable(3));
"""
if old_selected not in s:
    raise SystemExit("selected button style not found")
s = s.replace(old_selected, new_selected, 1)

old_primary = """        b.setTextColor(Color.WHITE);
        b.setBackground(round(ACCENT, 11));
"""
new_primary = """        b.setTextColor(PRIMARY_INK);
        b.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        b.setBackground(new NightButtonDrawable(1));
"""
if old_primary not in s:
    raise SystemExit("primary button style not found")
s = s.replace(old_primary, new_primary, 1)

old_secondary = """        b.setTextColor(ACCENT);
        b.setBackground(round(Color.WHITE, 11, ACCENT, 1));
"""
new_secondary = """        b.setTextColor(GOLD_TEXT);
        b.setBackground(new NightButtonDrawable(0));
"""
if old_secondary not in s:
    raise SystemExit("secondary button style not found")
s = s.replace(old_secondary, new_secondary, 1)

old_danger = """        b.setTextColor(DANGER);
        b.setBackground(round(Color.WHITE, 11, DANGER, 1));
"""
new_danger = """        b.setTextColor(Color.rgb(255, 214, 219));
        b.setBackground(new NightButtonDrawable(2));
"""
if old_danger not in s:
    raise SystemExit("danger button style not found")
s = s.replace(old_danger, new_danger, 1)

# ---------- cards ----------
s = s.replace("        c.setBackground(round(CARD, 15, BORDER, 1));\n", "        c.setBackground(new NightCardDrawable(15));\n", 1)
s = s.replace("        c.setBackground(round(CARD, 12, BORDER, 1));\n", "        c.setBackground(new NightCardDrawable(12));\n", 1)
s = s.replace(
    "        image.setBackgroundColor(Color.rgb(238, 234, 231));\n",
    "        image.setBackgroundColor(Color.rgb(16, 36, 64));\n",
    1
)

# ---------- dedicated visual classes ----------
marker = """    private LinearLayout page() {
"""
visual_code = r'''    private class BrandTitleView extends TextView {
        private final Paint decor = new Paint(Paint.ANTI_ALIAS_FLAG);

        BrandTitleView() {
            super(MainActivity.this);
            setTextColor(GOLD_TEXT);
            setTextSize(27);
            setTypeface(Typeface.SERIF, Typeface.BOLD_ITALIC);
            setPadding(dp(28), 0, dp(20), 0);
        }

        @Override
        protected void onDraw(Canvas canvas) {
            float d = getResources().getDisplayMetrics().density;
            decor.setStyle(Paint.Style.STROKE);
            decor.setStrokeCap(Paint.Cap.ROUND);
            decor.setStrokeWidth(1.7f * d);
            decor.setColor(Color.rgb(239, 201, 117));

            RectF moon = new RectF(1*d, getHeight()*0.26f, 21*d, getHeight()*0.72f);
            canvas.drawArc(moon, 74, 224, false, decor);

            decor.setStyle(Paint.Style.FILL);
            decor.setColor(Color.argb(190, 255, 232, 174));
            float sx = Math.max(0, getWidth() - 11*d);
            float sy = getHeight()*0.28f;
            canvas.drawCircle(sx, sy, 1.3f*d, decor);
            decor.setStrokeWidth(0.7f*d);
            decor.setStyle(Paint.Style.STROKE);
            canvas.drawLine(sx-4*d, sy, sx+4*d, sy, decor);
            canvas.drawLine(sx, sy-4*d, sx, sy+4*d, decor);

            super.onDraw(canvas);
        }
    }

    private class NightCardDrawable extends Drawable {
        private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
        private final Paint line = new Paint(Paint.ANTI_ALIAS_FLAG);
        private final float radius;

        NightCardDrawable(int radiusDp) {
            radius = dp(radiusDp);
        }

        @Override
        public void draw(Canvas canvas) {
            android.graphics.Rect b = getBounds();
            RectF r = new RectF(b.left, b.top, b.right, b.bottom);

            paint.setShader(new LinearGradient(
                    b.left, b.top, b.right, b.bottom,
                    new int[]{
                            Color.rgb(28, 53, 91),
                            Color.rgb(17, 36, 67),
                            Color.rgb(14, 29, 55)
                    },
                    null,
                    Shader.TileMode.CLAMP));
            canvas.drawRoundRect(r, radius, radius, paint);
            paint.setShader(null);

            // Soft moonlight glaze.
            paint.setColor(Color.argb(18, 255, 224, 158));
            canvas.drawRoundRect(new RectF(
                    b.left + dp(1),
                    b.top + dp(1),
                    b.right - dp(1),
                    b.top + Math.max(dp(24), b.height()*0.30f)),
                    radius, radius, paint);

            line.setStyle(Paint.Style.STROKE);
            line.setStrokeWidth(dp(1));
            line.setColor(BORDER);
            canvas.drawRoundRect(new RectF(
                    b.left + dp(0.5f), b.top + dp(0.5f),
                    b.right - dp(0.5f), b.bottom - dp(0.5f)),
                    radius, radius, line);

            // Small gold corner-star, enough to brand the surface without becoming wallpaper.
            float x = b.right - dp(15);
            float y = b.top + dp(15);
            line.setColor(Color.argb(120, 242, 204, 124));
            line.setStrokeWidth(dp(0.8f));
            canvas.drawLine(x-dp(4), y, x+dp(4), y, line);
            canvas.drawLine(x, y-dp(4), x, y+dp(4), line);
        }

        @Override public void setAlpha(int alpha) { }
        @Override public void setColorFilter(android.graphics.ColorFilter colorFilter) { }
        @Override public int getOpacity() { return android.graphics.PixelFormat.TRANSLUCENT; }
    }

    private class NightInputDrawable extends Drawable {
        private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
        private final Paint line = new Paint(Paint.ANTI_ALIAS_FLAG);

        @Override
        public void draw(Canvas canvas) {
            android.graphics.Rect b = getBounds();
            RectF r = new RectF(b.left, b.top, b.right, b.bottom);
            float radius = dp(11);

            paint.setShader(new LinearGradient(
                    b.left, b.top, b.left, b.bottom,
                    new int[]{Color.rgb(17, 37, 68), INPUT_BG},
                    null,
                    Shader.TileMode.CLAMP));
            canvas.drawRoundRect(r, radius, radius, paint);
            paint.setShader(null);

            line.setStyle(Paint.Style.STROKE);
            line.setStrokeWidth(dp(1));
            line.setColor(BORDER);
            canvas.drawRoundRect(new RectF(
                    b.left+dp(0.5f), b.top+dp(0.5f),
                    b.right-dp(0.5f), b.bottom-dp(0.5f)),
                    radius, radius, line);
        }

        @Override public void setAlpha(int alpha) { }
        @Override public void setColorFilter(android.graphics.ColorFilter colorFilter) { }
        @Override public int getOpacity() { return android.graphics.PixelFormat.TRANSLUCENT; }
    }

    private class NightButtonDrawable extends Drawable {
        // 0 secondary, 1 primary, 2 danger, 3 selected
        private final int kind;
        private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
        private final Paint line = new Paint(Paint.ANTI_ALIAS_FLAG);

        NightButtonDrawable(int kind) {
            this.kind = kind;
        }

        @Override
        public void draw(Canvas canvas) {
            android.graphics.Rect b = getBounds();
            RectF r = new RectF(b.left, b.top, b.right, b.bottom);
            float radius = dp(11);

            int[] colors;
            int border;
            if (kind == 1) {
                colors = new int[]{Color.rgb(250, 217, 145), Color.rgb(225, 181, 91)};
                border = Color.rgb(255, 232, 176);
            } else if (kind == 2) {
                colors = new int[]{Color.rgb(68, 40, 57), Color.rgb(32, 32, 57)};
                border = DANGER;
            } else if (kind == 3) {
                colors = new int[]{Color.rgb(54, 68, 107), Color.rgb(31, 47, 83)};
                border = ACCENT;
            } else {
                colors = new int[]{Color.rgb(29, 50, 84), Color.rgb(14, 30, 56)};
                border = ACCENT;
            }

            paint.setShader(new LinearGradient(
                    b.left, b.top, b.left, b.bottom,
                    colors, null, Shader.TileMode.CLAMP));
            canvas.drawRoundRect(r, radius, radius, paint);
            paint.setShader(null);

            line.setStyle(Paint.Style.STROKE);
            line.setStrokeWidth(dp(kind == 3 ? 2f : 1f));
            line.setColor(border);
            canvas.drawRoundRect(new RectF(
                    b.left+dp(0.5f), b.top+dp(0.5f),
                    b.right-dp(0.5f), b.bottom-dp(0.5f)),
                    radius, radius, line);

            // Primary/selected get one restrained sparkle.
            if (kind == 1 || kind == 3) {
                float x = b.right - dp(10);
                float y = b.top + dp(9);
                line.setStrokeWidth(dp(0.7f));
                line.setColor(Color.argb(120, 255, 246, 215));
                canvas.drawLine(x-dp(2.5f), y, x+dp(2.5f), y, line);
                canvas.drawLine(x, y-dp(2.5f), x, y+dp(2.5f), line);
            }
        }

        @Override public void setAlpha(int alpha) { }
        @Override public void setColorFilter(android.graphics.ColorFilter colorFilter) { }
        @Override public int getOpacity() { return android.graphics.PixelFormat.TRANSLUCENT; }
    }

    private class NightSkyDrawable extends Drawable {
        private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
        private final Paint line = new Paint(Paint.ANTI_ALIAS_FLAG);
        private final String screen;

        NightSkyDrawable(String screen) {
            this.screen = screen == null ? "" : screen;
        }

        @Override
        public void draw(Canvas canvas) {
            android.graphics.Rect b = getBounds();
            float w = Math.max(1f, b.width());
            float h = Math.max(1f, b.height());
            float d = getResources().getDisplayMetrics().density;

            paint.setShader(new LinearGradient(
                    0, 0, 0, h,
                    new int[]{
                            Color.rgb(5, 13, 31),
                            Color.rgb(9, 24, 52),
                            Color.rgb(15, 36, 68)
                    },
                    new float[]{0f, 0.56f, 1f},
                    Shader.TileMode.CLAMP));
            canvas.drawRect(b, paint);
            paint.setShader(null);

            // Soft painted mist/cloud masses.
            paint.setColor(Color.argb(18, 119, 145, 205));
            canvas.drawCircle(w*0.10f, h*0.17f, w*0.24f, paint);
            canvas.drawCircle(w*0.28f, h*0.20f, w*0.18f, paint);
            canvas.drawCircle(w*0.84f, h*0.28f, w*0.29f, paint);
            paint.setColor(Color.argb(12, 183, 154, 216));
            canvas.drawCircle(w*0.60f, h*0.72f, w*0.34f, paint);

            // Fine stars.
            int stars = "edit".equals(screen) ? 70 : 112;
            for (int i = 0; i < stars; i++) {
                float x = ((i * 53 + 17) % 223) / 223f * w;
                float y = ((i * 79 + 23) % 337) / 337f * h;
                boolean hero = i % 19 == 0;
                boolean medium = i % 7 == 0;
                float rr = (hero ? 1.7f : (medium ? 1.0f : 0.52f)) * d;
                int alpha = hero ? 190 : (medium ? 112 : 62);
                paint.setColor(Color.argb(alpha, 255, 238, 196));
                canvas.drawCircle(x, y, rr, paint);
                if (hero) {
                    line.setColor(Color.argb(100, 255, 231, 174));
                    line.setStrokeWidth(0.75f*d);
                    canvas.drawLine(x-3.6f*d, y, x+3.6f*d, y, line);
                    canvas.drawLine(x, y-3.6f*d, x, y+3.6f*d, line);
                }
            }

            // Decorative shooting-star curve.
            line.setStyle(Paint.Style.STROKE);
            line.setStrokeCap(Paint.Cap.ROUND);
            line.setStrokeWidth(0.95f*d);
            line.setColor(Color.argb(82, 246, 211, 136));
            Path arc = new Path();
            arc.moveTo(w*0.16f, h*0.12f);
            arc.quadTo(w*0.42f, h*0.072f, w*0.67f, h*0.155f);
            canvas.drawPath(arc, line);

            if ("home".equals(screen)) {
                drawMoonCat(canvas, w, h, d, 0.79f, 0.135f, 1.0f);
                drawCity(canvas, w, h, d, 0.88f);
                drawLanternGlow(canvas, w*0.16f, h*0.82f, d);
                drawLanternGlow(canvas, w*0.86f, h*0.80f, d);
            } else if ("view".equals(screen)) {
                drawMoonCat(canvas, w, h, d, 0.81f, 0.10f, 0.82f);
                drawCity(canvas, w, h, d, 0.93f);
            } else if ("materials".equals(screen)) {
                drawMoonPhases(canvas, w, h, d);
            } else if ("edit".equals(screen)) {
                // Editing stays calmer so controls remain the focus.
                drawTinyConstellation(canvas, w, h, d);
            } else {
                drawMoonCat(canvas, w, h, d, 0.83f, 0.11f, 0.62f);
            }
        }

        private void drawMoonCat(Canvas canvas, float w, float h, float d, float px, float py, float scale) {
            line.setStyle(Paint.Style.STROKE);
            line.setStrokeCap(Paint.Cap.ROUND);
            line.setStrokeWidth(2.0f*d*scale);
            line.setColor(Color.argb(96, 241, 198, 111));

            float cx = w*px;
            float cy = h*py;
            RectF moon = new RectF(
                    cx - 46*d*scale, cy - 48*d*scale,
                    cx + 46*d*scale, cy + 48*d*scale);
            canvas.drawArc(moon, 72, 220, false, line);

            Path cat = new Path();
            float ox = cx + 4*d*scale;
            float oy = cy + 7*d*scale;
            float sc = scale*d;
            cat.moveTo(ox, oy);
            cat.cubicTo(ox-8*sc, oy-6*sc, ox-8*sc, oy-17*sc, ox-2*sc, oy-23*sc);
            cat.lineTo(ox-4*sc, oy-33*sc);
            cat.lineTo(ox+4*sc, oy-27*sc);
            cat.lineTo(ox+12*sc, oy-34*sc);
            cat.lineTo(ox+12*sc, oy-23*sc);
            cat.cubicTo(ox+20*sc, oy-17*sc, ox+20*sc, oy-6*sc, ox+13*sc, oy+1*sc);
            cat.cubicTo(ox+22*sc, oy+10*sc, ox+22*sc, oy+31*sc, ox+16*sc, oy+42*sc);
            cat.cubicTo(ox+4*sc, oy+48*sc, ox-8*sc, oy+43*sc, ox-10*sc, oy+30*sc);
            cat.cubicTo(ox-11*sc, oy+18*sc, ox-7*sc, oy+7*sc, ox, oy);
            cat.moveTo(ox-8*sc, oy+33*sc);
            cat.cubicTo(ox-22*sc, oy+34*sc, ox-28*sc, oy+47*sc, ox-21*sc, oy+56*sc);
            cat.cubicTo(ox-14*sc, oy+63*sc, ox-4*sc, oy+58*sc, ox+1*sc, oy+50*sc);
            line.setStrokeWidth(1.25f*d*scale);
            line.setColor(Color.argb(76, 255, 242, 213));
            canvas.drawPath(cat, line);
        }

        private void drawCity(Canvas canvas, float w, float h, float d, float top) {
            paint.setColor(Color.argb(84, 5, 10, 24));
            Path city = new Path();
            city.moveTo(0, h);
            city.lineTo(0, h*top);
            float[] xs = {0.04f,0.09f,0.14f,0.20f,0.27f,0.33f,0.39f,0.46f,0.53f,0.61f,0.68f,0.75f,0.82f,0.89f,0.95f,1f};
            float[] ys = {0.97f,0.90f,0.98f,0.94f,0.99f,0.87f,0.95f,0.92f,1.00f,0.91f,0.96f,0.88f,0.98f,0.93f,0.99f,0.95f};
            for (int i=0; i<xs.length; i++) {
                float yy = Math.min(h, h*top + h*0.10f*(ys[i]-0.87f)/0.13f);
                city.lineTo(w*xs[i], yy);
            }
            city.lineTo(w, h);
            city.close();
            canvas.drawPath(city, paint);

            // Warm lit windows, tiny and sparse.
            paint.setColor(Color.argb(85, 244, 190, 92));
            for (int i=0;i<12;i++) {
                float x = ((i*79+21)%100)/100f*w;
                float y = h*(top + 0.025f + (i%3)*0.018f);
                canvas.drawRect(x, y, x+1.3f*d, y+2.2f*d, paint);
            }
        }

        private void drawLanternGlow(Canvas canvas, float x, float y, float d) {
            paint.setColor(Color.argb(28, 255, 190, 79));
            canvas.drawCircle(x, y, 26*d, paint);
            paint.setColor(Color.argb(46, 255, 211, 112));
            canvas.drawCircle(x, y, 10*d, paint);
        }

        private void drawMoonPhases(Canvas canvas, float w, float h, float d) {
            line.setStyle(Paint.Style.STROKE);
            line.setStrokeWidth(1.2f*d);
            line.setColor(Color.argb(72, 238, 200, 118));
            float y = h*0.11f;
            for (int i=0;i<5;i++) {
                float x = w*(0.63f + i*0.065f);
                canvas.drawCircle(x, y, 7*d, line);
                if (i<4) canvas.drawLine(x+9*d, y, x+15*d, y, line);
            }
        }

        private void drawTinyConstellation(Canvas canvas, float w, float h, float d) {
            line.setStyle(Paint.Style.STROKE);
            line.setStrokeWidth(0.8f*d);
            line.setColor(Color.argb(68, 210, 194, 230));
            float x1=w*0.73f, y1=h*0.105f;
            float x2=w*0.79f, y2=h*0.085f;
            float x3=w*0.85f, y3=h*0.12f;
            float x4=w*0.91f, y4=h*0.095f;
            canvas.drawLine(x1,y1,x2,y2,line);
            canvas.drawLine(x2,y2,x3,y3,line);
            canvas.drawLine(x3,y3,x4,y4,line);
            paint.setColor(Color.argb(100, 226, 205, 239));
            canvas.drawCircle(x1,y1,1.4f*d,paint);
            canvas.drawCircle(x2,y2,1.2f*d,paint);
            canvas.drawCircle(x3,y3,1.5f*d,paint);
            canvas.drawCircle(x4,y4,1.2f*d,paint);
        }

        @Override public void setAlpha(int alpha) { }
        @Override public void setColorFilter(android.graphics.ColorFilter colorFilter) { }
        @Override public int getOpacity() { return android.graphics.PixelFormat.OPAQUE; }
    }

'''
if marker not in s:
    raise SystemExit("page marker not found")
s = s.replace(marker, visual_code + marker, 1)

java.write_text(s, encoding="utf-8")

# ---------- theme ----------
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
st = st.replace('#FFF8F2', '#071022')
st = st.replace('#7A4E34', '#EAC36C')
styles.write_text(st, encoding="utf-8")

# ---------- launcher icon ----------
icon = root / "app/src/main/res/drawable/ic_launcher_recipe.xml"
icon.write_text(r'''<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <path android:fillColor="#071022" android:pathData="M0,0h108v108h-108z"/>
    <path android:fillColor="#102A50" android:pathData="M0,70 C25,52 55,82 108,55 L108,108 L0,108 Z"/>
    <path android:fillColor="#F7E3AA" android:pathData="M18,17l1.8,4.2 4.2,1.8 -4.2,1.8 -1.8,4.2 -1.8,-4.2 -4.2,-1.8 4.2,-1.8z"/>
    <path android:fillColor="#F7E3AA" android:pathData="M89,25l1.2,2.9 2.9,1.2 -2.9,1.2 -1.2,2.9 -1.2,-2.9 -2.9,-1.2 2.9,-1.2z"/>
    <path android:fillColor="#EAC36C" android:pathData="M65,12 A35,35 0,1 0,65,96 A35,35 0,1 0,65,12 Z"/>
    <path android:fillColor="#071022" android:pathData="M75,16 A31,31 0,1 0,75,92 A31,31 0,1 0,75,16 Z"/>
    <path
        android:fillColor="@android:color/transparent"
        android:strokeColor="#FFF5D8"
        android:strokeWidth="2.1"
        android:strokeLineCap="round"
        android:strokeLineJoin="round"
        android:pathData="M42,62 C37,57 37,49 41,45 L40,36 L48,42 L54,36 L55,45 C61,50 61,58 56,63 C62,68 64,76 61,83 C52,88 43,86 39,79 C36,73 37,67 42,62 M39,79 C30,80 27,87 31,92 C35,97 44,95 47,88"/>
</vector>
''', encoding="utf-8")

# ---------- version ----------
gradle = root / "app/build.gradle"
g = gradle.read_text(encoding="utf-8")
old_v = "versionCode 11\n        versionName '1.1.7'"
new_v = "versionCode 14\n        versionName '1.3.0'"
if old_v not in g:
    raise SystemExit("v1.1.7 version marker not found")
g = g.replace(old_v, new_v)
gradle.write_text(g, encoding="utf-8")
