#!/usr/bin/env python3
from pathlib import Path

root = Path("libQwenImage21")
src = root / "demo/src/main/java/com/scsonic/qwenimage21/demo"
main = src / "MainActivity.java"
layout = root / "demo/src/main/res/layout/activity_main.xml"
manifest = root / "demo/src/main/AndroidManifest.xml"

# ---------------------------------------------------------------- downloader
downloader = r'''package com.scsonic.qwenimage21.demo;

import android.os.Build;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

final class NoctModelDownloader {
    interface Listener {
        void onProgress(String label, long done, long total);
    }

    static final String TAG = "noctq-mobile-model-v1";
    static final String MARKER = "noctq_mobile_v1.marker";
    private static final String API =
            "https://api.github.com/repos/ryu4696-dev/1/releases/tags/" + TAG;

    private static final class Asset {
        final String name, url;
        final long size;
        Asset(String name, String url, long size) {
            this.name = name;
            this.url = url;
            this.size = size;
        }
    }

    static boolean installed(File dir) {
        return new File(dir, MARKER).isFile()
                && new File(dir, "dit.mnn").isFile()
                && new File(dir, "dit.mnn.weight").isFile()
                && new File(dir, "txt_in.mnn").isFile()
                && new File(dir, "txt_in.mnn.weight").isFile()
                && new File(dir, "img_in.mnn").isFile()
                && new File(dir, "img_in.mnn.weight").isFile();
    }

    static void install(File modelDir, Listener listener) throws Exception {
        modelDir.mkdirs();
        JSONObject release = new JSONObject(readText(API));
        JSONArray arr = release.getJSONArray("assets");
        Map<String, Asset> assets = new HashMap<>();
        List<String> parts = new ArrayList<>();
        long total = 0;
        for (int i = 0; i < arr.length(); i++) {
            JSONObject a = arr.getJSONObject(i);
            String name = a.getString("name");
            Asset x = new Asset(name, a.getString("browser_download_url"), a.optLong("size", 0));
            assets.put(name, x);
            if (name.equals("noctq-meta.tar") || name.startsWith("noctq-dit.mnn.weight.part-")) {
                total += x.size;
                if (name.startsWith("noctq-dit.mnn.weight.part-")) parts.add(name);
            }
        }
        Asset meta = assets.get("noctq-meta.tar");
        if (meta == null || parts.isEmpty()) {
            throw new IllegalStateException("Noct-Q配布ファイルがまだ揃っていません");
        }
        Collections.sort(parts);

        File tmp = new File(modelDir, ".noctq_install");
        deleteRec(tmp);
        if (!tmp.mkdirs()) throw new IllegalStateException("一時フォルダを作成できません");

        long[] done = {0};
        File tar = new File(tmp, "meta.tar");
        download(meta, tar, listener, done, total);
        extractTar(tar, tmp);
        tar.delete();

        File weight = new File(tmp, "dit.mnn.weight");
        try (OutputStream out = new BufferedOutputStream(new FileOutputStream(weight))) {
            for (String name : parts) {
                Asset a = assets.get(name);
                File part = new File(tmp, name);
                download(a, part, listener, done, total);
                try (InputStream in = new BufferedInputStream(new FileInputStream(part))) {
                    copy(in, out, a.size);
                }
                part.delete();
            }
        }

        verify(tmp);

        String[] replace = {
                "dit.mnn", "dit.mnn.weight",
                "txt_in.mnn", "txt_in.mnn.weight",
                "img_in.mnn", "img_in.mnn.weight"
        };
        for (String name : replace) {
            File from = new File(tmp, name);
            if (!from.isFile()) throw new IllegalStateException("変換モデルに不足: " + name);
            moveReplace(from, new File(modelDir, name));
        }

        try (FileOutputStream out = new FileOutputStream(new File(modelDir, MARKER))) {
            out.write(("Noct-Q Anime V1 / " + TAG + "\n").getBytes(StandardCharsets.UTF_8));
        }
        deleteRec(tmp);
        if (listener != null) listener.onProgress("Noct-Q導入完了", total, total);
    }

    private static void verify(File tmp) throws Exception {
        File manifest = new File(tmp, "manifest.json");
        if (!manifest.isFile()) throw new IllegalStateException("manifest.json がありません");
        JSONObject j = new JSONObject(readFileText(manifest));
        JSONArray files = j.getJSONArray("files");
        String[] required = {
                "dit.mnn", "dit.mnn.weight", "txt_in.mnn", "txt_in.mnn.weight",
                "img_in.mnn", "img_in.mnn.weight"
        };
        Map<String, String> expected = new HashMap<>();
        for (int i = 0; i < files.length(); i++) {
            JSONObject f = files.getJSONObject(i);
            expected.put(f.getString("name"), f.getString("sha256"));
        }
        for (String name : required) {
            File f = new File(tmp, name);
            String want = expected.get(name);
            if (!f.isFile() || want == null) throw new IllegalStateException("検証対象不足: " + name);
            String got = sha256(f);
            if (!want.equalsIgnoreCase(got)) throw new IllegalStateException("SHA-256不一致: " + name);
        }
    }

    private static String sha256(File f) throws Exception {
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        byte[] b = new byte[8 << 20];
        try (InputStream in = new BufferedInputStream(new FileInputStream(f))) {
            int n;
            while ((n = in.read(b)) > 0) md.update(b, 0, n);
        }
        StringBuilder sb = new StringBuilder();
        for (byte x : md.digest()) sb.append(String.format(Locale.US, "%02x", x & 255));
        return sb.toString();
    }

    private static void download(Asset a, File dst, Listener listener, long[] done, long total) throws Exception {
        HttpURLConnection c = (HttpURLConnection) new URL(a.url).openConnection();
        c.setInstanceFollowRedirects(true);
        c.setConnectTimeout(30000);
        c.setReadTimeout(60000);
        c.setRequestProperty("User-Agent", "NoctQ-Mobile/6");
        c.connect();
        int code = c.getResponseCode();
        if (code < 200 || code >= 300) throw new IllegalStateException("HTTP " + code + ": " + a.name);
        try (InputStream in = new BufferedInputStream(c.getInputStream());
             OutputStream out = new BufferedOutputStream(new FileOutputStream(dst))) {
            byte[] b = new byte[1 << 20];
            int n;
            while ((n = in.read(b)) > 0) {
                out.write(b, 0, n);
                done[0] += n;
                if (listener != null) listener.onProgress(a.name, done[0], total);
            }
        } finally {
            c.disconnect();
        }
        if (a.size > 0 && dst.length() != a.size) {
            throw new IllegalStateException("サイズ不一致: " + a.name);
        }
    }

    private static String readText(String url) throws Exception {
        HttpURLConnection c = (HttpURLConnection) new URL(url).openConnection();
        c.setConnectTimeout(30000);
        c.setReadTimeout(30000);
        c.setRequestProperty("User-Agent", "NoctQ-Mobile/6");
        int code = c.getResponseCode();
        if (code < 200 || code >= 300) throw new IllegalStateException("Release API HTTP " + code);
        try (InputStream in = c.getInputStream()) {
            ByteArrayOutputStream out = new ByteArrayOutputStream();
            byte[] b = new byte[65536];
            int n;
            while ((n = in.read(b)) > 0) out.write(b, 0, n);
            return out.toString("UTF-8");
        } finally {
            c.disconnect();
        }
    }

    private static String readFileText(File f) throws Exception {
        try (InputStream in = new FileInputStream(f)) {
            ByteArrayOutputStream out = new ByteArrayOutputStream();
            byte[] b = new byte[65536];
            int n;
            while ((n = in.read(b)) > 0) out.write(b, 0, n);
            return out.toString("UTF-8");
        }
    }

    private static void extractTar(File tar, File dir) throws Exception {
        String[] allowed = {
                "dit.mnn", "txt_in.mnn", "txt_in.mnn.weight",
                "img_in.mnn", "img_in.mnn.weight", "manifest.json",
                "SHA256SUMS.txt", "NOCTQ_LICENSE.txt", "NOCTQ_NOTICE.txt"
        };
        java.util.HashSet<String> ok = new java.util.HashSet<>();
        Collections.addAll(ok, allowed);
        try (InputStream in = new BufferedInputStream(new FileInputStream(tar))) {
            byte[] h = new byte[512];
            while (true) {
                if (!readFully(in, h)) break;
                boolean zero = true;
                for (byte x : h) if (x != 0) { zero = false; break; }
                if (zero) break;
                String name = cString(h, 0, 100);
                long size = parseOctal(h, 124, 12);
                if (ok.contains(name)) {
                    try (OutputStream out = new BufferedOutputStream(new FileOutputStream(new File(dir, name)))) {
                        copy(in, out, size);
                    }
                } else {
                    skipFully(in, size);
                }
                long pad = (512 - (size % 512)) % 512;
                skipFully(in, pad);
            }
        }
    }

    private static boolean readFully(InputStream in, byte[] b) throws Exception {
        int off = 0;
        while (off < b.length) {
            int n = in.read(b, off, b.length - off);
            if (n < 0) return off != 0 ? false : false;
            off += n;
        }
        return true;
    }

    private static String cString(byte[] b, int off, int len) {
        int end = off;
        while (end < off + len && b[end] != 0) end++;
        return new String(b, off, end - off, StandardCharsets.UTF_8);
    }

    private static long parseOctal(byte[] b, int off, int len) {
        long v = 0;
        for (int i = off; i < off + len; i++) {
            int c = b[i] & 255;
            if (c >= '0' && c <= '7') v = (v << 3) + (c - '0');
        }
        return v;
    }

    private static void copy(InputStream in, OutputStream out, long count) throws Exception {
        byte[] b = new byte[1 << 20];
        long left = count;
        while (left > 0) {
            int n = in.read(b, 0, (int)Math.min(b.length, left));
            if (n < 0) throw new IllegalStateException("予期せずファイル終端");
            out.write(b, 0, n);
            left -= n;
        }
    }

    private static void skipFully(InputStream in, long count) throws Exception {
        byte[] b = new byte[65536];
        long left = count;
        while (left > 0) {
            int n = in.read(b, 0, (int)Math.min(b.length, left));
            if (n < 0) throw new IllegalStateException("tar破損");
            left -= n;
        }
    }

    private static void moveReplace(File src, File dst) throws Exception {
        if (dst.exists() && !dst.delete()) throw new IllegalStateException("旧モデルを置換できません: " + dst.getName());
        if (src.renameTo(dst)) return;
        try (InputStream in = new FileInputStream(src); OutputStream out = new FileOutputStream(dst)) {
            byte[] b = new byte[1 << 20];
            int n;
            while ((n = in.read(b)) > 0) out.write(b, 0, n);
        }
        if (!src.delete()) src.deleteOnExit();
    }

    private static void deleteRec(File f) {
        if (f == null || !f.exists()) return;
        if (f.isDirectory()) {
            File[] kids = f.listFiles();
            if (kids != null) for (File k : kids) deleteRec(k);
        }
        f.delete();
    }
}
'''
(src / "NoctModelDownloader.java").write_text(downloader)

