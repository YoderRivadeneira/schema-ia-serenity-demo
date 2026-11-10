#!/usr/bin/env python3
import argparse
from datetime import datetime, timezone
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
import uuid
from typing import Dict, List, Optional


USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/537.36 IA-MCP/2.0"
DEFAULT_TIMEOUT_SECONDS = 20
MAX_FETCH_ATTEMPTS = 2


@dataclass
class ResolvedField:
    value: str
    source: str
    evidence: str


def load_json(path: Path) -> Dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def fetch_html(url: str) -> str:
    last_error = ""
    for _ in range(MAX_FETCH_ATTEMPTS):
        command = [
            "curl",
            "-L",
            "--silent",
            "--show-error",
            "--max-time",
            str(DEFAULT_TIMEOUT_SECONDS),
            "--user-agent",
            USER_AGENT,
            url,
        ]
        completed = subprocess.run(command, capture_output=True, text=True)
        if completed.returncode == 0 and completed.stdout.strip():
            return completed.stdout
        last_error = completed.stderr.strip() or "respuesta vacia"
    raise RuntimeError(f"No se pudo obtener fuente '{url}': {last_error}")


def fetch_text(url: str) -> str:
    return normalize_html_to_text(fetch_html(url))


def normalize_html_to_text(html: str) -> str:
    no_script = re.sub(r"(?is)<script.*?>.*?</script>", " ", html)
    no_style = re.sub(r"(?is)<style.*?>.*?</style>", " ", no_script)
    no_tags = re.sub(r"(?is)<[^>]+>", " ", no_style)
    normalized = re.sub(r"\s+", " ", no_tags)
    return normalized.strip()


def first_evidence_snippet(text: str, token: str, size: int = 90) -> str:
    lower_text = text.lower()
    lower_token = token.lower()
    idx = lower_text.find(lower_token)
    if idx < 0:
        return token
    start = max(0, idx - size)
    end = min(len(text), idx + len(token) + size)
    return text[start:end].strip()


def as_source_list(entry: Dict) -> List[str]:
    raw = entry.get("comoObtenerlo", [])
    if isinstance(raw, list):
        return [str(value).strip() for value in raw if str(value).strip()]
    if isinstance(raw, str) and raw.strip():
        return [raw.strip()]
    return []


def select_sources(sources: List[str], resolution_config: Dict, field_name: str) -> List[str]:
    allowed_sources = [
        str(value).strip()
        for value in resolution_config.get("fuentesPermitidas", [])
        if str(value).strip()
    ]
    if not allowed_sources:
        return sources

    allowed_set = set(allowed_sources)
    selected = [source for source in sources if source in allowed_set]
    if not selected:
        raise RuntimeError(
            f"La resolucion de '{field_name}' define fuentesPermitidas, "
            "pero ninguna coincide con comoObtenerlo del catalogo IA"
        )
    return selected


def extract_tokens(text: str, token_regex: str, min_length: int, max_length: int, excluded_words: List[str]) -> Dict[str, int]:
    pattern = re.compile(token_regex)
    excluded = {word.strip().lower() for word in excluded_words if word.strip()}
    counts: Dict[str, int] = {}
    canonical: Dict[str, str] = {}
    for match in pattern.finditer(text):
        token = match.group(0).strip(" \t\r\n.,;:!?¡¿()[]{}<>\"'`´")
        if len(token) < min_length or len(token) > max_length:
            continue
        key = token.lower()
        if key in excluded:
            continue
        if any(char.isdigit() for char in token):
            continue
        cleaned = token.replace(" ", "").replace("-", "").replace("'", "")
        if not cleaned.isalpha():
            continue
        counts[key] = counts.get(key, 0) + 1
        if key not in canonical:
            canonical[key] = token
    return {canonical[key]: value for key, value in counts.items()}


def extract_structured_wiki_surnames(raw_html: str, min_length: int, max_length: int) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for surname in re.findall(r'title="([^"]+?)\s*\(apellido\)"', raw_html, flags=re.IGNORECASE):
        token = surname.strip()
        if len(token) < min_length or len(token) > max_length:
            continue
        if not token.replace("-", "").replace("'", "").isalpha():
            continue
        counts[token] = counts.get(token, 0) + 2
    return counts


def extract_structured_wiki_character_names(text: str, min_length: int, max_length: int, excluded_words: List[str]) -> Dict[str, int]:
    excluded = {word.strip().lower() for word in excluded_words if word.strip()}
    counts: Dict[str, int] = {}
    for match in re.finditer(r"\b\d+\.\d+\s+([A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚÑáéíóúñüÜ' -]{1,24})", text):
        token = match.group(1).strip()
        if len(token) < min_length or len(token) > max_length:
            continue
        if token.lower() in excluded:
            continue
        if token.count(" ") > 1:
            continue
        cleaned = token.replace(" ", "").replace("-", "").replace("'", "")
        if not cleaned.isalpha():
            continue
        counts[token] = counts.get(token, 0) + 2
    return counts


