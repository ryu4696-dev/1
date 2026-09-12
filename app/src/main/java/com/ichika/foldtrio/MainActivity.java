package com.ichika.foldtrio;

import android.Manifest;
import android.app.Activity;
import android.app.PictureInPictureParams;
import android.content.pm.PackageManager;
import android.content.res.Configuration;
import android.graphics.Color;
import android.graphics.Rect;
import android.location.Address;
import android.location.Geocoder;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.SystemClock;
import android.util.Rational;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import java.util.List;
import java.util.Locale;

public class MainActivity extends Activity implements LocationListener {
    private static final int LOCATION_REQUEST = 1001;

    private final Handler handler = new Handler(Looper.getMainLooper());
    private LocationManager locationManager;
    private Geocoder geocoder;
    private LinearLayout root;
    private LinearLayout controls;
    private TextView speedView;
    private TextView distanceView;
    private TextView timeView;
    private TextView placeView;
    private TextView statusView;
    private Button startButton;
    private Button pauseButton;
    private boolean tracking;
    private boolean paused;
    private long startedAtMs;
    private long pausedAtMs;
    private long accumulatedPauseMs;
    private float distanceMeters;
    private float displayedSpeedKmh;
    private Location lastAcceptedLocation;
    private long lastGeocodeAtMs;
    private Location lastGeocodeLocation;
    private String currentPlace = "位置取得中";
    private String currentDirection = "—";

    private final Runnable clockTicker = new Runnable() {
        @Override public void run() {
            updateDashboard();
            handler.postDelayed(this, 500L);
        }
    };

