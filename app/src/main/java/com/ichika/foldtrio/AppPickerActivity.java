package com.ichika.foldtrio;

import android.app.Activity;
import android.content.ComponentName;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.content.pm.ResolveInfo;
import android.graphics.Color;
import android.graphics.drawable.Drawable;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ListView;
import android.widget.TextView;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;

public class AppPickerActivity extends Activity {
    public static final String EXTRA_COMPONENT = "component";
    public static final String EXTRA_LABEL = "label";

    private final List<AppChoice> allApps = new ArrayList<>();
    private final List<AppChoice> shownApps = new ArrayList<>();
    private AppAdapter adapter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().setStatusBarColor(getColor(R.color.bg));
        buildUi();
        loadApps();
    }

    private void buildUi() {
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(20), dp(12), dp(20), dp(12));
        root.setBackgroundColor(getColor(R.color.bg));

        TextView title = new TextView(this);
        title.setText("アプリを選択");
        title.setTextSize(28);
        title.setTextColor(getColor(R.color.text_primary));
        title.setPadding(0, dp(10), 0, dp(12));
        root.addView(title, new LinearLayout.LayoutParams(-1, -2));

        EditText search = new EditText(this);
        search.setHint("アプリ名で検索");
        search.setSingleLine(true);
        search.setTextSize(16);
        search.setPadding(dp(14), dp(10), dp(14), dp(10));
        root.addView(search, new LinearLayout.LayoutParams(-1, -2));

        ListView list = new ListView(this);
        list.setDividerHeight(0);
        adapter = new AppAdapter();
        list.setAdapter(adapter);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(-1, 0);
        lp.weight = 1f;
        lp.topMargin = dp(10);
        root.addView(list, lp);

        search.addTextChangedListener(new android.text.TextWatcher() {
            @Override public void beforeTextChanged(CharSequence s, int start, int count, int after) {}
            @Override public void onTextChanged(CharSequence s, int start, int before, int count) { filter(s.toString()); }
            @Override public void afterTextChanged(android.text.Editable s) {}
        });

        list.setOnItemClickListener((parent, view, position, id) -> {
            AppChoice app = shownApps.get(position);
            Intent data = new Intent();
            data.putExtra(EXTRA_COMPONENT, app.component.flattenToString());
            data.putExtra(EXTRA_LABEL, app.label);
            setResult(RESULT_OK, data);
            finish();
        });

        setContentView(root);
    }

    private void loadApps() {
        Intent launcher = new Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_LAUNCHER);
        PackageManager pm = getPackageManager();
        List<ResolveInfo> infos = pm.queryIntentActivities(launcher, PackageManager.ResolveInfoFlags.of(0));

        for (ResolveInfo info : infos) {
            if (info.activityInfo.packageName.equals(getPackageName())) continue;
            String label = String.valueOf(info.loadLabel(pm));
            Drawable icon = info.loadIcon(pm);
            ComponentName cn = new ComponentName(info.activityInfo.packageName, info.activityInfo.name);
            allApps.add(new AppChoice(label, cn, icon));
        }
        allApps.sort(Comparator.comparing(a -> a.label.toLowerCase(Locale.JAPANESE)));
        shownApps.clear();
        shownApps.addAll(allApps);
        adapter.notifyDataSetChanged();
    }

    private void filter(String q) {
        String needle = q.trim().toLowerCase(Locale.JAPANESE);
        shownApps.clear();
        if (needle.isEmpty()) {
            shownApps.addAll(allApps);
        } else {
            for (AppChoice app : allApps) {
                if (app.label.toLowerCase(Locale.JAPANESE).contains(needle)
                        || app.component.getPackageName().toLowerCase(Locale.ROOT).contains(needle)) {
                    shownApps.add(app);
                }
            }
        }
        adapter.notifyDataSetChanged();
    }

    private final class AppAdapter extends BaseAdapter {
        @Override public int getCount() { return shownApps.size(); }
        @Override public Object getItem(int position) { return shownApps.get(position); }
        @Override public long getItemId(int position) { return position; }

        @Override
        public View getView(int position, View convertView, ViewGroup parent) {
            LinearLayout row;
            ImageView icon;
            TextView label;
            TextView pkg;

            if (convertView == null) {
                row = new LinearLayout(AppPickerActivity.this);
                row.setOrientation(LinearLayout.HORIZONTAL);
                row.setGravity(Gravity.CENTER_VERTICAL);
                row.setPadding(dp(10), dp(10), dp(10), dp(10));

                icon = new ImageView(AppPickerActivity.this);
                row.addView(icon, new LinearLayout.LayoutParams(dp(48), dp(48)));

                LinearLayout texts = new LinearLayout(AppPickerActivity.this);
                texts.setOrientation(LinearLayout.VERTICAL);
                texts.setPadding(dp(14), 0, 0, 0);
                LinearLayout.LayoutParams tlp = new LinearLayout.LayoutParams(0, -2);
                tlp.weight = 1f;
                row.addView(texts, tlp);

                label = new TextView(AppPickerActivity.this);
                label.setTextSize(17);
                label.setTextColor(getColor(R.color.text_primary));
                texts.addView(label);

                pkg = new TextView(AppPickerActivity.this);
                pkg.setTextSize(12);
                pkg.setTextColor(getColor(R.color.text_secondary));
                texts.addView(pkg);

                row.setTag(new Object[]{icon, label, pkg});
            } else {
                row = (LinearLayout) convertView;
                Object[] tags = (Object[]) row.getTag();
                icon = (ImageView) tags[0];
                label = (TextView) tags[1];
                pkg = (TextView) tags[2];
            }

            AppChoice app = shownApps.get(position);
            icon.setImageDrawable(app.icon);
            label.setText(app.label);
            pkg.setText(app.component.getPackageName());
            row.setBackgroundColor(position % 2 == 0 ? Color.TRANSPARENT : 0x06000000);
            return row;
        }
    }

    private int dp(int v) {
        return Math.round(v * getResources().getDisplayMetrics().density);
    }
}
