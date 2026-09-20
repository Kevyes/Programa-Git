package com.kevyes.calzadoapp.domain.service;

import com.kevyes.calzadoapp.data.db.DatabaseHelper;
import com.kevyes.calzadoapp.data.model.CartItem;

import java.util.List;

/** Servicio del módulo de ventas virtuales. */
public class VentaService {
    private final DatabaseHelper database;

    public VentaService(DatabaseHelper database) {
        this.database = database;
    }

    public long procesarCompraVirtual(List<CartItem> cart) {
        return database.buyOnline(cart);
    }
}
