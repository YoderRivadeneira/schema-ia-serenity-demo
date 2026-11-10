package com.yoder.ejercicio1E2E.utils;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.io.InputStream;

public final class CatalogoIaCompra {
    private static final String CATALOGO_PATH = "catalog-ia/catalog-ia.json";
    private static final String PROP_NOMBRE = "dataia.nombre";
    private static final String PROP_APELLIDO = "dataia.apellido";
    private static final String PROP_CODIGO_POSTAL = "dataia.codigoPostal";
    private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();
    private static JsonNode catalogoCache;

    private CatalogoIaCompra() {
    }

    public static DatosFijos obtenerDatosFijos(String casoCatalogo) {
        JsonNode fijos = obtenerCaso(casoCatalogo).path("fijos");
        String usuario = obtenerCampoRequerido(fijos, "usuario", casoCatalogo);
        String password = obtenerCampoRequerido(fijos, "password", casoCatalogo);
        String mensajeEsperado = obtenerCampoRequerido(fijos, "mensajeEsperado", casoCatalogo);
        return new DatosFijos(usuario, password, mensajeEsperado);
    }

    public static DatosVariables obtenerDatosVariablesRuntime(String casoCatalogo) {
        JsonNode variables = obtenerCaso(casoCatalogo).path("variables");
        if (variables.isMissingNode() || variables.isNull()) {
            throw new IllegalStateException("El catalogo IA no define 'variables' para el caso '" + casoCatalogo + "'");
        }

        String nombre = obtenerPropiedadRequerida(PROP_NOMBRE);
        String apellido = obtenerPropiedadRequerida(PROP_APELLIDO);
        String codigoPostal = obtenerPropiedadRequerida(PROP_CODIGO_POSTAL);

        return new DatosVariables(nombre, apellido, codigoPostal);
    }

    private static String obtenerPropiedadRequerida(String propiedad) {
        String valor = System.getProperty(propiedad, "").trim();
        if (valor.isEmpty()) {
            throw new IllegalStateException(
                    "Falta la propiedad de ejecucion '" + propiedad + "'. " +
                    "Ejemplo: -D" + propiedad + "=valor"
            );
        }
        return valor;
    }

    private static String obtenerCampoRequerido(JsonNode nodo, String campo, String casoCatalogo) {
        String valor = nodo.path(campo).asText("").trim();
        if (valor.isEmpty()) {
            throw new IllegalStateException(
                    "El catalogo IA no define 'fijos." + campo + "' para el caso '" + casoCatalogo + "'"
            );
        }
        return valor;
    }

    private static JsonNode obtenerCaso(String casoCatalogo) {
        JsonNode caso = obtenerCatalogo().path(casoCatalogo);
        if (caso.isMissingNode() || caso.isNull()) {
            throw new IllegalStateException("No existe el caso '" + casoCatalogo + "' en " + CATALOGO_PATH);
        }
        return caso;
    }

    private static JsonNode obtenerCatalogo() {
        if (catalogoCache != null) {
            return catalogoCache;
        }

        synchronized (CatalogoIaCompra.class) {
            if (catalogoCache == null) {
                try (InputStream inputStream = CatalogoIaCompra.class.getClassLoader().getResourceAsStream(CATALOGO_PATH)) {
                    if (inputStream == null) {
                        throw new IllegalStateException("No se encontro el archivo " + CATALOGO_PATH);
                    }
                    catalogoCache = OBJECT_MAPPER.readTree(inputStream);
                } catch (IOException e) {
                    throw new IllegalStateException("No se pudo leer el archivo " + CATALOGO_PATH, e);
                }
            }
        }
        return catalogoCache;
    }

    public static final class DatosFijos {
        private final String usuario;
        private final String password;
        private final String mensajeEsperado;

        public DatosFijos(String usuario, String password, String mensajeEsperado) {
            this.usuario = usuario;
            this.password = password;
            this.mensajeEsperado = mensajeEsperado;
        }

        public String getUsuario() {
            return usuario;
        }

        public String getPassword() {
            return password;
        }

        public String getMensajeEsperado() {
            return mensajeEsperado;
        }
    }

    public static final class DatosVariables {
        private final String nombre;
        private final String apellido;
        private final String codigoPostal;

        public DatosVariables(String nombre, String apellido, String codigoPostal) {
            this.nombre = nombre;
            this.apellido = apellido;
            this.codigoPostal = codigoPostal;
        }

        public String getNombre() {
            return nombre;
        }

        public String getApellido() {
            return apellido;
        }

        public String getCodigoPostal() {
            return codigoPostal;
        }
    }
}
