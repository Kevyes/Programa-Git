package com.kevyes.calzadoapp.presentation.admin;

import android.app.Activity;
import android.app.DatePickerDialog;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Toast;

import com.kevyes.calzadoapp.data.db.DatabaseHelper;
import com.kevyes.calzadoapp.domain.service.AuditoriaService;
import com.kevyes.calzadoapp.presentation.common.Ui;
import com.kevyes.calzadoapp.presentation.login.LoginActivity;
import com.kevyes.calzadoapp.security.SessionManager;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.List;
import java.util.Locale;

public class AdminActivity extends Activity {
    private static final int CREATE_DOCUMENT_REQUEST = 2001;
    private DatabaseHelper database;
    private SessionManager session;
    private AuditoriaService auditoriaService;
    private EditText employeeDocument;
    private EditText dateFrom;
    private EditText dateTo;
    private LinearLayout reportContainer;
    private String pendingCsv;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        database = new DatabaseHelper(this);
        session = new SessionManager(this);
        auditoriaService = new AuditoriaService(database);
        if (!session.isLoggedIn() || !"ADMINISTRADOR".equals(session.getRole())) {
            goLogin();
            return;
        }

        LinearLayout root = Ui.page(this);
        root.addView(Ui.title(this, "Módulo Administrativo"));
        root.addView(Ui.label(this, "Administrador: " + session.getName()));

        employeeDocument = new EditText(this);
        employeeDocument.setHint("Documento vendedor (opcional)");
        root.addView(employeeDocument);

        dateFrom = new EditText(this);
        dateFrom.setHint("Fecha inicial yyyy-MM-dd");
        root.addView(dateFrom);
        Button fromButton = Ui.button(this, "Seleccionar fecha inicial");
        root.addView(fromButton);
        fromButton.setOnClickListener(v -> pickDate(dateFrom));

        dateTo = new EditText(this);
        dateTo.setHint("Fecha final yyyy-MM-dd");
        root.addView(dateTo);
        Button toButton = Ui.button(this, "Seleccionar fecha final");
        root.addView(toButton);
        toButton.setOnClickListener(v -> pickDate(dateTo));

        Button filter = Ui.button(this, "Consultar auditoría");
        root.addView(filter);
        filter.setOnClickListener(v -> loadReport());

        Button export = Ui.button(this, "Exportar reporte CSV");
        root.addView(export);
        export.setOnClickListener(v -> exportCsv());

        Button logout = Ui.button(this, "Cerrar sesión");
        root.addView(logout);
        logout.setOnClickListener(v -> logout());

        ScrollView scroll = new ScrollView(this);
        reportContainer = new LinearLayout(this);
        reportContainer.setOrientation(LinearLayout.VERTICAL);
        scroll.addView(reportContainer);
        root.addView(scroll, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1));

        setContentView(root);
        dateFrom.setText(todayString());
        dateTo.setText(todayString());
        loadReport();
    }

    private String todayString() {
        return new SimpleDateFormat("yyyy-MM-dd", Locale.getDefault()).format(Calendar.getInstance().getTime());
    }

    private void pickDate(EditText target) {
        Calendar c = Calendar.getInstance();
        new DatePickerDialog(this, (view, year, month, dayOfMonth) ->
                target.setText(String.format(Locale.getDefault(), "%04d-%02d-%02d", year, month + 1, dayOfMonth)),
                c.get(Calendar.YEAR), c.get(Calendar.MONTH), c.get(Calendar.DAY_OF_MONTH)).show();
    }

    private long parseDate(String text, boolean endOfDay) throws ParseException {
        java.util.Date date = new SimpleDateFormat("yyyy-MM-dd", Locale.getDefault()).parse(text);
        Calendar c = Calendar.getInstance();
        c.setTime(date);
        if (endOfDay) {
            c.set(Calendar.HOUR_OF_DAY, 23);
            c.set(Calendar.MINUTE, 59);
            c.set(Calendar.SECOND, 59);
            c.set(Calendar.MILLISECOND, 999);
        } else {
            c.set(Calendar.HOUR_OF_DAY, 0);
            c.set(Calendar.MINUTE, 0);
            c.set(Calendar.SECOND, 0);
            c.set(Calendar.MILLISECOND, 0);
        }
        return c.getTimeInMillis();
    }

    private long[] getRange() throws ParseException {
        long from = parseDate(dateFrom.getText().toString().trim(), false);
        long to = parseDate(dateTo.getText().toString().trim(), true);
        if (from > to) throw new IllegalArgumentException("La fecha inicial no puede ser posterior a la fecha final.");
        return new long[]{from, to};
    }

    private void loadReport() {
        try {
            long[] range = getRange();
            List<String> rows = auditoriaService.consultar(employeeDocument.getText().toString(), range[0], range[1]);
            reportContainer.removeAllViews();
            if (rows.isEmpty()) {
                reportContainer.addView(Ui.label(this, "No hay movimientos para el filtro."));
            } else {
                for (String row : rows) reportContainer.addView(Ui.card(this));
                // Recreate cards with text to keep the code/readability simple.
                reportContainer.removeAllViews();
                for (String row : rows) {
                    LinearLayout card = Ui.card(this);
                    card.addView(Ui.label(this, row));
                    reportContainer.addView(card);
                }
            }
        } catch (Exception e) {
            Toast.makeText(this, e.getMessage(), Toast.LENGTH_SHORT).show();
        }
    }

    private void exportCsv() {
        try {
            long[] range = getRange();
            pendingCsv = auditoriaService.exportarCsv(employeeDocument.getText().toString(), range[0], range[1]);
            Intent intent = new Intent(Intent.ACTION_CREATE_DOCUMENT);
            intent.addCategory(Intent.CATEGORY_OPENABLE);
            intent.setType("text/csv");
            intent.putExtra(Intent.EXTRA_TITLE, "auditoria_calzado.csv");
            startActivityForResult(intent, CREATE_DOCUMENT_REQUEST);
        } catch (Exception e) {
            Toast.makeText(this, e.getMessage(), Toast.LENGTH_SHORT).show();
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == CREATE_DOCUMENT_REQUEST && resultCode == RESULT_OK && data != null) {
            Uri uri = data.getData();
            try (java.io.OutputStream output = getContentResolver().openOutputStream(uri)) {
                output.write(pendingCsv.getBytes(java.nio.charset.StandardCharsets.UTF_8));
                Toast.makeText(this, "Reporte exportado correctamente.", Toast.LENGTH_LONG).show();
            } catch (Exception e) {
                Toast.makeText(this, "No se pudo exportar: " + e.getMessage(), Toast.LENGTH_SHORT).show();
            }
        }
    }

    private void logout() {
        session.logout();
        goLogin();
    }

    private void goLogin() {
        Intent intent = new Intent(this, LoginActivity.class);
        intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_NEW_TASK);
        startActivity(intent);
        finish();
    }
}
