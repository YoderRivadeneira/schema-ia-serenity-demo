package com.yoder.ejercicio1E2E.interfaces;

import net.serenitybdd.screenplay.targets.Target;

public class LoginInterface {

    public static final Target USERNAME_FIELD = Target.the("campo de usuario")
            .locatedBy("#user-name");
    public static final Target PASSWORD_FIELD = Target.the("campo de contraseña")
            .locatedBy("#password");
    public static final Target LOGIN_BUTTON = Target.the("botón de login")
            .locatedBy("#login-button");
}

