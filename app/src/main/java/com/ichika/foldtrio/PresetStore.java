package com.ichika.foldtrio;

import android.content.ComponentName;
import android.content.Context;
import android.content.SharedPreferences;

public final class PresetStore {
    private static final String PREFS = "fold_trio";

    private final SharedPreferences prefs;

    public PresetStore(Context context) {
        prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
    }

    public void save(int slot, ComponentName component) {
        prefs.edit().putString("slot_" + slot, component == null ? "" : component.flattenToString()).apply();
    }

    public ComponentName load(int slot) {
        String raw = prefs.getString("slot_" + slot, "");
        if (raw == null || raw.isBlank()) return null;
        return ComponentName.unflattenFromString(raw);
    }

    public void setPresetName(String name) {
        prefs.edit().putString("preset_name", name).apply();
    }

    public String getPresetName() {
        return prefs.getString("preset_name", "いつもの3つ");
    }
}
