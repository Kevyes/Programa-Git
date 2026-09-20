package com.kevyes.calzadoapp.data.model;

public class TemporaryLoan {
    public static final String RESERVED = "RESERVADO";
    public static final String RETURNED = "DEVUELTO";
    public static final String SOLD = "VENDIDO";

    private long idPrestamo;
    private long employeeId;
    private long shoeId;
    private long dateExit;
    private long dateReturn;
    private int quantity;
    private String state;

    public TemporaryLoan(long idPrestamo, long employeeId, long shoeId, long dateExit, long dateReturn, int quantity, String state) {
        this.idPrestamo = idPrestamo;
        this.employeeId = employeeId;
        this.shoeId = shoeId;
        this.dateExit = dateExit;
        this.dateReturn = dateReturn;
        this.quantity = quantity;
        this.state = state;
    }

    public long getIdPrestamo() { return idPrestamo; }
    public long getEmployeeId() { return employeeId; }
    public long getShoeId() { return shoeId; }
    public long getDateExit() { return dateExit; }
    public long getDateReturn() { return dateReturn; }
    public int getQuantity() { return quantity; }
    public String getState() { return state; }

    public void setIdPrestamo(long idPrestamo) { this.idPrestamo = idPrestamo; }
    public void setDateReturn(long dateReturn) { this.dateReturn = dateReturn; }
    public void setState(String state) { this.state = state; }
}
