package com.yoder.ejercicio1E2E.utils;

public final class CatalogoIaContext {
    private static final ThreadLocal<String> CASO_ACTIVO = new ThreadLocal<>();

    private CatalogoIaContext() {
    }

    public static void setCasoActivo(String casoCatalogo) {
        CASO_ACTIVO.set(casoCatalogo);
    }

    public static String getCasoActivoRequerido() {
        String caso = CASO_ACTIVO.get();
        if (caso == null || caso.trim().isEmpty()) {
            throw new IllegalStateException(
                    "No hay catalogo IA activo. Debes ejecutar el step: " +
                    "\"Given se carga el catalogo IA \\\"<caso>\\\"\""
            );
        }
        return caso;
    }

    public static void clear() {
        CASO_ACTIVO.remove();
    }
}
