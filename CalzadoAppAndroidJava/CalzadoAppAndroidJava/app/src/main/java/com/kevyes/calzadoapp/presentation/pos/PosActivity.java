package com.kevyes.calzadoapp.presentation.pos;

import android.app.Activity;
import android.os.Bundle;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import com.kevyes.calzadoapp.data.db.DatabaseHelper;
import com.kevyes.calzadoapp.data.model.Shoe;
import com.kevyes.calzadoapp.data.model.TemporaryLoan;
import com.kevyes.calzadoapp.domain.service.StockTemporalService;
import com.kevyes.calzadoapp.presentation.common.Ui;
import com.kevyes.calzadoapp.presentation.login.LoginActivity;
import com.kevyes.calzadoapp.security.SessionManager;

import android.content.Intent;
import java.util.ArrayList;
import java.util.List;

public class PosActivity extends Activity {
    private DatabaseHelper database;
    private SessionManager session;
    private StockTemporalService stockService;
    private Spinner shoeSpinner;
    private EditText quantity;
    private LinearLayout loansContainer;
    private List<Shoe> shoes = new ArrayList<>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        database = new DatabaseHelper(this);
        session = new SessionManager(this);
        stockService = new StockTemporalService(database);
        if (!session.isLoggedIn() || !"EMPLEADO_POS".equals(session.getRole())) {
            goLogin();
            return;
        }

        LinearLayout root = Ui.page(this);
        root.addView(Ui.title(this, "Módulo Presencial (Vendedor)"));
        root.addView(Ui.label(this, "Bienvenido: " + session.getName()));

        shoeSpinner = new Spinner(this);
        loadShoes();
        root.addView(shoeSpinner);

        quantity = new EditText(this);
        quantity.setHint("Cantidad");
        quantity.setInputType(2);
        root.addView(quantity);

        Button register = Ui.button(this, "Registrar salida temporal");
        root.addView(register);
        register.setOnClickListener(v -> registerLoan());

        Button logout = Ui.button(this, "Cerrar sesión");
        root.addView(logout);
        logout.setOnClickListener(v -> logout());

        root.addView(Ui.label(this, "Zapatos asignados a mi cuenta"));
        ScrollView scroll = new ScrollView(this);
        loansContainer = new LinearLayout(this);
        loansContainer.setOrientation(LinearLayout.VERTICAL);
        scroll.addView(loansContainer);
        root.addView(scroll, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1));

        setContentView(root);
        refreshLoans();
    }

    private void loadShoes() {
        shoes = database.getAllShoes();
        List<String> names = new ArrayList<>();
        for (Shoe shoe : shoes) names.add(shoe.toString() + " | " + Ui.money(shoe.getPrice()));
        shoeSpinner.setAdapter(new ArrayAdapter<>(this, android.R.layout.simple_spinner_dropdown_item, names));
    }

    private void registerLoan() {
        if (shoes.isEmpty()) return;
        int qty;
        try {
            qty = Integer.parseInt(quantity.getText().toString().trim());
        } catch (Exception e) {
            Toast.makeText(this, "Escribe una cantidad válida.", Toast.LENGTH_SHORT).show();
            return;
        }
        Shoe shoe = shoes.get(shoeSpinner.getSelectedItemPosition());
        try {
            stockService.registrarSalida(session.getUserId(), shoe.getIdZapato(), qty);
            Toast.makeText(this, "Salida temporal registrada.", Toast.LENGTH_SHORT).show();
            quantity.setText("");
            refreshLoans();
        } catch (Exception e) {
            Toast.makeText(this, e.getMessage(), Toast.LENGTH_SHORT).show();
        }
    }

    private void refreshLoans() {
        loansContainer.removeAllViews();
        for (TemporaryLoan loan : database.getActiveLoans(session.getUserId())) {
            Shoe shoe = database.getShoe(loan.getShoeId());
            LinearLayout card = Ui.card(this);
            TextView info = Ui.label(this,
                    "Préstamo #" + loan.getIdPrestamo() + "\n" + shoe +
                            "\nCantidad: " + loan.getQuantity() +
                            "\nSalida: " + Ui.dateTime(loan.getDateExit()) +
                            "\nEstado: " + loan.getState());
            card.addView(info);

            LinearLayout actions = new LinearLayout(this);
            actions.setOrientation(LinearLayout.HORIZONTAL);
            Button returnButton = Ui.button(this, "Devolver");
            Button sellButton = Ui.button(this, "Vender");
            actions.addView(returnButton, new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1));
            actions.addView(sellButton, new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1));
            card.addView(actions);
            loansContainer.addView(card);

            returnButton.setOnClickListener(v -> {
                try {
                    stockService.devolver(loan.getIdPrestamo());
                    Toast.makeText(this, "Calzado devuelto al stock disponible.", Toast.LENGTH_SHORT).show();
                    refreshLoans();
                } catch (Exception e) {
                    Toast.makeText(this, e.getMessage(), Toast.LENGTH_SHORT).show();
                }
            });
            sellButton.setOnClickListener(v -> {
                try {
                    stockService.vender(loan.getIdPrestamo());
                    Toast.makeText(this, "Venta presencial registrada y préstamo liquidado.", Toast.LENGTH_SHORT).show();
                    refreshLoans();
                } catch (Exception e) {
                    Toast.makeText(this, e.getMessage(), Toast.LENGTH_SHORT).show();
                }
            });
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
