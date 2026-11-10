package com.yoder.ejercicio1E2E.stepdefinitions;

import com.yoder.ejercicio1E2E.actors.ActorUsuario;
import com.yoder.ejercicio1E2E.tasks.TareaDeAgregarAlCarrito;
import com.yoder.ejercicio1E2E.utils.TestContext;
import io.cucumber.java.After;
import io.cucumber.java.Before;
import io.cucumber.java.en.When;
import java.util.Arrays;

public class PasosAgregarAlCarrito {

    @Before
    public void setUp() throws Exception {
        ActorUsuario.inicializar();
    }

    @After
    public void tearDown() {
        ActorUsuario.limpiar();
    }

    @When("el usuario agrega dos productos al carrito")
    public void elUsuarioAgregaDosProductosAlCarrito() {
        ActorUsuario.obtener().attemptsTo(
                TareaDeAgregarAlCarrito.agregarProductos(Arrays.asList("Sauce Labs Backpack", "Sauce Labs Bolt T-Shirt"))
        );
    }
}

