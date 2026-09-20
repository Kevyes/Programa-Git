package com.kevyes.calzadoapp.config;

/**
 * Punto único de configuración para la API REST del proyecto integrado.
 * La evidencia móvil funciona con SQLite local; esta clase deja preparada
 * la ubicación del backend sin obligar a la app académica a depender de él.
 */
public final class ApiConfig {
    private ApiConfig() { }

    public static final String BASE_URL = "http://10.0.2.2:8000/api/";
    public static final int CONNECT_TIMEOUT_MS = 10000;
    public static final int READ_TIMEOUT_MS = 10000;
}
