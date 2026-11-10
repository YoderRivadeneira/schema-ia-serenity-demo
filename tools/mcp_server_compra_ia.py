#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional


SERVER_NAME = "compra-ia-local"
SERVER_VERSION = "1.0.1"
PROTOCOL_VERSION = "2025-11-25"


def read_message() -> Optional[Dict[str, Any]]:
    first_line = sys.stdin.buffer.readline()
    if not first_line:
        return None

    stripped_first_line = first_line.lstrip()
    if stripped_first_line.startswith(b"{"):
        chunks = [first_line]
        while True:
            payload = b"".join(chunks).decode("utf-8", errors="replace").strip()
            if not payload:
                return None
            try:
                return json.loads(payload)
            except json.JSONDecodeError:
                next_line = sys.stdin.buffer.readline()
                if not next_line:
                    raise
                chunks.append(next_line)

    headers: Dict[str, str] = {}
    line = first_line
    while True:
        if line in (b"\r\n", b"\n"):
            break
        decoded = line.decode("utf-8", errors="replace").strip()
        if ":" in decoded:
            key, value = decoded.split(":", 1)
            headers[key.strip().lower()] = value.strip()
        line = sys.stdin.buffer.readline()
        if not line:
            return None

    content_length = int(headers.get("content-length", "0"))
    if content_length <= 0:
        return None

    body = sys.stdin.buffer.read(content_length)
    if not body:
        return None
    return json.loads(body.decode("utf-8"))


def send_message(message: Dict[str, Any]) -> None:
    payload = json.dumps(message, ensure_ascii=False).encode("utf-8")
    header = f"Content-Length: {len(payload)}\r\n\r\n".encode("utf-8")
    sys.stdout.buffer.write(header)
    sys.stdout.buffer.write(payload)
    sys.stdout.buffer.flush()


def send_result(request_id: Any, result: Dict[str, Any]) -> None:
    send_message(
        {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result,
        }
    )


def send_error(request_id: Any, code: int, message: str) -> None:
    send_message(
        {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message,
            },
        }
    )


def tool_definition() -> Dict[str, Any]:
    return {
        "collect_compra_ia_context": {
            "name": "collect_compra_ia_context",
            "description": (
                "Consulta fuentes del schema/policy y devuelve candidatos para que la IA "
                "decida nombre, apellido y codigo postal."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "case": {"type": "string", "default": "compra-saucedemo"},
                    "catalog": {
                        "type": "string",
                        "default": "src/test/resources/catalog-ia/catalog-ia.json",
                    },
                    "policy": {
                        "type": "string",
                        "default": "src/test/resources/catalog-ia/mcp-policy.json",
                    },
                    "limit": {"type": "integer", "default": 12},
                },
                "additionalProperties": False,
            },
        },
        "run_compra_ia": {
            "name": "run_compra_ia",
            "description": (
                "Ejecuta el test IA con valores ya decididos por IA (nombre, apellido, codigoPostal)."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "case": {"type": "string", "default": "compra-saucedemo"},
                    "nombre": {"type": "string"},
                    "apellido": {"type": "string"},
                    "codigoPostal": {"type": "string"},
                    "nombreSource": {"type": "string", "default": "ia-decision"},
                    "apellidoSource": {"type": "string", "default": "ia-decision"},
                    "codigoPostalSource": {"type": "string", "default": "ia-decision"},
                    "nombreEvidence": {"type": "string", "default": ""},
                    "apellidoEvidence": {"type": "string", "default": ""},
                    "codigoPostalEvidence": {"type": "string", "default": ""},
                    "aiDecisionId": {"type": "string", "default": ""},
                    "decisionReasoning": {"type": "string", "default": ""},
                    "candidatePoolHash": {"type": "string", "default": ""},
                    "dryRun": {"type": "boolean", "default": False},
                    "catalog": {
                        "type": "string",
                        "default": "src/test/resources/catalog-ia/catalog-ia.json",
                    },
                    "policy": {
                        "type": "string",
                        "default": "src/test/resources/catalog-ia/mcp-policy.json",
                    }
                },
                "required": ["nombre", "apellido", "codigoPostal"],
                "additionalProperties": False,
            },
        },
    }


def run_script(command: list[str]) -> Dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[1]
    script_path = command[1] if len(command) > 1 else ""
    if not Path(script_path).exists():
        return {
            "content": [{"type": "text", "text": f"No existe script: {script_path}"}],
            "isError": True,
        }

    completed = subprocess.run(
        command,
        cwd=str(repo_root),
        capture_output=True,
        text=True,
    )
    output = completed.stdout
    if completed.stderr.strip():
        output = (output + "\n" + completed.stderr).strip()

    if completed.returncode != 0:
        return {
            "content": [
                {
                    "type": "text",
                    "text": output or f"run_compra_ia falló con código {completed.returncode}",
                }
            ],
            "isError": True,
        }

    return {"content": [{"type": "text", "text": output}], "isError": False}


