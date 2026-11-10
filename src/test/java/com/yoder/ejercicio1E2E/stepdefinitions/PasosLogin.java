package com.yoder.ejercicio1E2E.stepdefinitions;

import com.yoder.ejercicio1E2E.actors.ActorUsuario;
import com.yoder.ejercicio1E2E.tasks.TareaDeLogin;
import com.yoder.ejercicio1E2E.utils.CatalogoIaCompra;
import com.yoder.ejercicio1E2E.utils.CatalogoIaContext;
import io.cucumber.java.After;
import io.cucumber.java.Before;
import io.cucumber.java.en.Given;

public class PasosLogin {

    @Before
    public void setUp() throws Exception {
        ActorUsuario.inicializar();
    }

    @After
    public void tearDown() {
        CatalogoIaContext.clear();
        ActorUsuario.limpiar();
    }

    @Given("se carga el catalogo IA {string}")
    public void seCargaElCatalogoIA(String casoCatalogo) {
        CatalogoIaCompra.obtenerDatosFijos(casoCatalogo);
        CatalogoIaContext.setCasoActivo(casoCatalogo);
    }

    @Given("el usuario se logea con {string} y {string}")
    public void elUsuarioSeLogeaCon(String usuario, String password) {
        ActorUsuario.obtener().attemptsTo(
                TareaDeLogin.conCredenciales(usuario, password)
        );
    }

    @Given("el usuario se logea con credenciales del catalogo IA {string}")
    public void elUsuarioSeLogeaConCredencialesDelCatalogoIA(String casoCatalogo) {
        CatalogoIaCompra.DatosFijos datosFijos = CatalogoIaCompra.obtenerDatosFijos(casoCatalogo);
        ActorUsuario.obtener().attemptsTo(
                TareaDeLogin.conCredenciales(datosFijos.getUsuario(), datosFijos.getPassword())
        );
    }

    @Given("el usuario se logea con credenciales del catalogo IA activo")
    public void elUsuarioSeLogeaConCredencialesDelCatalogoIAActivo() {
        String casoCatalogo = CatalogoIaContext.getCasoActivoRequerido();
        elUsuarioSeLogeaConCredencialesDelCatalogoIA(casoCatalogo);
    }
}
