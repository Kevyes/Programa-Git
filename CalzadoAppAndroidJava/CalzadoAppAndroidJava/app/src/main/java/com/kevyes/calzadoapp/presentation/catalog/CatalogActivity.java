package com.kevyes.calzadoapp.presentation.catalog;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import com.kevyes.calzadoapp.data.db.DatabaseHelper;
import com.kevyes.calzadoapp.data.model.CartItem;
import com.kevyes.calzadoapp.data.model.Shoe;
import com.kevyes.calzadoapp.domain.service.VentaService;
import com.kevyes.calzadoapp.presentation.common.Ui;
import com.kevyes.calzadoapp.presentation.login.LoginActivity;
import com.kevyes.calzadoapp.security.SessionManager;

import java.util.ArrayList;
import java.util.List;

public class CatalogActivity extends Activity {
    private DatabaseHelper database;
    private SessionManager session;
    private VentaService ventaService;
    private Spinner sizeSpinner;
    private Spinner colorSpinner;
    private LinearLayout productsContainer;
    private TextView cartSummary;
    private final List<CartItem> cart = new ArrayList<>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        database = new DatabaseHelper(this);
        session = new SessionManager(this);
        ventaService = new VentaService(database);
        if (!session.isLoggedIn() || !"CLIENTE_VIRTUAL".equals(session.getRole())) {
            goLogin();
            return;
        }

        LinearLayout root = Ui.page(this);
        root.addView(Ui.title(this, "Módulo Virtual (Cliente)"));
        root.addView(Ui.label(this, "Cliente: " + session.getName()));

        sizeSpinner = new Spinner(this);
        sizeSpinner.setAdapter(new ArrayAdapter<>(this, android.R.layout.simple_spinner_dropdown_item,
                new String[]{"TODAS", "39", "40", "41", "42"}));
        root.addView(sizeSpinner);

        colorSpinner = new Spinner(this);
        colorSpinner.setAdapter(new ArrayAdapter<>(this, android.R.layout.simple_spinner_dropdown_item,
                new String[]{"TODOS", "Negro", "Blanco", "Rojo", "Azul"}));
        root.addView(colorSpinner);

        Button filter = Ui.button(this, "Filtrar catálogo");
        root.addView(filter);
        filter.setOnClickListener(v -> refreshProducts());

        cartSummary = Ui.label(this, "Carrito: 0 ítems - $0");
        root.addView(cartSummary);

        Button checkout = Ui.button(this, "Procesar compra en línea");
        root.addView(checkout);
        checkout.setOnClickListener(v -> checkout());

        Button logout = Ui.button(this, "Cerrar sesión");
        root.addView(logout);
        logout.setOnClickListener(v -> logout());

        ScrollView scroll = new ScrollView(this);
        productsContainer = new LinearLayout(this);
        productsContainer.setOrientation(LinearLayout.VERTICAL);
        scroll.addView(productsContainer);
        root.addView(scroll, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1));

        setContentView(root);
        refreshProducts();
    }

    private void refreshProducts() {
        productsContainer.removeAllViews();
        String size = String.valueOf(sizeSpinner.getSelectedItem());
        String color = String.valueOf(colorSpinner.getSelectedItem());
        List<Shoe> shoes = database.getAvailableShoes(size, color);
        for (Shoe shoe : shoes) {
            LinearLayout card = Ui.card(this);
            card.addView(Ui.label(this, shoe.toString() + "\nPrecio: " + Ui.money(shoe.getPrice())));
            Button add = Ui.button(this, "Agregar al carrito");
            card.addView(add);
            productsContainer.addView(card);
            add.setOnClickListener(v -> {
                addToCart(shoe);
                Toast.makeText(this, "Agregado: " + shoe, Toast.LENGTH_SHORT).show();
            });
        }
        if (shoes.isEmpty()) productsContainer.addView(Ui.label(this, "No hay productos con stock disponible para el filtro seleccionado."));
    }

    private void addToCart(Shoe shoe) {
        for (int i = 0; i < cart.size(); i++) {
            CartItem item = cart.get(i);
            if (item.getShoe().getIdZapato() == shoe.getIdZapato()) {
                cart.set(i, new CartItem(shoe, item.getQuantity() + 1));
                updateCartSummary();
                return;
            }
        }
        cart.add(new CartItem(shoe, 1));
        updateCartSummary();
    }

    private void updateCartSummary() {
        int quantity = 0;
        double total = 0;
        for (CartItem item : cart) {
            quantity += item.getQuantity();
            total += item.getSubtotal();
        }
        cartSummary.setText("Carrito: " + quantity + " ítems - " + Ui.money(total));
    }

    private void checkout() {
        try {
            long saleId = ventaService.procesarCompraVirtual(cart);
            Toast.makeText(this, "Compra procesada. Venta #" + saleId, Toast.LENGTH_LONG).show();
            cart.clear();
            updateCartSummary();
            refreshProducts();
        } catch (Exception e) {
            Toast.makeText(this, e.getMessage(), Toast.LENGTH_SHORT).show();
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
