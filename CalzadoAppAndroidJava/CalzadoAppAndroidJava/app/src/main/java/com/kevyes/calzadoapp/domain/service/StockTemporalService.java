package com.kevyes.calzadoapp.domain.service;

import com.kevyes.calzadoapp.data.db.DatabaseHelper;

/**
 * Servicio del módulo de inventario/préstamos temporales.
 * La persistencia y las transacciones SQL quedan encapsuladas en DatabaseHelper.
 */
public class StockTemporalService {
    private final DatabaseHelper database;

    public StockTemporalService(DatabaseHelper database) {
        this.database = database;
    }

    public long registrarSalida(long employeeId, long shoeId, int quantity) {
        return database.registerTemporaryLoan(employeeId, shoeId, quantity);
    }

    public void devolver(long loanId) {
        database.returnTemporaryLoan(loanId);
    }

    public long vender(long loanId) {
        return database.sellTemporaryLoan(loanId);
    }
}
