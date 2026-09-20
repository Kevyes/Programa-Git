package com.kevyes.calzadoapp.security;

import com.kevyes.calzadoapp.data.db.DatabaseHelper;
import com.kevyes.calzadoapp.data.model.Employee;

public class AuthService {
    private final DatabaseHelper database;

    public AuthService(DatabaseHelper database) {
        this.database = database;
    }

    public Employee authenticate(String username, String password, String expectedRole) {
        if (username == null || password == null || expectedRole == null) return null;
        if (!"1234".equals(password)) return null;

        String document;
        switch (expectedRole) {
            case "EMPLEADO_POS": document = "1001"; break;
            case "CLIENTE_VIRTUAL": document = "2001"; break;
            case "ADMINISTRADOR": document = "3001"; break;
            default: return null;
        }
        if (!username.equals("empleado") && !username.equals("cliente") && !username.equals("admin")) return null;
        if (!roleMatchesUsername(username, expectedRole)) return null;
        return database.findEmployeeByDocument(document);
    }

    private boolean roleMatchesUsername(String username, String role) {
        return ("empleado".equals(username) && "EMPLEADO_POS".equals(role))
                || ("cliente".equals(username) && "CLIENTE_VIRTUAL".equals(role))
                || ("admin".equals(username) && "ADMINISTRADOR".equals(role));
    }
}
