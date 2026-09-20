package com.kevyes.calzadoapp.data.model;

public class Inventory {
    private long shoeId;
    private int stockAvailable;
    private int stockInTest;

    public Inventory(long shoeId, int stockAvailable, int stockInTest) {
        this.shoeId = shoeId;
        this.stockAvailable = stockAvailable;
        this.stockInTest = stockInTest;
    }

    public long getShoeId() { return shoeId; }
    public int getStockAvailable() { return stockAvailable; }
    public int getStockInTest() { return stockInTest; }
    public void setStockAvailable(int value) { this.stockAvailable = value; }
    public void setStockInTest(int value) { this.stockInTest = value; }
}
