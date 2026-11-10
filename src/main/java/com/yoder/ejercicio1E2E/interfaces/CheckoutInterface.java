package com.yoder.ejercicio1E2E.interfaces;

import net.serenitybdd.screenplay.targets.Target;

public class CheckoutInterface {

    public static final Target NOMBRE_FIELD = Target.the("Campo de nombre")
            .locatedBy("#first-name");
    public static final Target APELLIDO_FIELD = Target.the("Campo de apellido")
            .locatedBy("#last-name");
    public static final Target CODIGO_POSTAL_FIELD = Target.the("Campo de código postal")
            .locatedBy("#postal-code");
    public static final Target BOTON_CONTINUAR = Target.the("Botón continuar al resumen")
            .locatedBy("#continue");
    public static final Target BOTON_FINISH = Target.the("Botón para finalizar la compra")
            .locatedBy("#finish");
    public static final Target MENSAJE_CONFIRMACION = Target.the("Mensaje de confirmación de la compra")
            .locatedBy(".complete-header");
}

