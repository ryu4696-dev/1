package com.ichika.foldtrio;

import android.content.ComponentName;
import android.graphics.drawable.Drawable;

public final class AppChoice {
    public final String label;
    public final ComponentName component;
    public final Drawable icon;

    public AppChoice(String label, ComponentName component, Drawable icon) {
        this.label = label;
        this.component = component;
        this.icon = icon;
    }
}