# ---------------------------------------------------------------- MainActivity
s = main.read_text()
s = s.replace(
    'private CheckBox gpu, teCpu, keep, turbo, dlStandard, dlTurbo, refHalf;',
    'private CheckBox gpu, teCpu, keep, turbo, dlStandard, dlTurbo, refHalf, animeMode;'
)
s = s.replace(
    'private File modelDir, inputFile, inputFile2, crashMarker;',
    'private File modelDir, inputFile, inputFile2, crashMarker, noctMarker;'
)
s = s.replace(
    'crashMarker = new File(getFilesDir(), "generation_in_progress.txt");',
    'crashMarker = new File(getFilesDir(), "generation_in_progress.txt");\n'
    '        noctMarker = new File(modelDir, NoctModelDownloader.MARKER);'
)
s = s.replace(
    'refHalf = findViewById(R.id.ref_half);',
    'refHalf = findViewById(R.id.ref_half);\n'
    '        animeMode = findViewById(R.id.anime_mode);'
)
s = s.replace(
    'download.setOnClickListener(v -> startDownload());',
    'download.setOnClickListener(v -> startNoctDownload());'
)

# Keep Noct non-turbo. Viggle Turbo was trained against the base model, not this fine-tune.
s = s.replace(
    'turbo.setChecked(prefs.getBoolean("turbo", false));',
    'turbo.setChecked(false);'
)
s = s.replace(
    'prefs.edit().putBoolean("turbo", checked).apply();',
    'prefs.edit().putBoolean("turbo", false).apply();'
)
s = s.replace(
    'if (checked) {',
    'if (false && checked) {',
    1
)
# Hide downloader selectors in code as well.
anchor = 'dlTurbo.setOnCheckedChangeListener((b, c) -> prefs.edit().putBoolean("dlTurbo", c).apply());'
s = s.replace(anchor, anchor + '''
        animeMode.setChecked(prefs.getBoolean("animeMode", true));
        animeMode.setOnCheckedChangeListener((b, c) -> prefs.edit().putBoolean("animeMode", c).apply());''')

