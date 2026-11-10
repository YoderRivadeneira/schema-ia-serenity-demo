package com.yoder.ejercicio1E2E.interfaces;

import net.serenitybdd.screenplay.targets.Target;

public class CarritoInterface {

    public static final Target PRIMER_PRODUCTO = Target.the("Primer producto en la lista")
            .locatedBy("#add-to-cart-sauce-labs-backpack");

    public static final Target SEGUNDO_PRODUCTO = Target.the("Segundo producto en la lista")
            .locatedBy("#add-to-cart-sauce-labs-bike-light");

    public static final Target BOTON_CARRITO = Target.the("Botón para ir al carrito")
            .locatedBy(".shopping_cart_link");

    public static final Target BOTON_CHECKOUT = Target.the("Botón para proceder al checkout")
            .locatedBy("#checkout");


    public static Target productoConNombre(String nombre) {
        return Target.the("Producto con nombre: " + nombre)
                .locatedBy("//div[text()='" + nombre + "']/following-sibling::button");
    }

}

