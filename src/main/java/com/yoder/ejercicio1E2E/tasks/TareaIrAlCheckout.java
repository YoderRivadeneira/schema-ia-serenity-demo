package com.yoder.ejercicio1E2E.tasks;

import com.yoder.ejercicio1E2E.interfaces.CarritoInterface;
import net.serenitybdd.screenplay.Actor;
import net.serenitybdd.screenplay.Task;
import net.serenitybdd.screenplay.actions.Click;

import static net.serenitybdd.screenplay.Tasks.instrumented;

public class TareaIrAlCheckout implements Task {

    public static TareaIrAlCheckout ir() {
        return instrumented(TareaIrAlCheckout.class);
    }

    @Override
    public <T extends Actor> void performAs(T actor) {
        actor.attemptsTo(
                Click.on(CarritoInterface.BOTON_CARRITO),
                
                Click.on(CarritoInterface.BOTON_CHECKOUT)
        );
    }
}

