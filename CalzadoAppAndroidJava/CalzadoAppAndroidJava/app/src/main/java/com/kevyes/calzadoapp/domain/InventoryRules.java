package com.kevyes.calzadoapp.domain;

public final class InventoryRules {
    private InventoryRules() { }

    public static int availableAfterTemporaryExit(int available, int requested) {
        validateQuantity(requested);
        if (available < requested) throw new IllegalStateException("Stock disponible insuficiente.");
        return available - requested;
    }

    public static int testAfterTemporaryExit(int inTest, int requested) {
        validateQuantity(requested);
        return inTest + requested;
    }

    public static int availableAfterReturn(int available, int requested) {
        validateQuantity(requested);
        return available + requested;
    }

    public static int testAfterReturn(int inTest, int requested) {
        validateQuantity(requested);
        if (inTest < requested) throw new IllegalStateException("Stock en prueba insuficiente.");
        return inTest - requested;
    }

    public static double total(double unitPrice, int quantity) {
        validateQuantity(quantity);
        if (unitPrice < 0) throw new IllegalArgumentException("El precio no puede ser negativo.");
        return unitPrice * quantity;
    }

    private static void validateQuantity(int quantity) {
        if (quantity <= 0) throw new IllegalArgumentException("La cantidad debe ser mayor que cero.");
    }
}
