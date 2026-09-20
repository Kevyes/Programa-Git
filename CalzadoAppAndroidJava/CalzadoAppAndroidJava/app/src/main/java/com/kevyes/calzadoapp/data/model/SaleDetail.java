package com.kevyes.calzadoapp.data.model;

public class SaleDetail {
    private long idDetail;
    private long saleId;
    private long shoeId;
    private int quantity;
    private double subtotal;

    public SaleDetail(long idDetail, long saleId, long shoeId, int quantity, double subtotal) {
        this.idDetail = idDetail;
        this.saleId = saleId;
        this.shoeId = shoeId;
        this.quantity = quantity;
        this.subtotal = subtotal;
    }

    public long getIdDetail() { return idDetail; }
    public long getSaleId() { return saleId; }
    public long getShoeId() { return shoeId; }
    public int getQuantity() { return quantity; }
    public double getSubtotal() { return subtotal; }
}
