package com.yoder.ejercicio1E2E.tasks;

import com.yoder.ejercicio1E2E.interfaces.LoginInterface;
import net.serenitybdd.screenplay.Actor;
import net.serenitybdd.screenplay.Task;
import net.serenitybdd.screenplay.actions.Click;
import net.serenitybdd.screenplay.actions.Enter;
import net.serenitybdd.screenplay.actions.Open;
import net.serenitybdd.screenplay.waits.WaitUntil;

import static net.serenitybdd.screenplay.Tasks.instrumented;
import static net.serenitybdd.screenplay.matchers.WebElementStateMatchers.isVisible;

public class TareaDeLogin implements Task {

    private final String username;
    private final String password;

    public TareaDeLogin(String username, String password) {
        this.username = username;
        this.password = password;
    }

    public static TareaDeLogin conCredenciales(String username, String password) {
        return instrumented(TareaDeLogin.class, username, password);
    }
    @Override
    public <T extends Actor> void performAs(T actor) {
        actor.attemptsTo(
                Open.url("https://www.saucedemo.com/"),
                WaitUntil.the(LoginInterface.USERNAME_FIELD, isVisible()).forNoMoreThan(10).seconds(),
                Enter.theValue(username).into(LoginInterface.USERNAME_FIELD),
                Enter.theValue(password).into(LoginInterface.PASSWORD_FIELD),
                Click.on(LoginInterface.LOGIN_BUTTON)
        );
    }
}