def extract_counts_from_sources(
    sources: List[str],
    max_length: int,
    min_frequency: int,
    min_length: int = 2,
    token_regex: str = r"\b[A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚÑáéíóúñüÜ'-]{1,}\b",
    excluded_words: Optional[List[str]] = None,
) -> List[Dict]:
    excluded_words = excluded_words or []
    aggregated: Dict[str, Dict] = {}
    for source in sources:
        if not source.startswith("http://") and not source.startswith("https://"):
            continue
        try:
            raw_html = fetch_html(source)
            text = normalize_html_to_text(raw_html)
        except Exception:
            continue

        if "wikipedia.org/wiki/Anexo:Apellidos" in source:
            source_candidates = extract_structured_wiki_surnames(raw_html, min_length, max_length)
        elif "wikipedia.org/wiki/Anexo:Personajes_de_Dragon_Ball" in source:
            source_candidates = extract_structured_wiki_character_names(text, min_length, max_length, excluded_words)
        else:
            source_candidates = extract_tokens(text, token_regex, min_length, max_length, excluded_words)

        source_candidates = {
            key: score for key, score in source_candidates.items() if score >= min_frequency
        }

        for value, count in source_candidates.items():
            if value not in aggregated:
                aggregated[value] = {
                    "value": value,
                    "score": count,
                    "sources": [source],
                    "evidence": first_evidence_snippet(text, value),
                }
            else:
                aggregated[value]["score"] += count
                if source not in aggregated[value]["sources"]:
                    aggregated[value]["sources"].append(source)

    ranked = sorted(
        aggregated.values(),
        key=lambda item: (-int(item["score"]), str(item["value"]).lower()),
    )
    return ranked


def extract_postal_candidates(sources: List[str], regex: str) -> List[Dict]:
    validation_pattern = re.compile(regex)
    extraction_regex = regex
    if extraction_regex.startswith("^") and extraction_regex.endswith("$"):
        extraction_regex = extraction_regex[1:-1]
    extraction_pattern = re.compile(rf"\b(?:{extraction_regex})\b")

    candidates: Dict[str, Dict] = {}
    for source in sources:
        if not source.startswith("http://") and not source.startswith("https://"):
            continue
        try:
            text = fetch_text(source)
        except Exception:
            continue
        for value in extraction_pattern.findall(text):
            if not validation_pattern.fullmatch(value):
                continue
            if value not in candidates:
                candidates[value] = {
                    "value": value,
                    "score": 1,
                    "sources": [source],
                    "evidence": first_evidence_snippet(text, value),
                }
            else:
                candidates[value]["score"] += 1
                if source not in candidates[value]["sources"]:
                    candidates[value]["sources"].append(source)

    ranked = sorted(
        candidates.values(),
        key=lambda item: (-int(item["score"]), str(item["value"])),
    )
    return ranked


def build_context(catalog: Dict, policy: Dict, case_name: str, limit: int) -> Dict:
    case = catalog.get(case_name)
    if not case:
        raise RuntimeError(f"No existe el caso '{case_name}' en el catalogo IA")

    variables = case.get("variables", {})
    validation = policy.get("validacion", {})
    resolution = policy.get("resolucion", {})

    nombre_sources = as_source_list(variables.get("nombre", {}))
    apellido_sources = as_source_list(variables.get("apellido", {}))
    codigo_sources = as_source_list(variables.get("codigoPostal", {}))

    nombre_max = int(validation.get("nombre", {}).get("maxLongitud", 15))
    apellido_max = int(validation.get("apellido", {}).get("maxLongitud", 15))
    codigo_regex = str(validation.get("codigoPostal", {}).get("regex", r"^11\d{4}$"))
    nombre_resolution = resolution.get("nombre", {})
    apellido_resolution = resolution.get("apellido", {})
    codigo_resolution = resolution.get("codigoPostal", {})
    nombre_sources = select_sources(nombre_sources, nombre_resolution, "nombre")
    apellido_sources = select_sources(apellido_sources, apellido_resolution, "apellido")
    codigo_sources = select_sources(codigo_sources, codigo_resolution, "codigoPostal")
    nombre_min_freq = int(resolution.get("nombre", {}).get("minFrecuencia", 1))
    apellido_min_freq = int(resolution.get("apellido", {}).get("minFrecuencia", 1))
    nombre_min_len = int(resolution.get("nombre", {}).get("minLongitud", 2))
    apellido_min_len = int(resolution.get("apellido", {}).get("minLongitud", 2))
    nombre_token_regex = str(
        resolution.get(
            "nombre", {}
        ).get("regexToken", r"\b[A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚÑáéíóúñüÜ'-]{1,}\b")
    )
    apellido_token_regex = str(
        resolution.get(
            "apellido", {}
        ).get("regexToken", r"\b[A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚÑáéíóúñüÜ'-]{1,}\b")
    )
    nombre_excluidas = [str(v) for v in resolution.get("nombre", {}).get("palabrasExcluidas", [])]
    apellido_excluidas = [str(v) for v in resolution.get("apellido", {}).get("palabrasExcluidas", [])]

    nombre_candidates = extract_counts_from_sources(
        nombre_sources,
        nombre_max,
        nombre_min_freq,
        min_length=nombre_min_len,
        token_regex=nombre_token_regex,
        excluded_words=nombre_excluidas,
    )[:limit]
    apellido_candidates = extract_counts_from_sources(
        apellido_sources,
        apellido_max,
        apellido_min_freq,
        min_length=apellido_min_len,
        token_regex=apellido_token_regex,
        excluded_words=apellido_excluidas,
    )[:limit]
    codigo_candidates = extract_postal_candidates(codigo_sources, codigo_regex)[:limit]

    return {
        "schema": "compra-ia-context/v1",
        "case": case_name,
        "fixed": case.get("fijos", {}),
        "rules": {
            "nombre": validation.get("nombre", {}),
            "apellido": validation.get("apellido", {}),
            "codigoPostal": validation.get("codigoPostal", {}),
            "descripcion": {
                "nombre": variables.get("nombre", {}).get("descripcion", ""),
                "apellido": variables.get("apellido", {}).get("descripcion", ""),
                "codigoPostal": variables.get("codigoPostal", {}).get("descripcion", ""),
            },
        },
        "candidates": {
            "nombre": nombre_candidates,
            "apellido": apellido_candidates,
            "codigoPostal": codigo_candidates,
        },
    }


