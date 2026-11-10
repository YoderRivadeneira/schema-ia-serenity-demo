================================================================================
EJERCICIO E2E - FLUJO DE COMPRA EN SAUCEDEMO
Prueba Funcional Automatizada con SerenityBDD y ScreenPlay
================================================================================

DESCRIPCION DEL PROYECTO:
Este proyecto realiza una prueba funcional automatizada (Prueba E2E) para un 
flujo de compra en la página https://www.saucedemo.com/ utilizando SerenityBDD 
con ScreenPlay.

INCLUYE: Integración continua (DevOps) CI/CD con GitHub Actions

================================================================================
PREREQUISITOS
================================================================================

Antes de ejecutar el proyecto, asegúrate de cumplir con los siguientes requisitos:

✓ Sistema Operativo: Windows 10 / macOS / Linux
✓ IDE Recomendado: IntelliJ IDEA 2023.1 o superior
✓ JDK: Versión 17 o superior (configurado en JAVA_HOME)
✓ Google Chrome: Cualquier versión (preferiblemente la última)
✓ Gradle Wrapper: Incluido en el proyecto (no necesita instalación global)

================================================================================
PASOS PARA EJECUTAR EL PROYECTO
================================================================================

PASO 1: CLONAR EL REPOSITORIO
________________________________

Abre una terminal y ejecuta:

    git clone https://github.com/YoderRivadeneira/ejercicio1E2E
    cd ejercicio1E2E

PASO 2: CONFIGURAR PERMISOS (IMPORTANTE EN LINUX/MAC)
________________________________

Asigna permisos de ejecución al Gradle Wrapper:

    chmod +x ./gradlew

(Nota: Este comando es ejecutado automáticamente en CI/CD con GitHub Actions)

PASO 3: CONFIGURAR LA VERSION DE GRADLE
________________________________

Asegúrate de ejecutar este comando en la raíz del proyecto:

    ./gradlew wrapper --gradle-version 7.6.1

PASO 4: DESCARGAR DEPENDENCIAS
________________________________

Verifica que todas las dependencias se instalen correctamente:

    ./gradlew build

Esto descargará todas las dependencias declaradas en build.gradle
(También puedes hacerlo desde el IDE con las opciones de Gradle)

PASO 5: EJECUTAR LAS PRUEBAS
________________________________

OPCION A - Desde línea de comandos:

    ./gradlew test --tests "com.devsu.ejercicio1E2E.runner.EjecutarSerenity" --info

OPCION B - Desde IntelliJ IDEA:

    1. Localiza la clase "EjecutarSerenity" en el árbol del proyecto
    2. Click derecho sobre ella
    3. Selecciona "Run EjecutarSerenity"
    
    O también puedes:
    1. Ubicar el icono verde de Run
    2. Ejecutar "EjecutarSerenity"
    3. Si no está configurado, ve a Run > Edit Configuration
    4. Asigna el siguiente comando:
       :test --tests "com.devsu.ejercicio1E2E.runner.EjecutarSerenity"

PASO 6: VISUALIZAR LOS REPORTES
________________________________

Después de ejecutar las pruebas, los reportes se generan automáticamente.

Ruta del reporte:
    ejercicio1E2E/build/reports/tests/test/index.html

Abre este archivo en tu navegador para ver:
    • Detalles de cada escenario ejecutado
    • Tiempo de ejecución por escenario
    • Acceso a errores o excepciones
    • Estado final de las pruebas (éxito o fallo)
    • Capturas de pantalla automáticas de cada paso

================================================================================
FLUJO DE COMPRA AUTOMATIZADO
================================================================================

El proyecto automatiza el siguiente flujo en SauceDemo:

1. Autenticación con credenciales:
   - Usuario: standard_user
   - Contraseña: secret_sauce

2. Agregar dos productos al carrito

3. Visualizar el carrito

4. Completar el formulario de compra

5. Finalizar la compra

6. Verificar el mensaje de confirmación: "THANK YOU FOR YOUR ORDER"

================================================================================
ESTRUCTURA DEL PROYECTO
================================================================================

src/
├── main/
│   └── java/
│       └── com/devsu/ejercicio1E2E/
│           ├── tasks/                 # Implementaciones de tareas (ScreenPlay)
│           ├── questions/             # Preguntas para verificar estados
│           ├── actors/                # Configuración del actor
│           ├── models/                # Modelos para datos del JSON
│           ├── utils/                 # Utilidades (lectura JSON, WebDriver)
│           ├── interfaces/            # Selectores de elementos web
│           └── resources/
│               └── datos.json         # Datos de prueba
│
└── test/
    └── java/
        └── com/devsu/ejercicio1E2E/
            ├── runner/                # Clase de ejecución (Runner)
            ├── stepdefinitions/       # Definición de pasos de escenarios
            └── features/              # Escenarios en Cucumber

================================================================================
INTEGRACION CI/CD CON GITHUB ACTIONS
================================================================================

El proyecto incluye integración continua automática. Cuando hagas push a main,
se ejecutará automáticamente:

✓ Checkout del código
✓ Setup de JDK 17
✓ Cache de dependencias Gradle
✓ Asignación de permisos al Gradle Wrapper: chmod +x ./gradlew
✓ Verificación y configuración de Gradle 7.6.1
✓ Ejecución de pruebas en modo headless
✓ Carga de reportes automáticamente

URL para ver ejecuciones:
    https://github.com/YoderRivadeneira/ejercicio1E2E/actions

================================================================================
SOLUCIÓN DE PROBLEMAS
================================================================================

PROBLEMA: "Permission denied: ./gradlew"
SOLUCIÓN: Ejecuta: chmod +x ./gradlew

PROBLEMA: "JAVA_HOME no está configurado"
SOLUCIÓN: Configura la variable de entorno JAVA_HOME apuntando a tu 
          instalación de JDK 17

PROBLEMA: Las pruebas no se ejecutan en el IDE
SOLUCIÓN: Configura Run > Edit Configuration con:
          :test --tests "com.devsu.ejercicio1E2E.runner.EjecutarSerenity"

PROBLEMA: Errores de dependencias
SOLUCIÓN: Ejecuta: ./gradlew clean build

================================================================================
NOTAS ADICIONALES
================================================================================

• El proyecto incluye Gradle Wrapper configurado para no necesitar
  instalación global de Gradle

• Las capturas de pantalla se toman automáticamente durante la ejecución
  y se guardan en la carpeta target/

• Los reportes de Cucumber se generan automáticamente en:
  build/reports/tests/test/index.html

• Para más detalles sobre la estructura y configuración, consulta README.md


