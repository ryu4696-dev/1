# Fold Trio v0.1

Pixel 10 Pro Fold / Android 17 を主対象にした個人用3アプリランチャーの試作です。

## できること

- 端末内のランチャーアプリから A / B / C を選択
- 選択した組み合わせを端末内に保存
- 標準分割を狙う起動（best-effort）
- 3つのFreeformウィンドウを「左1枚 + 右上下2枚」で起動する実験モード
- Foldを開いた状態の `screenWidthDp` とFreeform機能有無を表示

## 重要

Android 17ではPixel Fold上で「2分割 + バブル」による3アプリ利用がOS標準で可能です。一方、第三者アプリが任意の別アプリを強制的にバブル化する公開APIはありません。

そのためv0.1の「3窓で起動」は、Android内部でActivityOptionsが使うBundleキーとFreeform windowing modeを指定して3窓配置を試みます。OS/OEM側がその指定を拒否する場合は効きません。

## 3窓レイアウト

```
┌─────────────────┬──────────────┐
│                 │      B       │
│        A        ├──────────────┤
│                 │      C       │
└─────────────────┴──────────────┘
        約53%            約47%
```

## ビルド環境

- Android Studio
- Android 17 SDK / API 37
- Android Gradle Plugin 9.4.0
- Gradle 9.6
- JDK 17

## ビルド

Android Studioでこのフォルダを開き、SDK 37を入れて `Build > Build APK(s)`。

CLIならGradle 9.6が使える環境で:

```bash
gradle :app:assembleDebug
```

生成先:

`app/build/outputs/apk/debug/app-debug.apk`

## Pixel実機で最初に試す順番

1. Pixel 10 Pro Foldを開く
2. Fold TrioでA/B/Cを選ぶ
3. 「3窓で起動（実験）」
4. 3窓にならなければ「開発者向けオプション」を開き、Freeform / desktop windowing関連設定が存在するか確認
5. 「標準分割で起動」も確認

## 次の版でやること

実機結果に応じてどちらかへ進みます。

- Freeformが効く: ウィンドウ比率保存、横/縦レイアウト、セット複数保存、ワンタップショートカット
- Freeformが拒否される: Shizuku経由でWindowManager Shell / ActivityTaskManagerを操作する実装へ切り替え

