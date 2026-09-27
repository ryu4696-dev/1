from pathlib import Path

main = Path("recipe-book/app/src/main/java/dev/ryu4696/recipebook/MainActivity.java")
s = main.read_text(encoding="utf-8")

if "import android.text.TextUtils;" not in s:
    s = s.replace("import android.text.TextWatcher;\n", "import android.text.TextWatcher;\nimport android.text.TextUtils;\n")

old = '''        page.addView(sectionTitle("倍率"));
        HorizontalScrollView multScroll = new HorizontalScrollView(this);
        multScroll.setHorizontalScrollBarEnabled(false);
        LinearLayout mults = row();
        double[] ms = {0.5, 1.0, 1.5, 2.0};
        for (double m : ms) {
            Button b = Math.abs(viewMultiplier - m) < 0.0001 ? primaryButton(num(m) + "×", v -> {}) : button(num(m) + "×", v -> {});
            b.setOnClickListener(v -> { viewMultiplier = m; showRecipeView(); });
            mults.addView(b); mults.addView(gapH());
        }
        EditText custom = edit("任意倍率", true);
        custom.setText(Math.abs(viewMultiplier - 1) < 0.0001 ? "" : num(viewMultiplier));
        custom.setLayoutParams(new LinearLayout.LayoutParams(dp(110), dp(48)));
        mults.addView(custom); mults.addView(gapH());
        mults.addView(button("反映", v -> {
            double m = parseDouble(custom.getText().toString(), 0);
            if (m <= 0) toast("倍率は0より大きい数値にしてください");
            else { viewMultiplier = m; showRecipeView(); }
        }));
        multScroll.addView(mults);
        page.addView(multScroll);
        page.addView(gapV(16));
'''
new = '''        page.addView(sectionTitle("仕込み量"));
        TextView batchHint = text("基準 " + num(r.yieldQty) + r.yieldUnit + "。1/4量・半量、または作りたい個数から材料量と原価を換算します。", 13, MUTED);
        batchHint.setPadding(0, 0, 0, dp(8));
        page.addView(batchHint);

        LinearLayout batch = row();
        batch.setGravity(Gravity.CENTER_VERTICAL);

        Button quarter = Math.abs(viewMultiplier - 0.25) < 0.0001
                ? primaryButton("1/4量", v -> {})
                : button("1/4量", v -> {});
        quarter.setLayoutParams(new LinearLayout.LayoutParams(0, dp(48), 1f));
        quarter.setOnClickListener(v -> { viewMultiplier = 0.25; showRecipeView(); });
        batch.addView(quarter);
        batch.addView(gapH());

        Button half = Math.abs(viewMultiplier - 0.5) < 0.0001
                ? primaryButton("半量", v -> {})
                : button("半量", v -> {});
        half.setLayoutParams(new LinearLayout.LayoutParams(0, dp(48), 1f));
        half.setOnClickListener(v -> { viewMultiplier = 0.5; showRecipeView(); });
        batch.addView(half);
        batch.addView(gapH());

        EditText targetQty = edit("個数", true);
        targetQty.setSingleLine(true);
        targetQty.setText(num(r.yieldQty * viewMultiplier));
        targetQty.setSelectAllOnFocus(true);
        targetQty.setLayoutParams(new LinearLayout.LayoutParams(0, dp(48), 1f));
        batch.addView(targetQty);
        batch.addView(gapH());

        Button applyQty = primaryButton(r.yieldUnit + "分", v -> {
            double qty = parseDouble(targetQty.getText().toString(), 0);
            if (qty <= 0) {
                toast("作る個数を0より大きい数値で入力してください");
            } else if (r.yieldQty <= 0) {
                toast("レシピの出来上がり量を設定してください");
            } else {
                viewMultiplier = qty / r.yieldQty;
                showRecipeView();
            }
        });
        applyQty.setMinWidth(dp(54));
        applyQty.setPadding(dp(8), 0, dp(8), 0);
        batch.addView(applyQty);

        page.addView(batch);
        page.addView(gapV(16));
'''
if old not in s:
    raise SystemExit("multiplier block not found")
s = s.replace(old, new)

old2 = '''    private LinearLayout topBar(String leftText, String title, View.OnClickListener leftClick, String rightText, View.OnClickListener rightClick) {
        LinearLayout bar = row();
        bar.setPadding(0, 0, 0, dp(14));
        if (leftText != null) {
            Button b = tinyButton(leftText, leftClick);
            b.setMinWidth(dp(52));
            bar.addView(b);
        }
        TextView t = text(title, 24, INK);
        t.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        t.setGravity(Gravity.CENTER_VERTICAL);
        t.setLayoutParams(new LinearLayout.LayoutParams(0, dp(52), 1f));
        if (leftText == null) t.setGravity(Gravity.START | Gravity.CENTER_VERTICAL);
        bar.addView(t);
        if (rightText != null) {
            bar.addView(primaryButton(rightText, rightClick));
        }
        return bar;
    }
'''
new2 = '''    private LinearLayout topBar(String leftText, String title, View.OnClickListener leftClick, String rightText, View.OnClickListener rightClick) {
        LinearLayout bar = row();
        bar.setGravity(Gravity.CENTER_VERTICAL);
        bar.setPadding(0, 0, 0, dp(14));

        if (leftText != null) {
            Button b = tinyButton(leftText, leftClick);
            b.setMinWidth(dp(58));
            b.setLayoutParams(new LinearLayout.LayoutParams(dp(58), dp(48)));
            bar.addView(b);
            bar.addView(gapH());
        }

        TextView t = text(title, 22, INK);
        t.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        t.setGravity(Gravity.START | Gravity.CENTER_VERTICAL);
        t.setSingleLine(true);
        t.setEllipsize(TextUtils.TruncateAt.END);
        t.setLayoutParams(new LinearLayout.LayoutParams(0, dp(52), 1f));
        bar.addView(t);

        if (rightText != null) {
            bar.addView(gapH());
            Button action = primaryButton(rightText, rightClick);
            action.setMinWidth(dp(68));
            action.setLayoutParams(new LinearLayout.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, dp(48)));
            bar.addView(action);
        }
        return bar;
    }
'''
if old2 not in s:
    raise SystemExit("topbar block not found")
s = s.replace(old2, new2)
main.write_text(s, encoding="utf-8")

gradle = Path("recipe-book/app/build.gradle")
g = gradle.read_text(encoding="utf-8")
g = g.replace("versionCode 2\n        versionName '1.0.1'", "versionCode 3\n        versionName '1.0.2'")
gradle.write_text(g, encoding="utf-8")