    @Override protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        locationManager = (LocationManager) getSystemService(LOCATION_SERVICE);
        geocoder = new Geocoder(this, Locale.JAPAN);
        buildUi();
        configurePip(false);
        handler.post(clockTicker);
    }

    private void buildUi() {
        root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setGravity(Gravity.CENTER);
        root.setPadding(dp(20), dp(20), dp(20), dp(20));
        root.setBackgroundColor(Color.rgb(8, 12, 18));

        TextView title = text("DRIVE METER", 18, Color.rgb(92, 180, 255));
        title.setLetterSpacing(0.18f);
        title.setTag("title");
        root.addView(title, params(-1, -2, 0, dp(8)));

        LinearLayout meter = new LinearLayout(this);
        meter.setOrientation(LinearLayout.VERTICAL);
        meter.setGravity(Gravity.CENTER);
        meter.setPadding(dp(12), dp(10), dp(12), dp(10));
        meter.setBackgroundColor(Color.rgb(8, 12, 18));
        meter.setTag("meter");

        speedView = text("0 km/h", 48, Color.WHITE);
        distanceView = text("0.0 km", 28, Color.rgb(92, 205, 255));
        timeView = text("0:00", 28, Color.rgb(205, 213, 224));
        placeView = text("位置取得中・—", 22, Color.WHITE);
        placeView.setSingleLine(true);
        meter.addView(speedView, params(-1, -2, 0, 0));
        meter.addView(distanceView, params(-1, -2, 0, 0));
        meter.addView(timeView, params(-1, -2, 0, 0));
        meter.addView(placeView, params(-1, -2, 0, 0));
        root.addView(meter, new LinearLayout.LayoutParams(-1, 0, 1f));

        controls = new LinearLayout(this);
        controls.setOrientation(LinearLayout.VERTICAL);
        controls.setGravity(Gravity.CENTER);
        statusView = text("位置情報を許可して開始", 14, Color.rgb(160, 170, 184));
        controls.addView(statusView, params(-1, -2, 0, dp(12)));

        LinearLayout buttons = new LinearLayout(this);
        buttons.setGravity(Gravity.CENTER);
        startButton = button("開始してPiP", v -> startTripAndEnterPip());
        pauseButton = button("一時停止", v -> togglePause());
        pauseButton.setEnabled(false);
        Button resetButton = button("終了・リセット", v -> resetTrip());
        buttons.addView(startButton, weightedButton());
        buttons.addView(pauseButton, weightedButton());
        buttons.addView(resetButton, weightedButton());
        controls.addView(buttons, params(-1, -2, 0, 0));
        root.addView(controls, params(-1, -2, dp(12), 0));
        setContentView(root);
    }

    private void startTripAndEnterPip() {
        if (!hasLocationPermission()) {
            requestPermissions(new String[]{Manifest.permission.ACCESS_FINE_LOCATION,
                    Manifest.permission.ACCESS_COARSE_LOCATION}, LOCATION_REQUEST);
            return;
        }
        if (!tracking) {
            tracking = true;
            paused = false;
            startedAtMs = SystemClock.elapsedRealtime();
            accumulatedPauseMs = 0L;
            distanceMeters = 0f;
            lastAcceptedLocation = null;
            startButton.setText("PiP表示");
            pauseButton.setEnabled(true);
        }
        requestLocationUpdates();
        statusView.setText("計測中");
        configurePip(true);
        enterPip();
    }

    private void togglePause() {
        if (!tracking) return;
        if (!paused) {
            paused = true;
            pausedAtMs = SystemClock.elapsedRealtime();
            displayedSpeedKmh = 0f;
            lastAcceptedLocation = null;
            pauseButton.setText("再開");
            statusView.setText("一時停止中");
        } else {
            paused = false;
            accumulatedPauseMs += SystemClock.elapsedRealtime() - pausedAtMs;
            lastAcceptedLocation = null;
            pauseButton.setText("一時停止");
            statusView.setText("計測中");
        }
        configurePip(tracking && !paused);
        updateDashboard();
    }

    private void resetTrip() {
        tracking = false;
        paused = false;
        distanceMeters = 0f;
        displayedSpeedKmh = 0f;
        startedAtMs = 0L;
        accumulatedPauseMs = 0L;
        lastAcceptedLocation = null;
        currentPlace = "位置取得中";
        currentDirection = "—";
        startButton.setText("開始してPiP");
        pauseButton.setText("一時停止");
        pauseButton.setEnabled(false);
        statusView.setText("停止しました");
        configurePip(false);
        updateDashboard();
    }

    private void requestLocationUpdates() {
        if (!hasLocationPermission()) return;
        try {
            if (locationManager.isProviderEnabled(LocationManager.GPS_PROVIDER)) {
                locationManager.requestLocationUpdates(LocationManager.GPS_PROVIDER,
                        1000L, 1f, this, Looper.getMainLooper());
            }
            locationManager.requestLocationUpdates(LocationManager.NETWORK_PROVIDER,
                    3000L, 5f, this, Looper.getMainLooper());
        } catch (SecurityException | IllegalArgumentException ignored) {
            statusView.setText("位置情報を取得できません");
        }
    }

    @Override public void onLocationChanged(Location location) {
        if (!tracking || paused) return;
        float rawSpeed = location.hasSpeed() ? Math.max(0f, location.getSpeed() * 3.6f) : 0f;
        displayedSpeedKmh = displayedSpeedKmh == 0f
                ? rawSpeed : displayedSpeedKmh * 0.65f + rawSpeed * 0.35f;
        if (displayedSpeedKmh < 1.5f) displayedSpeedKmh = 0f;
        if (location.hasBearing() && rawSpeed >= 3f) currentDirection = directionFor(location.getBearing());

        if (lastAcceptedLocation != null && location.getAccuracy() <= 40f
                && lastAcceptedLocation.getAccuracy() <= 40f) {
            float segment = lastAcceptedLocation.distanceTo(location);
            long deltaMs = location.getTime() - lastAcceptedLocation.getTime();
            if (rawSpeed >= 3f && segment >= 2f && segment <= 500f
                    && deltaMs > 0 && deltaMs <= 30000L) distanceMeters += segment;
        }
        if (location.getAccuracy() <= 40f) lastAcceptedLocation = new Location(location);
        maybeReverseGeocode(location);
        updateDashboard();
    }

    private void maybeReverseGeocode(Location location) {
        long now = SystemClock.elapsedRealtime();
        boolean movedEnough = lastGeocodeLocation == null || lastGeocodeLocation.distanceTo(location) >= 500f;
        if (!movedEnough && now - lastGeocodeAtMs < 30000L) return;
        lastGeocodeAtMs = now;
        lastGeocodeLocation = new Location(location);
        geocoder.getFromLocation(location.getLatitude(), location.getLongitude(), 1,
                new Geocoder.GeocodeListener() {
                    @Override public void onGeocode(List<Address> addresses) {
                        if (addresses == null || addresses.isEmpty()) return;
                        Address a = addresses.get(0);
                        String place = firstNonEmpty(a.getLocality(), a.getSubAdminArea(),
                                a.getSubLocality(), a.getAdminArea());
                        if (place != null) {
                            currentPlace = place;
                            runOnUiThread(() -> updateDashboard());
                        }
                    }
                    @Override public void onError(String errorMessage) { }
                });
    }

    private void updateDashboard() {
        speedView.setText(String.format(Locale.JAPAN, "%d km/h", Math.round(displayedSpeedKmh)));
        distanceView.setText(String.format(Locale.JAPAN, "%.1f km", distanceMeters / 1000f));
        long elapsed = 0L;
        if (tracking) {
            long end = paused ? pausedAtMs : SystemClock.elapsedRealtime();
            elapsed = Math.max(0L, end - startedAtMs - accumulatedPauseMs);
        }
        long totalMinutes = elapsed / 60000L;
        timeView.setText(String.format(Locale.JAPAN, "%d:%02d", totalMinutes / 60L, totalMinutes % 60L));
        placeView.setText(currentPlace + "・" + currentDirection);
    }

    private void configurePip(boolean autoEnter) {
        if (!getPackageManager().hasSystemFeature(PackageManager.FEATURE_PICTURE_IN_PICTURE)) return;
        PictureInPictureParams.Builder builder = new PictureInPictureParams.Builder()
                .setAspectRatio(new Rational(3, 4))
                .setAutoEnterEnabled(autoEnter)
                .setSeamlessResizeEnabled(false);
        View meter = root == null ? null : root.findViewWithTag("meter");
        if (meter != null) {
            Rect rect = new Rect();
            if (meter.getGlobalVisibleRect(rect)) builder.setSourceRectHint(rect);
        }
        setPictureInPictureParams(builder.build());
    }

    private void enterPip() {
        if (!getPackageManager().hasSystemFeature(PackageManager.FEATURE_PICTURE_IN_PICTURE)) {
            Toast.makeText(this, "この端末はPiPに対応していません", Toast.LENGTH_SHORT).show();
            return;
        }
        enterPictureInPictureMode(new PictureInPictureParams.Builder()
                .setAspectRatio(new Rational(3, 4)).setAutoEnterEnabled(true)
                .setSeamlessResizeEnabled(false).build());
    }

    @Override public void onPictureInPictureModeChanged(boolean inPipMode, Configuration newConfig) {
        super.onPictureInPictureModeChanged(inPipMode, newConfig);
        root.findViewWithTag("title").setVisibility(inPipMode ? View.GONE : View.VISIBLE);
        controls.setVisibility(inPipMode ? View.GONE : View.VISIBLE);
        int pad = inPipMode ? dp(4) : dp(20);
        root.setPadding(pad, pad, pad, pad);
        speedView.setTextSize(inPipMode ? 28 : 48);
        distanceView.setTextSize(inPipMode ? 20 : 28);
        timeView.setTextSize(inPipMode ? 20 : 28);
        placeView.setTextSize(inPipMode ? 15 : 22);
    }

    @Override public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == LOCATION_REQUEST) {
            if (hasLocationPermission()) startTripAndEnterPip();
            else statusView.setText("位置情報の許可が必要です");
        }
    }

    private boolean hasLocationPermission() {
        return checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED
                || checkSelfPermission(Manifest.permission.ACCESS_COARSE_LOCATION) == PackageManager.PERMISSION_GRANTED;
    }

    private String directionFor(float bearing) {
        String[] dirs = {"北", "北東", "東", "南東", "南", "南西", "西", "北西"};
        return dirs[Math.round(bearing / 45f) % 8];
    }

    private String firstNonEmpty(String... values) {
        for (String value : values) if (value != null && !value.trim().isEmpty()) return value;
        return null;
    }

    private TextView text(String value, float sp, int color) {
        TextView view = new TextView(this);
        view.setText(value);
        view.setTextSize(sp);
        view.setTextColor(color);
        view.setGravity(Gravity.CENTER);
        view.setFontFeatureSettings("tnum");
        return view;
    }

    private Button button(String value, View.OnClickListener listener) {
        Button button = new Button(this);
        button.setText(value);
        button.setTextSize(13);
        button.setOnClickListener(listener);
        return button;
    }

    private LinearLayout.LayoutParams weightedButton() {
        LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(0, dp(52), 1f);
        p.setMargins(dp(3), 0, dp(3), 0);
        return p;
    }

    private LinearLayout.LayoutParams params(int width, int height, int top, int bottom) {
        LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(width, height);
        p.setMargins(0, top, 0, bottom);
        return p;
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }

    @Override protected void onDestroy() {
        handler.removeCallbacks(clockTicker);
        try { locationManager.removeUpdates(this); } catch (SecurityException ignored) { }
        super.onDestroy();
    }
}
