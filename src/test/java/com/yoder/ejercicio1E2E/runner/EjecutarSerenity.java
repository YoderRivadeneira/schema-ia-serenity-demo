package com.yoder.ejercicio1E2E.runner;
import org.junit.runner.RunWith;
import net.serenitybdd.cucumber.CucumberWithSerenity;
import io.cucumber.junit.CucumberOptions;

@RunWith(CucumberWithSerenity.class)
@CucumberOptions(
        features = "src/test/java/com/yoder/ejercicio1E2E/features",
        glue = "com.yoder.ejercicio1E2E.stepdefinitions",
        tags = "not @IA",
        snippets = CucumberOptions.SnippetType.CAMELCASE,
        plugin = {"pretty"}
)
public class EjecutarSerenity {
}
