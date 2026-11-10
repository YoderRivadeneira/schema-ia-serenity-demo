package com.yoder.ejercicio1E2E.questions;
import net.serenitybdd.screenplay.waits.WaitUntil;
import static net.serenitybdd.screenplay.matchers.WebElementStateMatchers.isVisible;
import com.yoder.ejercicio1E2E.interfaces.CheckoutInterface;
import net.serenitybdd.screenplay.Actor;
import net.serenitybdd.screenplay.Question;
import net.serenitybdd.screenplay.questions.TextContent;

public class PreguntaMensajeConfirmacion implements Question<String> {

    public static PreguntaMensajeConfirmacion esVisible() {
        return new PreguntaMensajeConfirmacion();
    }

    @Override
    public String answeredBy(Actor actor) {
              actor.attemptsTo(
            WaitUntil.the(CheckoutInterface.MENSAJE_CONFIRMACION, isVisible()).forNoMoreThan(10).seconds()
        );
        return TextContent.of(CheckoutInterface.MENSAJE_CONFIRMACION)
                .answeredBy(actor);
    }
}

