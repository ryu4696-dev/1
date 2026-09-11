package com.ichika.foldtrio;

import android.app.Activity;
import android.content.ComponentName;
import android.content.Intent;
import android.content.pm.ActivityInfo;
import android.content.pm.PackageManager;
import android.content.res.Configuration;
import android.graphics.drawable.Drawable;
import android.os.Bundle;
import android.provider.Settings;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

public class MainActivity extends Activity {
    private static final int PICK_A = 101;
    private static final int PICK_B = 102;
    private static final int PICK_C = 103;

    private PresetStore store;
    private MultiWindowLauncher launcher;
    private ComponentName appA;
    private ComponentName appB;
    private ComponentName appC;

    private final ImageView[] icons = new ImageView[3];
    private final TextView[] labels = new TextView[3];
    private EditText presetName;
    private TextView deviceInfo;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().setStatusBarColor(getColor(R.color.bg));
        store = new PresetStore(this);
        launcher = new MultiWindowLauncher(this);
        appA = store.load(0);
        appB = store.load(1);
        appC = store.load(2);
        buildUi();
        refreshAllSlots();
        refreshDeviceInfo();
    }

    private void buildUi() {
        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(true);
        scroll.setBackgroundColor(getColor(R.color.bg));

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(20), dp(18), dp(20), dp(28));
        scroll.addView(root, new ScrollView.LayoutParams(-1, -2));

        TextView eyebrow = new TextView(this);
        eyebrow.setText("PIXEL 10 PRO FOLD / PERSONAL TOOL");
        eyebrow.setTextSize(12);
        eyebrow.setLetterSpacing(0.08f);
        eyebrow.setTextColor(getColor(R.color.accent));
        root.addView(eyebrow);

        TextView title = new TextView(this);
        title.setText("Fold Trio");
        title.setTextSize(34);
        title.setTextColor(getColor(R.color.text_primary));
        title.setPadding(0, dp(3), 0, dp(4));
        root.addView(title);

        TextView sub = new TextView(this);
        sub.setText("3つのアプリを、Fold向けの配置でまとめて呼び出す。");
        sub.setTextSize(15);
        sub.setTextColor(getColor(R.color.text_secondary));
        sub.setPadding(0, 0, 0, dp(18));
        root.addView(sub);

        presetName = new EditText(this);
        presetName.setText(store.getPresetName());
        presetName.setHint("セット名");
        presetName.setSingleLine(true);
        presetName.setTextSize(18);
        root.addView(presetName, new LinearLayout.LayoutParams(-1, -2));

        TextView chooseLabel = sectionTitle("アプリ構成");
        chooseLabel.setPadding(0, dp(22), 0, dp(8));
        root.addView(chooseLabel);

        root.addView(slotCard(0, "A", "左側のメインアプリ", PICK_A));
        root.addView(spacer(10));
        root.addView(slotCard(1, "B", "右上 / 分割相手", PICK_B));
        root.addView(spacer(10));
        root.addView(slotCard(2, "C", "右下 / 第3アプリ", PICK_C));

        Button save = button("このセットを保存", false);
        LinearLayout.LayoutParams saveLp = new LinearLayout.LayoutParams(-1, dp(54));
        saveLp.topMargin = dp(16);
        root.addView(save, saveLp);
        save.setOnClickListener(v -> {
            store.setPresetName(presetName.getText().toString().trim().isEmpty()
                    ? "いつもの3つ" : presetName.getText().toString().trim());
            store.save(0, appA);
            store.save(1, appB);
            store.save(2, appC);
            Toast.makeText(this, "保存した", Toast.LENGTH_SHORT).show();
        });

        TextView launchTitle = sectionTitle("起動");
        launchTitle.setPadding(0, dp(24), 0, dp(8));
        root.addView(launchTitle);

        Button experimental = button("3窓で起動（実験）", true);
        root.addView(experimental, new LinearLayout.LayoutParams(-1, dp(58)));
        experimental.setOnClickListener(v -> launcher.launchThreeFreeform(appA, appB, appC));

        Button standard = button("標準分割で起動", false);
        LinearLayout.LayoutParams standardLp = new LinearLayout.LayoutParams(-1, dp(54));
        standardLp.topMargin = dp(10);
        root.addView(standard, standardLp);
        standard.setOnClickListener(v -> launcher.launchStandard(appA, appB, appC));

        deviceInfo = new TextView(this);
        deviceInfo.setTextSize(13);
        deviceInfo.setTextColor(getColor(R.color.text_secondary));
        deviceInfo.setPadding(dp(2), dp(14), dp(2), dp(6));
        root.addView(deviceInfo);

        Button devSettings = button("開発者向けオプションを開く", false);
        LinearLayout.LayoutParams devLp = new LinearLayout.LayoutParams(-1, dp(50));
        devLp.topMargin = dp(6);
        root.addView(devSettings, devLp);
        devSettings.setOnClickListener(v -> {
            try {
                startActivity(new Intent(Settings.ACTION_APPLICATION_DEVELOPMENT_SETTINGS));
            } catch (Exception e) {
                Toast.makeText(this, "開発者向けオプションを開けなかった", Toast.LENGTH_SHORT).show();
            }
        });

        TextView note = new TextView(this);
        note.setText("3窓モードはAndroidのFreeform起動指定を使う試験機能。端末側が拒否した場合は、標準分割＋Android 17のバブルを使う。まず実機で挙動を見て詰めるためのv0.1。\n\n配置: A = 左53% / B = 右上 / C = 右下");
        note.setTextSize(13);
        note.setTextColor(getColor(R.color.text_secondary));
        note.setPadding(0, dp(16), 0, 0);
        root.addView(note);

        setContentView(scroll);
    }

    private View slotCard(int index, String letter, String description, int requestCode) {
        LinearLayout card = new LinearLayout(this);
        card.setOrientation(LinearLayout.HORIZONTAL);
        card.setGravity(Gravity.CENTER_VERTICAL);
        card.setPadding(dp(16), dp(14), dp(16), dp(14));
        card.setBackgroundResource(R.drawable.card_bg);
        card.setOnClickListener(v -> pickApp(requestCode));

        TextView badge = new TextView(this);
        badge.setText(letter);
        badge.setGravity(Gravity.CENTER);
        badge.setTextSize(18);
        badge.setTextColor(getColor(R.color.accent));
        badge.setBackgroundColor(getColor(R.color.accent_soft));
        card.addView(badge, new LinearLayout.LayoutParams(dp(42), dp(42)));

        ImageView icon = new ImageView(this);
        icons[index] = icon;
        LinearLayout.LayoutParams ilp = new LinearLayout.LayoutParams(dp(46), dp(46));
        ilp.leftMargin = dp(12);
        card.addView(icon, ilp);

        LinearLayout texts = new LinearLayout(this);
        texts.setOrientation(LinearLayout.VERTICAL);
        LinearLayout.LayoutParams tlp = new LinearLayout.LayoutParams(0, -2);
        tlp.leftMargin = dp(12);
        tlp.weight = 1f;
        card.addView(texts, tlp);

        TextView app = new TextView(this);
        labels[index] = app;
        app.setText("タップして選択");
        app.setTextSize(17);
        app.setTextColor(getColor(R.color.text_primary));
        texts.addView(app);

        TextView desc = new TextView(this);
        desc.setText(description);
        desc.setTextSize(12);
        desc.setTextColor(getColor(R.color.text_secondary));
        texts.addView(desc);

        TextView arrow = new TextView(this);
        arrow.setText("›");
        arrow.setTextSize(30);
        arrow.setTextColor(getColor(R.color.text_secondary));
        card.addView(arrow);

        return card;
    }

    private Button button(String text, boolean primary) {
        Button b = new Button(this);
        b.setText(text);
        b.setTextSize(16);
        b.setAllCaps(false);
        b.setTextColor(primary ? 0xFFFFFFFF : getColor(R.color.accent));
        b.setBackgroundResource(primary ? R.drawable.button_primary : R.drawable.button_secondary);
        b.setStateListAnimator(null);
        return b;
    }

    private TextView sectionTitle(String text) {
        TextView t = new TextView(this);
        t.setText(text);
        t.setTextSize(20);
        t.setTextColor(getColor(R.color.text_primary));
        return t;
    }

    private View spacer(int dp) {
        View v = new View(this);
        v.setLayoutParams(new LinearLayout.LayoutParams(1, dp(dp)));
        return v;
    }

    private void pickApp(int requestCode) {
        startActivityForResult(new Intent(this, AppPickerActivity.class), requestCode);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (resultCode != RESULT_OK || data == null) return;
        String raw = data.getStringExtra(AppPickerActivity.EXTRA_COMPONENT);
        ComponentName cn = raw == null ? null : ComponentName.unflattenFromString(raw);
        if (cn == null) return;

        if (requestCode == PICK_A) { appA = cn; store.save(0, cn); }
        if (requestCode == PICK_B) { appB = cn; store.save(1, cn); }
        if (requestCode == PICK_C) { appC = cn; store.save(2, cn); }
        refreshAllSlots();
    }

    private void refreshAllSlots() {
        refreshSlot(0, appA);
        refreshSlot(1, appB);
        refreshSlot(2, appC);
    }

    private void refreshSlot(int index, ComponentName cn) {
        if (labels[index] == null || icons[index] == null) return;
        if (cn == null) {
            labels[index].setText("タップして選択");
            icons[index].setImageDrawable(null);
            return;
        }
        PackageManager pm = getPackageManager();
        try {
            ActivityInfo info = pm.getActivityInfo(cn, PackageManager.ComponentInfoFlags.of(0));
            CharSequence label = info.loadLabel(pm);
            Drawable icon = info.loadIcon(pm);
            labels[index].setText(label);
            icons[index].setImageDrawable(icon);
        } catch (PackageManager.NameNotFoundException e) {
            labels[index].setText(cn.getPackageName());
            icons[index].setImageDrawable(null);
        }
    }

    private void refreshDeviceInfo() {
        int widthDp = getResources().getConfiguration().screenWidthDp;
        boolean large = widthDp >= 600;
        boolean freeform = launcher.deviceReportsFreeform();
        String orientation = getResources().getConfiguration().orientation == Configuration.ORIENTATION_LANDSCAPE
                ? "横" : "縦";
        deviceInfo.setText("現在: " + widthDp + "dp / " + orientation
                + " / 大画面=" + (large ? "YES" : "NO")
                + " / Freeform機能=" + (freeform ? "YES" : "NO"));
    }

    @Override
    public void onConfigurationChanged(Configuration newConfig) {
        super.onConfigurationChanged(newConfig);
        refreshDeviceInfo();
    }

    private int dp(int v) {
        return Math.round(v * getResources().getDisplayMetrics().density);
    }
}
