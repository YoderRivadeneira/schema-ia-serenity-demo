package com.yoder.ejercicio1E2E.tasks;
import net.serenitybdd.screenplay.Actor;
import net.serenitybdd.screenplay.Task;
import net.serenitybdd.screenplay.actions.Click;

import java.util.List;

import static net.serenitybdd.screenplay.Tasks.instrumented;

public class TareaDeAgregarAlCarrito implements Task {

    private final List<String> productos;

    public TareaDeAgregarAlCarrito(List<String> productos) {
        this.productos = productos;
    }

    public static TareaDeAgregarAlCarrito agregarProductos(List<String> productos) {
        return instrumented(TareaDeAgregarAlCarrito.class, productos);
    }

    @Override
    public <T extends Actor> void performAs(T actor) {
        productos.forEach(producto -> {

            actor.attemptsTo(
                    Click.on("//button[contains(@id, '" + producto.toLowerCase().replace(" ", "-") + "')]")
            );
        });
    }
}

