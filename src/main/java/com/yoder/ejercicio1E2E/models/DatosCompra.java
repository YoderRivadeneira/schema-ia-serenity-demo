package com.yoder.ejercicio1E2E.models;

import java.util.List;

public class DatosCompra {
    private String usuario;
    private String password;
    private List<String> productos;
    private DatosFormulario datosCompra;


    public String getUsuario() {
        return usuario;
    }

    public void setUsuario(String usuario) {
        this.usuario = usuario;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public List<String> getProductos() {
        return productos;
    }

    public void setProductos(List<String> productos) {
        this.productos = productos;
    }

    public DatosFormulario getDatosCompra() {
        return datosCompra;
    }

    public void setDatosCompra(DatosFormulario datosCompra) {
        this.datosCompra = datosCompra;
    }


    public static class DatosFormulario {
        private String nombre;
        private String apellido;
        private String codigoPostal;


        public String getNombre() {
            return nombre;
        }

        public void setNombre(String nombre) {
            this.nombre = nombre;
        }

        public String getApellido() {
            return apellido;
        }

        public void setApellido(String apellido) {
            this.apellido = apellido;
        }

        public String getCodigoPostal() {
            return codigoPostal;
        }

        public void setCodigoPostal(String codigoPostal) {
            this.codigoPostal = codigoPostal;
        }
    }
}