# Replace the v5.1 prompt construction robustly. The workflow-generated
# source has changed indentation/line wrapping a few times, so match the
# semantic anchors rather than one exact multiline literal.
src_lines = s.splitlines()
out_lines = []
i = 0
prompt_patched = False
while i < len(src_lines):
    line = src_lines[i]
    if 'final String userText = prompt.getText().toString().trim();' in line:
        indent = line[:len(line) - len(line.lstrip())]
        out_lines.append(line)
        j = i + 1
        while j < len(src_lines) and 'addHistory(' not in src_lines[j]:
            j += 1
        if j >= len(src_lines):
            raise SystemExit("addHistory after userText not found")
        out_lines.extend([
            indent + 'String coreText = userText;',
            indent + 'if (animeMode.isChecked()) coreText = "An anime illustration of " + coreText;',
            indent + 'final String text = coreText + "。人物が含まれる場合は、成人として、自然な人体構造、正しい関節、左右の手足が明確、手指の形が自然、顔と身体のつながりが自然、重複した手足や余分な指を避ける。";',
            indent + 'addHistory(userText);',
        ])
        i = j + 1
        prompt_patched = True
        continue
    out_lines.append(line)
    i += 1
if not prompt_patched:
    raise SystemExit("v5.1 userText prompt anchor not found")
