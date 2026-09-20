package com.kevyes.calzadoapp.data.model;

public class Sale {
    public static final String PRESENTIAL = "PRESENCIAL";
    public static final String VIRTUAL = "VIRTUAL";

    private long idSale;
    private long date;
    private String channel;
    private double total;

    public Sale(long idSale, long date, String channel, double total) {
        this.idSale = idSale;
        this.date = date;
        this.channel = channel;
        this.total = total;
    }

    public long getIdSale() { return idSale; }
    public long getDate() { return date; }
    public String getChannel() { return channel; }
    public double getTotal() { return total; }
}
