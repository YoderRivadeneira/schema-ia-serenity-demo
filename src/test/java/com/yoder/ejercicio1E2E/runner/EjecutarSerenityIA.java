package com.yoder.ejercicio1E2E.runner;

import io.cucumber.junit.CucumberOptions;
import net.serenitybdd.cucumber.CucumberWithSerenity;
import org.junit.runner.RunWith;

@RunWith(CucumberWithSerenity.class)
@CucumberOptions(
        features = "src/test/java/com/yoder/ejercicio1E2E/features",
        glue = "com.yoder.ejercicio1E2E.stepdefinitions",
        tags = "@IA",
        snippets = CucumberOptions.SnippetType.CAMELCASE,
        plugin = {"pretty"}
)
public class EjecutarSerenityIA {
}
