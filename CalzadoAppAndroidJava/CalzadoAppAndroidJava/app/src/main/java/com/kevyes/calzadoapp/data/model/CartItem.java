package com.kevyes.calzadoapp.data.model;

public class CartItem {
    private final Shoe shoe;
    private final int quantity;

    public CartItem(Shoe shoe, int quantity) {
        this.shoe = shoe;
        this.quantity = quantity;
    }

    public Shoe getShoe() { return shoe; }
    public int getQuantity() { return quantity; }
    public double getSubtotal() { return shoe.getPrice() * quantity; }
}
