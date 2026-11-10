package com.yoder.ejercicio1E2E.stepdefinitions;

import com.yoder.ejercicio1E2E.actors.ActorUsuario;
import com.yoder.ejercicio1E2E.tasks.TareaIrAlCheckout;
import com.yoder.ejercicio1E2E.tasks.TareaDeCompletarCompra;
import com.yoder.ejercicio1E2E.utils.CatalogoIaCompra;
import com.yoder.ejercicio1E2E.utils.CatalogoIaContext;
import com.yoder.ejercicio1E2E.questions.PreguntaMensajeConfirmacion;
import io.cucumber.java.en.And;
import io.cucumber.java.en.Then;
import static net.serenitybdd.screenplay.GivenWhenThen.seeThat;
import static org.hamcrest.Matchers.containsString;

public class PasosCompletarCompra {

    @And("procede al checkout de los productos agregados al carrito")
    public void procedeAlCheckout() {
        ActorUsuario.obtener().attemptsTo(
                TareaIrAlCheckout.ir()
        );
    }

    @And("completa el formulario de compra con {string}, {string} y {string}")
    public void completaFormularioCon(String nombre, String apellido, String codigoPostal) {
        ActorUsuario.obtener().attemptsTo(
                TareaDeCompletarCompra.conDatos(nombre, apellido, codigoPostal)
        );
    }

    @And("completa el formulario de compra con datos IA del catalogo {string}")
    public void completaFormularioConDatosIADelCatalogo(String casoCatalogo) {
        CatalogoIaCompra.DatosVariables datosVariables = CatalogoIaCompra.obtenerDatosVariablesRuntime(casoCatalogo);
        ActorUsuario.obtener().attemptsTo(
                TareaDeCompletarCompra.conDatos(
                        datosVariables.getNombre(),
                        datosVariables.getApellido(),
                        datosVariables.getCodigoPostal()
                )
        );
    }

    @And("completa el formulario de compra con datos IA del catalogo activo")
    public void completaFormularioConDatosIADelCatalogoActivo() {
        String casoCatalogo = CatalogoIaContext.getCasoActivoRequerido();
        completaFormularioConDatosIADelCatalogo(casoCatalogo);
    }

    @Then("el mensaje de correcto debe ser {string}")
    public void elMensajeDeConfirmacionDeberiaSer(String mensajeEsperado) {
        ActorUsuario.obtener().should(
                seeThat(
                        "El mensaje de confirmación",
                        actor -> PreguntaMensajeConfirmacion.esVisible().answeredBy(actor).toLowerCase(),
                        containsString(mensajeEsperado.toLowerCase())
                )
        );
    }

    @Then("el mensaje de correcto del catalogo IA {string} debe ser visible")
    public void elMensajeDelCatalogoIADebeSerVisible(String casoCatalogo) {
        String mensajeEsperado = CatalogoIaCompra.obtenerDatosFijos(casoCatalogo).getMensajeEsperado();
        elMensajeDeConfirmacionDeberiaSer(mensajeEsperado);
    }

    @Then("el mensaje de correcto del catalogo IA activo debe ser visible")
    public void elMensajeDelCatalogoIAActivoDebeSerVisible() {
        String casoCatalogo = CatalogoIaContext.getCasoActivoRequerido();
        elMensajeDelCatalogoIADebeSerVisible(casoCatalogo);
    }
}