s = "\n".join(out_lines) + "\n"

# Require Noct installation before generation.
needle = '    private void startGeneration() {\n        if (!refreshModelStatus()) return;'
rep = '''    private void startGeneration() {
        if (!NoctModelDownloader.installed(modelDir)) {
            showError("Noct-Q未導入", "モデル管理の「Noct-Qを導入 / 更新」を押してください。既存のQwen共通ファイルはそのまま再利用します。");
            return;
        }
        if (!refreshModelStatus()) return;'''
if needle not in s:
    raise SystemExit("startGeneration target not found")
s = s.replace(needle, rep, 1)

# Add Noct downloader and status handling before old startDownload.
marker = '    private void startDownload() {'
methods = r'''
    private void startNoctDownload() {
        // Noct-Q only replaces the transformer pieces. The text encoder/VAE from
        // the already working Qwen installation are shared.
        String sharedMissing = QwenImage21.missingStandardDitFiles(modelDir);
        if (sharedMissing != null && !new File(modelDir, "text_encoder/llm.mnn").isFile()) {
            showError("共通モデルが必要です",
                    "この端末ではv5で使っていたQwen共通モデル（text encoder / VAE）を再利用します。先に通常モデル一式を用意してください。");
            return;
        }
        if (model != null) {
            model.close();
            model = null;
            modelKey = null;
        }
        setBusy(true);
        progress.setProgress(0);
        status.setText("Noct-Q Anime V1 を導入しています…");
        new Thread(() -> {
            try {
                NoctModelDownloader.install(modelDir, (label, done, total) -> runOnUiThread(() -> {
                    int p = total > 0 ? (int)Math.min(100, done * 100 / total) : 0;
                    progress.setProgress(p);
                    status.setText(String.format("Noct-Q導入中: %s\n%.2f / %.2f GB",
                            label, done / 1e9, total / 1e9));
                }));
                runOnUiThread(() -> {
                    status.setText("Noct-Q Anime V1 導入完了。日本語で生成できます。");
                    refreshModelStatus();
                });
            } catch (Exception e) {
                runOnUiThread(() -> showError("Noct-Q導入失敗", String.valueOf(e.getMessage())));
            } finally {
                runOnUiThread(() -> setBusy(false));
            }
        }, "noct-model-download").start();
    }

'''
if marker not in s:
    raise SystemExit("startDownload marker missing")
s = s.replace(marker, methods + marker, 1)

