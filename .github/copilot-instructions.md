# Instrucciones para GitHub Copilot — SCHEMA_IA

## Regla SCHEMA_IA (orquestador IA basado en schema)

Si el mensaje contiene `SCHEMA_IA`, usa el MCP `compra-ia-local` para resolver y ejecutar el flujo IA según el schema/policy activo.

Flujo general:

1. Recolectar contexto con `collect_compra_ia_context`.
   - Si el usuario envía `case`, `catalog` o `policy`, usarlos.
   - Si no los envía, usar los valores por defecto del MCP.
2. Seleccionar valores desde los candidatos, respetando validaciones del policy.
   - Usar selección aleatoria dentro del top de candidatos válidos (recomendado: top 5 por campo).
   - Evitar repetir exactamente la última combinación resuelta (`nombre`, `apellido`, `codigoPostal`) cuando existan alternativas válidas.
   - Si no hay historial o no hay alternativa, seleccionar cualquier combinación válida.
3. Ejecutar con `run_compra_ia` usando los campos requeridos por el schema actual (por ejemplo: `nombre`, `apellido`, `codigoPostal`).

Reglas operativas:
- Si el usuario pide solo análisis/contexto, ejecutar únicamente `collect_compra_ia_context`.
- Si el usuario pide ejecución completa, ejecutar `collect_compra_ia_context` y luego `run_compra_ia`.
- Si el usuario pide simulación, usar `dryRun: true`.
- Si falta información clave para ejecutar, pedirla antes de correr.
