package com.kevyes.calzadoapp.presentation.common;

import android.content.Context;
import android.graphics.Typeface;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

import java.text.NumberFormat;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

public final class Ui {
    private Ui() { }

    public static LinearLayout page(Context context) {
        LinearLayout root = new LinearLayout(context);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(32, 24, 32, 24);
        root.setBackgroundColor(0xFFF5F7FA);
        return root;
    }

    public static TextView title(Context context, String text) {
        TextView t = new TextView(context);
        t.setText(text);
        t.setTextSize(24);
        t.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        t.setPadding(0, 0, 0, 20);
        return t;
    }

    public static TextView label(Context context, String text) {
        TextView t = new TextView(context);
        t.setText(text);
        t.setTextSize(16);
        t.setPadding(0, 8, 0, 8);
        return t;
    }

    public static Button button(Context context, String text) {
        Button b = new Button(context);
        b.setText(text);
        return b;
    }

    public static LinearLayout card(Context context) {
        LinearLayout card = new LinearLayout(context);
        card.setOrientation(LinearLayout.VERTICAL);
        card.setPadding(20, 16, 20, 16);
        card.setBackgroundColor(0xFFFFFFFF);
        LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        p.setMargins(0, 0, 0, 16);
        card.setLayoutParams(p);
        return card;
    }

    public static String money(double value) {
        return NumberFormat.getCurrencyInstance(new Locale("es", "CO")).format(value);
    }

    public static String dateTime(long millis) {
        if (millis <= 0) return "-";
        return new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault()).format(new Date(millis));
    }
}
