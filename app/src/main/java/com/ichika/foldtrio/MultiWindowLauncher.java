package com.ichika.foldtrio;

import android.app.Activity;
import android.content.ComponentName;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Rect;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.DisplayMetrics;
import android.widget.Toast;

public final class MultiWindowLauncher {
    private static final String KEY_WINDOWING_MODE = "android.activity.windowingMode";
    private static final String KEY_LAUNCH_BOUNDS = "android:activity.launchBounds";

    // Historical platform values. Current Android internally uses shell-managed split screen,
    // so these are best-effort only. Freeform remains mode 5 in current AOSP.
    private static final int WINDOWING_MODE_SPLIT_PRIMARY = 3;
    private static final int WINDOWING_MODE_SPLIT_SECONDARY = 4;
    private static final int WINDOWING_MODE_FREEFORM = 5;

    private final Activity activity;
    private final Handler handler = new Handler(Looper.getMainLooper());

    public MultiWindowLauncher(Activity activity) {
        this.activity = activity;
    }

    public void launchStandard(ComponentName a, ComponentName b, ComponentName c) {
        if (!ready(a, b, c)) return;

        try {
            Intent first = launchIntent(a);
            Bundle firstOpts = new Bundle();
            firstOpts.putInt(KEY_WINDOWING_MODE, WINDOWING_MODE_SPLIT_PRIMARY);
            activity.startActivity(first, firstOpts);

            handler.postDelayed(() -> {
                try {
                    Intent second = launchIntent(b);
                    second.addFlags(Intent.FLAG_ACTIVITY_LAUNCH_ADJACENT);
                    Bundle secondOpts = new Bundle();
                    secondOpts.putInt(KEY_WINDOWING_MODE, WINDOWING_MODE_SPLIT_SECONDARY);
                    activity.startActivity(second, secondOpts);
                } catch (Exception e) {
                    toast("Bの分割起動に失敗: " + shortError(e));
                }
            }, 500);

            handler.postDelayed(() -> {
                try {
                    // Android 17 lets the user bubble any app, but there is no public API that lets
                    // another app force an arbitrary third-party app into a bubble. We therefore
                    // bring C to front as the final step in standard mode. The experimental mode
                    // below attempts true 3-window freeform placement.
                    Intent third = launchIntent(c);
                    activity.startActivity(third);
                    toast("標準モード: Cは必要ならタスクバーからバブル化");
                } catch (Exception e) {
                    toast("Cの起動に失敗: " + shortError(e));
                }
            }, 1100);
        } catch (Exception e) {
            toast("起動に失敗: " + shortError(e));
        }
    }

    public void launchThreeFreeform(ComponentName a, ComponentName b, ComponentName c) {
        if (!ready(a, b, c)) return;

        DisplayMetrics dm = activity.getResources().getDisplayMetrics();
        int w = dm.widthPixels;
        int h = dm.heightPixels;

        int gap = Math.max(8, Math.round(8 * dm.density));
        int topInset = Math.round(36 * dm.density);
        int bottomInset = Math.round(70 * dm.density);
        int usableTop = topInset + gap;
        int usableBottom = h - bottomInset - gap;

        int leftW = Math.round(w * 0.53f);
        int rightL = leftW + gap;
        int rightW = w - rightL - gap;
        int usableH = usableBottom - usableTop;
        int topH = (usableH - gap) / 2;

        Rect left = new Rect(gap, usableTop, leftW, usableBottom);
        Rect rightTop = new Rect(rightL, usableTop, rightL + rightW, usableTop + topH);
        Rect rightBottom = new Rect(rightL, usableTop + topH + gap, rightL + rightW, usableBottom);

        try {
            startFreeform(a, left);
            handler.postDelayed(() -> {
                try { startFreeform(b, rightTop); }
                catch (Exception e) { toast("Bの3窓起動に失敗: " + shortError(e)); }
            }, 350);
            handler.postDelayed(() -> {
                try { startFreeform(c, rightBottom); }
                catch (Exception e) { toast("Cの3窓起動に失敗: " + shortError(e)); }
            }, 700);
        } catch (Exception e) {
            toast("3窓起動に失敗: " + shortError(e));
        }
    }

    private void startFreeform(ComponentName component, Rect bounds) {
        Intent intent = launchIntent(component);
        Bundle opts = new Bundle();
        opts.putInt(KEY_WINDOWING_MODE, WINDOWING_MODE_FREEFORM);
        opts.putParcelable(KEY_LAUNCH_BOUNDS, bounds);
        activity.startActivity(intent, opts);
    }

    private Intent launchIntent(ComponentName component) {
        Intent base = new Intent(Intent.ACTION_MAIN)
                .addCategory(Intent.CATEGORY_LAUNCHER)
                .setComponent(component)
                .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                .addFlags(Intent.FLAG_ACTIVITY_MULTIPLE_TASK)
                .addFlags(Intent.FLAG_ACTIVITY_NO_ANIMATION);
        return base;
    }

    private boolean ready(ComponentName a, ComponentName b, ComponentName c) {
        if (a == null || b == null || c == null) {
            toast("A・B・Cを全部選んでから起動して");
            return false;
        }
        return true;
    }

    public boolean deviceReportsFreeform() {
        return activity.getPackageManager().hasSystemFeature(PackageManager.FEATURE_FREEFORM_WINDOW_MANAGEMENT);
    }

    private void toast(String message) {
        Toast.makeText(activity, message, Toast.LENGTH_LONG).show();
    }

    private String shortError(Exception e) {
        String m = e.getMessage();
        return m == null ? e.getClass().getSimpleName() : m;
    }
}
