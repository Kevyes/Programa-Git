package com.kevyes.calzadoapp.domain.service;

import com.kevyes.calzadoapp.data.db.DatabaseHelper;

import java.util.List;

/** Servicio para consulta y exportación de auditoría. */
public class AuditoriaService {
    private final DatabaseHelper database;

    public AuditoriaService(DatabaseHelper database) {
        this.database = database;
    }

    public List<String> consultar(String employeeDocument, long from, long to) {
        return database.getAuditLines(employeeDocument, from, to);
    }

    public String exportarCsv(String employeeDocument, long from, long to) {
        return database.buildAuditCsv(employeeDocument, from, to);
    }
}
