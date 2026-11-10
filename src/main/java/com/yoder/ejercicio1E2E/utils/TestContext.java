package com.yoder.ejercicio1E2E.utils;

import io.github.bonigarcia.wdm.WebDriverManager;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;

public class TestContext {
    private static WebDriver driver;
    private static Path tempProfileDir;

    public static void initialize() throws IOException {
        if (driver == null) {
            WebDriverManager.chromedriver().setup();

            ChromeOptions options = new ChromeOptions();
            
            tempProfileDir = Files.createTempDirectory("chrome-profile");
            options.addArguments("user-data-dir=" + tempProfileDir.toAbsolutePath());
            
            options.addArguments("--password-store=basic");
            options.addArguments("--disable-blink-features=AutomationControlled");
            options.addArguments("--disable-password-generation");
            options.addArguments("--disable-password-manager-reauthentication");
            options.addArguments("--disable-autofill-keyboard-accessory-view");
            options.addArguments("--disable-autofill");
            options.addArguments("--disable-extensions");
            options.addArguments("--disable-plugins");
            options.addArguments("--disable-notifications");
            options.addArguments("--no-first-run");
            options.addArguments("--no-default-browser-check");
            options.addArguments("--disable-default-apps");
            options.addArguments("--disable-component-update");
            options.addArguments("--disable-sync");
            options.addArguments("--disable-infobars");
            options.addArguments("--no-sandbox");
            options.addArguments("--disable-dev-shm-usage");
          //  options.addArguments("--headless");
            options.addArguments("--disable-gpu");
            
            Map<String, Object> prefs = new HashMap<>();
            prefs.put("credentials_enable_service", false);
            prefs.put("profile.password_manager_enabled", false);
            prefs.put("profile.password_manager_leak_detection", false);
            prefs.put("profile.default_content_settings.popups", 0);
            prefs.put("profile.managed_default_content_settings.popups", 0);
            prefs.put("profile.default_content_setting_values.notifications", 2);
            prefs.put("profile.default_content_setting_values.automatic_downloads", 1);
            prefs.put("profile.managed_default_content_settings.notifications", 2);
            prefs.put("safebrowsing.enabled", true);
            
            options.setExperimentalOption("prefs", prefs);

            driver = new ChromeDriver(options);

        }
    }

    public static WebDriver getDriver() {
        return driver;
    }

    public static void tearDown() {
        if (driver != null) {
            driver.quit();
            driver = null;
        }
        
        // Limpiar el directorio temporal de Chrome
        if (tempProfileDir != null) {
            try {
                Files.walk(tempProfileDir)
                        .sorted(java.util.Comparator.reverseOrder())
                        .forEach(path -> {
                            try {
                                Files.delete(path);
                            } catch (IOException e) {
                                // Ignorar errores al limpiar
                            }
                        });
            } catch (IOException e) {
                // Ignorar errores al limpiar
            }
        }
    }
}

