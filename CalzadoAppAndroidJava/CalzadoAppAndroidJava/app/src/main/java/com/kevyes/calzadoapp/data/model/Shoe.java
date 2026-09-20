package com.kevyes.calzadoapp.data.model;

public class Shoe {
    private long idZapato;
    private String reference;
    private String brand;
    private int size;
    private String color;
    private String model;
    private double price;

    public Shoe(long idZapato, String reference, String brand, int size, String color, String model, double price) {
        this.idZapato = idZapato;
        this.reference = reference;
        this.brand = brand;
        this.size = size;
        this.color = color;
        this.model = model;
        this.price = price;
    }

    public long getIdZapato() { return idZapato; }
    public String getReference() { return reference; }
    public String getBrand() { return brand; }
    public int getSize() { return size; }
    public String getColor() { return color; }
    public String getModel() { return model; }
    public double getPrice() { return price; }

    @Override
    public String toString() {
        return brand + " " + model + " - Talla " + size + " - " + color;
    }
}