def validate_resolved_values(policy: Dict, nombre: str, apellido: str, codigo_postal: str) -> None:
    validation = policy.get("validacion", {})
    nombre_max = int(validation.get("nombre", {}).get("maxLongitud", 15))
    apellido_max = int(validation.get("apellido", {}).get("maxLongitud", 15))
    codigo_regex = str(validation.get("codigoPostal", {}).get("regex", r"^11\d{4}$"))

    if not nombre or len(nombre.strip()) == 0:
        raise RuntimeError("nombre es requerido para ejecutar el test IA")
    if len(nombre.strip()) > nombre_max:
        raise RuntimeError(f"nombre excede maxLongitud={nombre_max}")

    if not apellido or len(apellido.strip()) == 0:
        raise RuntimeError("apellido es requerido para ejecutar el test IA")
    if len(apellido.strip()) > apellido_max:
        raise RuntimeError(f"apellido excede maxLongitud={apellido_max}")

    if not re.fullmatch(codigo_regex, codigo_postal.strip()):
        raise RuntimeError(f"codigoPostal no cumple regex {codigo_regex}")


def build_gradle_command(policy: Dict, resolved: Dict[str, ResolvedField]) -> List[str]:
    salida_props = policy.get("salidaProps", {})
    execution = policy.get("ejecucion", {})
    gradle_task = execution.get("gradleTask", "test")
    runner = execution.get("runner")
    tags = str(execution.get("tags", "")).strip()
    if not runner:
        raise RuntimeError("La politica MCP debe definir ejecucion.runner")

    command = ["./gradlew", gradle_task, "--tests", runner]
    if tags:
        command.append(f"-Dcucumber.filter.tags={tags}")
    for field_name, property_name in salida_props.items():
        if field_name not in resolved:
            raise RuntimeError(f"La salidaProps referencia un campo no resuelto: '{field_name}'")
        command.append(f"-D{property_name}={resolved[field_name].value}")
    return command


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def deterministic_sha256(payload: Dict) -> str:
    serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def build_ai_decision_id(case_name: str) -> str:
    return f"{case_name}-{uuid.uuid4()}"


def persist_trace(
    trace_path: Path,
    case_name: str,
    resolved: Dict[str, ResolvedField],
    decision_mode: str,
    audit: Optional[Dict] = None,
) -> None:
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    trace_payload = {
        "caso": case_name,
        "decisionMode": decision_mode,
        "traceCreatedAtUtc": utc_now_iso(),
        "audit": audit or {},
        "resuelto": {
            key: {
                "valor": data.value,
                "fuente": data.source,
                "evidencia": data.evidence,
            }
            for key, data in resolved.items()
        },
    }
    with trace_path.open("w", encoding="utf-8") as handle:
        json.dump(trace_payload, handle, ensure_ascii=False, indent=2)


def print_resolution(resolved: Dict[str, ResolvedField], command: List[str]) -> None:
    print("Valores resueltos por IA:")
    for field_name, info in resolved.items():
        print(f"  - {field_name}: {info.value}")
        print(f"    fuente: {info.source}")
    print("\nComando de ejecucion:")
    print(" ".join(command))


