package com.yoder.ejercicio1E2E.tasks;
import net.serenitybdd.screenplay.waits.WaitUntil;
import static net.serenitybdd.screenplay.matchers.WebElementStateMatchers.isVisible;
import com.yoder.ejercicio1E2E.interfaces.CheckoutInterface;
import net.serenitybdd.screenplay.Actor;
import net.serenitybdd.screenplay.Task;
import net.serenitybdd.screenplay.abilities.BrowseTheWeb;
import net.serenitybdd.screenplay.actions.Click;
import net.serenitybdd.screenplay.actions.Enter;
import org.openqa.selenium.Keys;
import org.openqa.selenium.interactions.Actions;
import org.openqa.selenium.JavascriptExecutor;

import static net.serenitybdd.screenplay.Tasks.instrumented;

public class TareaDeCompletarCompra implements Task {

    private final String nombre;
    private final String apellido;
    private final String codigoPostal;

    public TareaDeCompletarCompra(String nombre, String apellido, String codigoPostal) {
        this.nombre = nombre;
        this.apellido = apellido;
        this.codigoPostal = codigoPostal;
    }

    public static TareaDeCompletarCompra conDatos(String nombre, String apellido, String codigoPostal) {
        return instrumented(TareaDeCompletarCompra.class, nombre, apellido, codigoPostal);
    }

    @Override
    public <T extends Actor> void performAs(T actor) {
        try {
            BrowseTheWeb browse = actor.abilityTo(BrowseTheWeb.class);
            
            actor.attemptsTo(
                    Enter.theValue(nombre).into(CheckoutInterface.NOMBRE_FIELD),
                    Enter.theValue(apellido).into(CheckoutInterface.APELLIDO_FIELD),
                    Enter.theValue(codigoPostal).into(CheckoutInterface.CODIGO_POSTAL_FIELD)
            );
            
            Thread.sleep(1000);
            cerrarPopupsChrome(actor);
            cerrarPopupsChromeConJavaScript(browse);
            
            actor.attemptsTo(
                    WaitUntil.the(CheckoutInterface.BOTON_CONTINUAR, isVisible()).forNoMoreThan(10).seconds(),
                    Click.on(CheckoutInterface.BOTON_CONTINUAR)
            );
            
            for (int i = 0; i < 6; i++) {
                Thread.sleep(1000);
                cerrarPopupsChrome(actor);
                cerrarPopupsChromeConJavaScript(browse);
            }
            
            actor.attemptsTo(
                    WaitUntil.the(CheckoutInterface.BOTON_FINISH, isVisible()).forNoMoreThan(25).seconds(),
                    Click.on(CheckoutInterface.BOTON_FINISH)
            );
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new RuntimeException(e);
        }
    }
    
    private void cerrarPopupsChrome(Actor actor) {
        try {
            BrowseTheWeb browse = actor.abilityTo(BrowseTheWeb.class);
            if (browse != null) {
                try {
                    new Actions(browse.getDriver())
                            .sendKeys(Keys.ESCAPE)
                            .perform();
                    Thread.sleep(500);
                } catch (Exception ignored) {
                }
            }
        } catch (Exception ignored) {
        }
    }
    
    private void cerrarPopupsChromeConJavaScript(BrowseTheWeb browse) {
        try {
            if (browse != null) {
                JavascriptExecutor js = (JavascriptExecutor) browse.getDriver();
                
                String script = 
                    "var modals = document.querySelectorAll('dialog, [role=\"dialog\"], .modal, .popup, [aria-modal=\"true\"]'); " +
                    "modals.forEach(function(modal) { " +
                    "  try { " +
                    "    modal.style.display = 'none'; " +
                    "    modal.remove(); " +
                    "  } catch(e) {} " +
                    "}); " +
                    "var closeButtons = document.querySelectorAll('button[aria-label*=\"Close\"], button[aria-label*=\"close\"], .close, [data-close]'); " +
                    "closeButtons.forEach(function(btn) { " +
                    "  try { " +
                    "    if (btn.offsetParent !== null) btn.click(); " +
                    "  } catch(e) {} " +
                    "});";
                
                js.executeScript(script);
                Thread.sleep(300);
            }
        } catch (Exception ignored) {
        }
    }
}