# Status: make it explicit whether the current files are really Noct.
needle = '    private boolean refreshModelStatus() {\n'
rep = '''    private boolean refreshModelStatus() {
        if (NoctModelDownloader.installed(modelDir)) {
            String missingEdit = QwenImage21.missingEditFiles(modelDir);
            status.setText("モデル: Noct-Q Anime V1 / MNN INT4"
                    + (missingEdit != null ? "\n画像編集の追加ファイル不足: " + missingEdit : "")
                    + "\n空きメモリ: " + QwenImage21.availableMemoryMB() + " MB");
            return true;
        }
'''
if needle not in s:
    raise SystemExit("refresh status target missing")
s = s.replace(needle, rep, 1)

# Presets: Noct is not distilled. Do not repeat the 8-step anatomy mistake.
start = s.index('              private void applyPreset(int mode) {')
end = s.index('              private void saveLastImage()', start)
newpreset = r'''              private void applyPreset(int mode) {
                  keep.setChecked(false);
                  gpu.setChecked(false);
                  teCpu.setChecked(true);
                  turbo.setChecked(false);
                  if (mode == 0) {
                      tier.setSelection(1);
                      steps.setText("16");
                      status.setText("省時間：Fast 384 / 16step（Noct-Q・非Turbo）");
                  } else if (mode == 1) {
                      tier.setSelection(1);
                      steps.setText("20");
                      status.setText("標準：Fast 384 / 20step");
                  } else {
                      tier.setSelection(1);
                      steps.setText("25");
                      status.setText("高品質：Fast 384 / 25step（Noct-Q推奨step数）");
                  }
              }

'''
s = s[:start] + newpreset + s[end:]

# Default Noct standard preset.
s = s.replace(
    'if (!prefs.getBoolean("v51_defaults", false)) {\n                  applyPreset(2);\n                  prefs.edit().putBoolean("v51_defaults", true).apply();\n              }',
    'if (!prefs.getBoolean("v6_defaults", false)) {\n                  applyPreset(1);\n                  prefs.edit().putBoolean("v6_defaults", true).apply();\n              }'
)

main.write_text(s)

# ---------------------------------------------------------------- layout
x = layout.read_text()
x = x.replace('NoctQ Mobile v5.1 · ローカル画像生成', 'NoctQ Mobile v6 · Noct-Q Anime V1')
x = x.replace(
    '日本語でそのまま入力できます。生成画像は Pictures/NoctQ に自動保存します。',
    'Noct-Q Anime V1を端末内で生成。日本語入力・Pictures/NoctQ自動保存。'
)
# Put anime/photo switch below prompt area, before recommended settings.
target = '''                  <TextView android:layout_width="match_parent" android:layout_height="wrap_content"
                      android:text="おすすめ設定" android:textStyle="bold" android:layout_marginTop="8dp" />'''
anime = '''                  <CheckBox
                      android:id="@+id/anime_mode"
                      android:layout_width="match_parent"
                      android:layout_height="wrap_content"
                      android:checked="true"
                      android:text="アニメ優先（OFFで写真寄り）" />

                  <TextView android:layout_width="match_parent" android:layout_height="wrap_content"
                      android:text="おすすめ設定" android:textStyle="bold" android:layout_marginTop="8dp" />'''
if target not in x:
    raise SystemExit("layout recommended target missing")
x = x.replace(target, anime, 1)
x = x.replace('android:text="高速" />', 'android:text="省時間" />', 1)
# Hide old Turbo and upstream model selectors; keep IDs because MainActivity references them.
x = x.replace(
    'android:text="高速Turbo（6step・別モデルが必要）" />',
    'android:text="Turbo" android:visibility="gone" />'
)
x = x.replace(
    'android:text="通常モデル" />',
    'android:text="通常モデル" android:visibility="gone" />'
)
x = x.replace(
    'android:checked="true" android:text="高速Turboモデル" />',
    'android:checked="false" android:text="高速Turboモデル" android:visibility="gone" />'
)
x = x.replace('android:text="モデル管理"', 'android:text="Noct-Q モデル管理"')
x = x.replace(
    'android:text="選択したモデルをダウンロード" />',
    'android:text="Noct-Qを導入 / 更新" />'
)
layout.write_text(x)

m = manifest.read_text().replace('android:label="NoctQ Mobile v5.1"', 'android:label="NoctQ Mobile v6"')
manifest.write_text(m)
print("patched NoctQ Mobile v6")
