package com.kevyes.calzadoapp.data.model;

public class Employee {
    private long idEmpleado;
    private String document;
    private String name;
    private String role;

    public Employee(long idEmpleado, String document, String name, String role) {
        this.idEmpleado = idEmpleado;
        this.document = document;
        this.name = name;
        this.role = role;
    }

    public long getIdEmpleado() { return idEmpleado; }
    public String getDocument() { return document; }
    public String getName() { return name; }
    public String getRole() { return role; }
}
