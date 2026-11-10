package com.yoder.ejercicio1E2E.actors;

import com.yoder.ejercicio1E2E.utils.TestContext;
import net.serenitybdd.screenplay.abilities.BrowseTheWeb;
import net.serenitybdd.screenplay.actors.OnStage;

import net.serenitybdd.screenplay.Actor;
public class ActorUsuario {

    private static final String NOMBRE_ACTOR = "UsuarioQAYoder";

    private ActorUsuario() {
    }

    public static void inicializar() throws Exception {
        TestContext.initialize();
        OnStage.setTheStage(new net.serenitybdd.screenplay.actors.Cast());
        OnStage.theActorCalled(NOMBRE_ACTOR).can(BrowseTheWeb.with(TestContext.getDriver()));
    }

    public static void limpiar() {
        TestContext.tearDown();
    }

    public static Actor obtener() {
        return OnStage.theActorCalled(NOMBRE_ACTOR);
    }
}