def collect_compra_ia_context(arguments: Dict[str, Any]) -> Dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "tools" / "mcp_ejecutar_compra_ia.py"
    case_name = str(arguments.get("case", "compra-saucedemo"))
    catalog = str(arguments.get("catalog", "src/test/resources/catalog-ia/catalog-ia.json"))
    policy = str(arguments.get("policy", "src/test/resources/catalog-ia/mcp-policy.json"))
    limit = int(arguments.get("limit", 12))
    command = [
        "python3",
        str(script_path),
        "--case",
        case_name,
        "--catalog",
        catalog,
        "--policy",
        policy,
        "collect",
        "--limit",
        str(limit),
    ]
    return run_script(command)


def run_compra_ia_tool(arguments: Dict[str, Any]) -> Dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "tools" / "mcp_ejecutar_compra_ia.py"
    case_name = str(arguments.get("case", "compra-saucedemo"))
    catalog = str(arguments.get("catalog", "src/test/resources/catalog-ia/catalog-ia.json"))
    policy = str(arguments.get("policy", "src/test/resources/catalog-ia/mcp-policy.json"))
    nombre = str(arguments.get("nombre", "")).strip()
    apellido = str(arguments.get("apellido", "")).strip()
    codigo_postal = str(arguments.get("codigoPostal", "")).strip()
    if not nombre or not apellido or not codigo_postal:
        return {
            "content": [{
                "type": "text",
                "text": (
                    "Faltan valores para ejecutar. Primero usa collect_compra_ia_context, "
                    "luego decide con IA y llama run_compra_ia con nombre/apellido/codigoPostal."
                ),
            }],
            "isError": True,
        }

    command = [
        "python3",
        str(script_path),
        "--case",
        case_name,
        "--catalog",
        catalog,
        "--policy",
        policy,
        "execute",
        "--nombre",
        nombre,
        "--apellido",
        apellido,
        "--codigo-postal",
        codigo_postal,
        "--nombre-source",
        str(arguments.get("nombreSource", "ia-decision")),
        "--apellido-source",
        str(arguments.get("apellidoSource", "ia-decision")),
        "--codigo-postal-source",
        str(arguments.get("codigoPostalSource", "ia-decision")),
        "--nombre-evidence",
        str(arguments.get("nombreEvidence", "")),
        "--apellido-evidence",
        str(arguments.get("apellidoEvidence", "")),
        "--codigo-postal-evidence",
        str(arguments.get("codigoPostalEvidence", "")),
    ]
    ai_decision_id = str(arguments.get("aiDecisionId", "")).strip()
    if ai_decision_id:
        command.extend(["--ai-decision-id", ai_decision_id])
    decision_reasoning = str(arguments.get("decisionReasoning", "")).strip()
    if decision_reasoning:
        command.extend(["--decision-reasoning", decision_reasoning])
    candidate_pool_hash = str(arguments.get("candidatePoolHash", "")).strip()
    if candidate_pool_hash:
        command.extend(["--candidate-pool-hash", candidate_pool_hash])
    if bool(arguments.get("dryRun", False)):
        command.append("--dry-run")

    return run_script(command)


def handle_request(message: Dict[str, Any]) -> None:
    method = message.get("method")
    request_id = message.get("id")
    params = message.get("params", {})

    if method == "initialize":
        send_result(
            request_id,
            {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            },
        )
        return

    if method == "tools/list":
        tools = tool_definition()
        send_result(request_id, {"tools": [tools["collect_compra_ia_context"], tools["run_compra_ia"]]})
        return

    if method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        if tool_name == "collect_compra_ia_context":
            result = collect_compra_ia_context(arguments)
            send_result(request_id, result)
            return
        if tool_name == "run_compra_ia":
            result = run_compra_ia_tool(arguments)
            send_result(request_id, result)
            return
        else:
            send_error(request_id, -32602, f"Herramienta no soportada: {tool_name}")
            return

    if method == "ping":
        send_result(request_id, {})
        return

    if request_id is not None:
        send_error(request_id, -32601, f"Método no soportado: {method}")


def main() -> int:
    while True:
        message = read_message()
        if message is None:
            return 0
        if "id" not in message:
            continue
        handle_request(message)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(0)