def command_collect(args: argparse.Namespace) -> int:
    catalog = load_json(Path(args.catalog))
    policy = load_json(Path(args.policy))
    context = build_context(catalog, policy, args.case, args.limit)
    context_hash = deterministic_sha256(context)
    output = {
        **context,
        "candidatePoolHash": context_hash,
        "collectedAtUtc": utc_now_iso(),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


def command_execute(args: argparse.Namespace) -> int:
    policy = load_json(Path(args.policy))
    validate_resolved_values(policy, args.nombre, args.apellido, args.codigo_postal)

    resolved = {
        "nombre": ResolvedField(args.nombre.strip(), args.nombre_source or "ia-decision", args.nombre_evidence or args.nombre),
        "apellido": ResolvedField(args.apellido.strip(), args.apellido_source or "ia-decision", args.apellido_evidence or args.apellido),
        "codigoPostal": ResolvedField(
            args.codigo_postal.strip(),
            args.codigo_postal_source or "ia-decision",
            args.codigo_postal_evidence or args.codigo_postal,
        ),
    }

    trace_output = policy.get("trazabilidad", {}).get("guardarArchivo")
    audit = {
        "aiDecisionId": (args.ai_decision_id or build_ai_decision_id(args.case)).strip(),
        "decisionReasoning": (args.decision_reasoning or "").strip(),
        "candidatePoolHash": (args.candidate_pool_hash or "").strip(),
        "catalogPath": args.catalog,
        "policyPath": args.policy,
        "executedAtUtc": utc_now_iso(),
    }
    if trace_output:
        persist_trace(Path(trace_output), args.case, resolved, "ai", audit)

    command = build_gradle_command(policy, resolved)
    print_resolution(resolved, command)
    if args.dry_run:
        return 0

    completed = subprocess.run(command)
    return completed.returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="MCP local: recolecta contexto y ejecuta test IA con valores decididos por IA"
    )
    parser.add_argument("--case", default="compra-saucedemo", help="Caso del catalogo IA")
    parser.add_argument(
        "--catalog",
        default="src/test/resources/catalog-ia/catalog-ia.json",
        help="Ruta al catalogo IA",
    )
    parser.add_argument(
        "--policy",
        default="src/test/resources/catalog-ia/mcp-policy.json",
        help="Ruta a la politica MCP",
    )

    subparsers = parser.add_subparsers(dest="command")

    collect_parser = subparsers.add_parser("collect", help="Recolecta candidatos desde fuentes para decision IA")
    collect_parser.add_argument("--limit", type=int, default=12, help="Maximo de candidatos por campo")

    execute_parser = subparsers.add_parser("execute", help="Ejecuta test IA con valores ya decididos")
    execute_parser.add_argument("--nombre", required=True, help="Valor final para dataia.nombre")
    execute_parser.add_argument("--apellido", required=True, help="Valor final para dataia.apellido")
    execute_parser.add_argument("--codigo-postal", required=True, dest="codigo_postal", help="Valor final para dataia.codigoPostal")
    execute_parser.add_argument("--nombre-source", default="ia-decision", dest="nombre_source", help="Fuente de decision para nombre")
    execute_parser.add_argument("--apellido-source", default="ia-decision", dest="apellido_source", help="Fuente de decision para apellido")
    execute_parser.add_argument(
        "--codigo-postal-source",
        default="ia-decision",
        dest="codigo_postal_source",
        help="Fuente de decision para codigo postal",
    )
    execute_parser.add_argument("--nombre-evidence", default="", dest="nombre_evidence", help="Evidencia de decision para nombre")
    execute_parser.add_argument("--apellido-evidence", default="", dest="apellido_evidence", help="Evidencia de decision para apellido")
    execute_parser.add_argument(
        "--codigo-postal-evidence",
        default="",
        dest="codigo_postal_evidence",
        help="Evidencia de decision para codigo postal",
    )
    execute_parser.add_argument(
        "--ai-decision-id",
        default="",
        dest="ai_decision_id",
        help="Identificador unico de la decision IA (auditoria)",
    )
    execute_parser.add_argument(
        "--decision-reasoning",
        default="",
        dest="decision_reasoning",
        help="Razon breve de seleccion por IA (auditoria)",
    )
    execute_parser.add_argument(
        "--candidate-pool-hash",
        default="",
        dest="candidate_pool_hash",
        help="Hash del contexto generado por collect (auditoria)",
    )
    execute_parser.add_argument("--dry-run", action="store_true", help="Solo imprime comando, no ejecuta Gradle")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 2

    if args.command == "collect":
        return command_collect(args)
    if args.command == "execute":
        return command_execute(args)

    raise RuntimeError(f"Comando no soportado: {args.command}")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
