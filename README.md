# Nuevo paradigma: test + conocimiento + ejecución IA (Serenity + MCP)
Esta implementación de schemas de conocimiento evoluciona la automatización de pruebas al erradicar los datos estáticos o "quemados" que proporcionamos a los test .


Es una guía práctica de como implementar schemas de conocmientos para nuestros tests (aplicado a un flujo de compra en línea en la página de pruebas SauceDemo: https://www.saucedemo.com/).


Este proyecto muestra cómo implementar **schemas de conocimiento** sobre los datos de entrada de un test E2E.
En lugar de quemar valores o depender de entradas fijas en `Scenario Outline`, archivos `.txt`, fuentes offline o bases de datos rígidas por corrida, aquí se define el conocimiento: qué dato se necesita, cómo obtenerlo o generarlo en runtime y qué reglas contractuales debe cumplir.

La IA consume ese schema por medio de MCP, consulta fuentes en vivo, decide los valores y ejecuta el test con trazabilidad.
El modo clásico se mantiene como fallback.

## DEMO:



https://github.com/user-attachments/assets/1f21c30f-9b59-4c51-a3a8-62814c70dc9c





## Catálogo activo como schema de conocimiento

En lugar de pasar `nombre`, `apellido` y `codigoPostal` de forma fija:

- el feature IA consume un **catálogo activo** que funciona como **schema de conocimiento**,
- el schema define la semántica del dato, cómo rastrearlo (`comoObtenerlo`) y qué reglas debe cumplir,
- el servidor/motor MCP usa ese schema para resolver y rankear candidatos desde fuentes configuradas,
- la IA decide los valores finales y el motor inyecta propiedades runtime (`-Ddataia.*`) al runner IA.

Resultado: el test sigue siendo legible y estable, pero los datos variables son dinámicos y trazables.

## Antes vs Después (Feature)

### Antes (estático)

```gherkin
Scenario Outline: Completar una compra satisfactoriamente
  Given el usuario se logea con "<usuario>" y "<password>"
  When el usuario agrega dos productos al carrito
  And procede al checkout de los productos agregados al carrito
  And completa el formulario de compra con "<nombre>", "<apellido>" y "<codigoPostal>"
  Then el mensaje de correcto debe ser "<mensajeEsperado>"

Examples:
  | usuario       | password     | nombre | apellido | codigoPostal | mensajeEsperado          |
  | standard_user | secret_sauce | NOMBRE_ESTATICO | APELLIDO_ESTATICO | CODIGO_POSTAL_ESTATICO | THANK YOU FOR YOUR ORDER |
```

### Después (knowledge-driven + IA)

```gherkin
@IA @compraSaucesCatalogoIA
Scenario: Completar una compra satisfactoriamente con catalogo IA
  Given se carga el catalogo IA "compra-saucedemo"
  And el usuario se logea con credenciales del catalogo IA activo
  When el usuario agrega dos productos al carrito
  And procede al checkout de los productos agregados al carrito
  And completa el formulario de compra con datos IA del catalogo activo
  Then el mensaje de correcto del catalogo IA activo debe ser visible
```

## Antes vs Después (Datos)

### Antes (datos directos en el feature)

```text
usuario=standard_user
password=secret_sauce
nombre=NOMBRE_ESTATICO
apellido=APELLIDO_ESTATICO
codigoPostal=CODIGO_POSTAL_ESTATICO
mensajeEsperado=THANK YOU FOR YOUR ORDER
```

### Después (schema de conocimiento + policy MCP)

```json
{
  "compra-saucedemo": {
    "fijos": {
      "usuario": "standard_user",
      "password": "secret_sauce",
      "mensajeEsperado": "THANK YOU FOR YOUR ORDER"
    },
    "variables": {
      "nombre": {
        "descripcion": "Nombre de personaje de Dragon Ball...",
        "comoObtenerlo": ["https://es.wikipedia.org/wiki/Anexo:Personajes_de_Dragon_Ball"]
      },
      "apellido": {
        "descripcion": "Apellido latino...",
        "comoObtenerlo": ["https://es.wikipedia.org/wiki/Anexo:Apellidos_m%C3%A1s_comunes_en_Espa%C3%B1a_e_Hispanoam%C3%A9rica"]
      },
      "codigoPostal": {
        "descripcion": "Codigo postal real de Loja, Ecuador",
        "comoObtenerlo": ["https://codigo-postal.co/ecuador/loja/loja/"]
      }
    }
  }
}
```

El MCP consulta fuentes, arma candidatos, la IA decide y luego se ejecuta el test con `-Ddataia.*`.

## Estructura clave del ecosistema

```text
src/test/resources/catalog-ia/catalog-ia.json      # Schema de conocimiento (fuentes y semántica)
src/test/resources/catalog-ia/mcp-policy.json      # Policy de control (validaciones y mapeo runtime)
tools/mcp_ejecutar_compra_ia.py                    # Motor CLI local (collect + execute)
dist/compra-ia-local/index.js                      # Servidor MCP stdio (Node) para IDE/agentes
src/test/java/com/yoder/ejercicio1E2E/runner/EjecutarSerenity.java     # Runner clásico (fallback, not @IA)
src/test/java/com/yoder/ejercicio1E2E/runner/EjecutarSerenityIA.java   # Runner IA (@IA)
```

## Escenario IA (limpio de datos concretos)

```gherkin
@IA @compraSaucesCatalogoIA
Scenario: Completar una compra satisfactoriamente con catalogo IA
  Given se carga el catalogo IA "compra-saucedemo"
  And el usuario se logea con credenciales del catalogo IA activo
  When el usuario agrega dos productos al carrito
  And procede al checkout de los productos agregados al carrito
  And completa el formulario de compra con datos IA del catalogo activo
  Then el mensaje de correcto del catalogo IA activo debe ser visible
```

## Prerrequisitos

- Java 17+
- Chrome instalado
- `python3` disponible (usar `/usr/bin/env python3`)
- Gradle Wrapper del repo

## Modos de ejecución

El ecosistema permite dos modalidades: **modo autónomo por agente** (vía servidor MCP) y **modo manual/pipeline** (vía CLI).

### Opción A) Modo autónomo por agente (Servidor MCP)

Cuando trabajas desde un cliente/agente compatible con MCP, el agente puede usar directamente las tools del servidor local:

- `collect_compra_ia_context` para recolectar contexto y candidatos.
- `run_compra_ia` para ejecutar con los valores decididos por IA.

Configura el servidor MCP local así:

```json
{
  "mcpServers": {
    "compra-ia-local": {
      "command": "node",
      "args": ["dist/compra-ia-local/index.js"]
    }
  }
}
```
luego ejecuta el siguiente prompt en el chat de tu agente 

```
hola ejecuta mi test   @IA @compraSaucesCatalogoIA con SCHEMA_IA
```
### Opción B) Modo manual / orquestación por pipeline (CLI)

#### 1) Recolectar contexto y candidatos en tiempo real

```bash
/usr/bin/env python3 tools/mcp_ejecutar_compra_ia.py --case compra-saucedemo collect --limit 8
```

Este paso no ejecuta el test. Solo devuelve candidatos + evidencia + `candidatePoolHash` para la decisión IA.

#### 2) Ejecutar con valores decididos por IA

```bash
/usr/bin/env python3 tools/mcp_ejecutar_compra_ia.py --case compra-saucedemo execute --nombre <valor_ia_nombre> --apellido <valor_ia_apellido> --codigo-postal <valor_ia_codigo_postal>
```

`<valor_ia_nombre>`, `<valor_ia_apellido>` y `<valor_ia_codigo_postal>` deben venir de la decisión IA usando el contexto del paso `collect`.

Versión auditada (recomendada):

```bash
/usr/bin/env python3 tools/mcp_ejecutar_compra_ia.py --case compra-saucedemo execute --nombre <valor_ia_nombre> --apellido <valor_ia_apellido> --codigo-postal <valor_ia_codigo_postal> --ai-decision-id ia-run-001 --decision-reasoning "Seleccion por cumplimiento de reglas y score de candidatos" --candidate-pool-hash <hash_de_collect>
```

#### 3) Previsualizar ejecución (dry-run, sin correr Gradle)

```bash
/usr/bin/env python3 tools/mcp_ejecutar_compra_ia.py --case compra-saucedemo execute --nombre <valor_ia_nombre> --apellido <valor_ia_apellido> --codigo-postal <valor_ia_codigo_postal> --dry-run
```

#### 4) Modo clásico (fallback, sin capa IA)

```bash
./gradlew test --tests "com.yoder.ejercicio1E2E.runner.EjecutarSerenity"
```

## Cómo funciona el motor analítico local

1. **Carga de configuración**: consume `catalog-ia.json` y `mcp-policy.json`.
2. **Extracción y filtrado**: consulta fuentes por campo (`nombre`, `apellido`, `codigoPostal`) y normaliza texto.
3. **Puntuación**: arma un pool de candidatos por frecuencia/relevancia y conserva evidencia textual.
4. **Decisión IA**: la IA elige valores finales usando contexto + reglas del schema.
5. **Validación de contratos**: en `execute`, valida longitudes y regex antes de correr el test.
6. **Inyección runtime**: construye Gradle para `EjecutarSerenityIA` con:
   - `-Ddataia.nombre=...`
   - `-Ddataia.apellido=...`
   - `-Ddataia.codigoPostal=...`
7. **Ejecución**: dispara el runner IA con tags configurados.

## Trazabilidad

Cada corrida guarda resolución en:

`target/catalog-ia/ultimo-resuelto.json`

Incluye por campo:
- valor resuelto,
- fuente utilizada,
- evidencia textual.

Además guarda auditoría:
- `aiDecisionId`
- `decisionReasoning`
- `candidatePoolHash`
- `catalogPath` / `policyPath`
- timestamps UTC

`candidatePoolHash` se calcula con SHA-256 sobre el contexto recolectado para control de integridad de la decisión.

## Ventajas del enfoque

- **Menos fragilidad**: desacopla lógica funcional y datos variables.
- **Escalabilidad**: una policy puede gobernar múltiples casos.
- **Auditoría real**: evidencia + metadatos de decisión por corrida.
- **Reutilización**: mismo motor para distintos escenarios.
- **Evolución natural a IA**: el test consume conocimiento, no literals por ejecución.

## Nota de ejecución visual

Si quieres ver el navegador, ejecuta localmente desde IDE/terminal de tu máquina.  
En contextos remotos/no GUI el test puede correr sin mostrar ventana.

## CI/CD

El repo mantiene ejecución automatizada con GitHub Actions:

`https://github.com/YoderRivadeneira/ejercicio1E2E/actions`
