#!/usr/bin/env python3
"""
D.O.R.S. Context Loader — Carrega histórico de loops do projeto.

Uso:
    python context-loader.py --project-dir /caminho/projeto
    python context-loader.py --project-dir /caminho/projeto --format markdown
    python context-loader.py --project-dir /caminho/projeto --format json

Output padrão: bloco markdown pronto para injeção em prompt.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


def find_dors_dir(project_dir: Path) -> Path | None:
    """Encontra a pasta dors-loops/ ou .dors/ no projeto."""
    for candidate in ["dors-loops", ".dors"]:
        path = project_dir / candidate
        if path.is_dir():
            return path
    return None


def load_registry(dors_dir: Path) -> dict | None:
    """Carrega o .dors-registry.json."""
    registry_path = dors_dir / ".dors-registry.json"
    if registry_path.exists():
        try:
            return json.loads(registry_path.read_text())
        except json.JSONDecodeError:
            return None
    return None


def load_specs(dors_dir: Path) -> list[dict]:
    """Carrega todos os specs da pasta, ordenados por data."""
    specs = []
    for item in sorted(dors_dir.iterdir()):
        if item.is_dir():
            spec_file = item / "spec.md"
            final_file = item / "final.md"
            if spec_file.exists():
                spec_data = {
                    "id": item.name,
                    "spec_path": str(spec_file),
                    "spec_content": spec_file.read_text()[:3000],
                    "final_content": final_file.read_text() if final_file.exists() else None,
                    "loop_dir": str(item),
                }
                specs.append(spec_data)
    return specs


def extract_lessons(specs: list[dict]) -> list[str]:
    """Extrai lições dos specs anteriores."""
    lessons = []
    for spec in specs:
        content = spec["spec_content"]
        # Extrai seção "Contexto de Loops Anteriores" ou "Lições"
        for line in content.split("\n"):
            line_stripped = line.strip()
            if line_stripped.startswith("- ") and any(
                kw in line_stripped.lower()
                for kw in ["falhou", "timeout", "thrashing", "erro", "ajustar", "aprendido", "lição"]
            ):
                lessons.append(f"[{spec['id']}] {line_stripped}")
    return lessons


def extract_patterns(specs: list[dict]) -> dict:
    """Extrai padrões recorrentes: verificadores usados, arquivos proibidos, etc."""
    checkers = []
    forbidden = []
    max_turns = []

    for spec in specs:
        content = spec["spec_content"]
        for line in content.split("\n"):
            ls = line.strip()
            if ls.startswith("```") and not checkers:
                # Pega primeiro bloco de código como possível checker
                pass
            if "pytest" in ls or "npm test" in ls or "cargo test" in ls or "go test" in ls:
                if ls not in checkers:
                    checkers.append(ls)
            if ls.startswith("- ") and any(
                ext in ls for ext in [".env", ".key", "migrations", "prod", "secrets"]
            ):
                if ls not in forbidden:
                    forbidden.append(ls)

    # Extrai max_turns
    for spec in specs:
        for line in spec["spec_content"].split("\n"):
            if "Máximo de tentativas" in line or "max_turns" in line.lower():
                try:
                    num = int("".join(c for c in line if c.isdigit()))
                    max_turns.append(num)
                except ValueError:
                    pass

    return {
        "preferred_verifiers": list(set(checkers))[:5],
        "recurring_forbidden": list(set(forbidden))[:5],
        "avg_max_turns": sum(max_turns) // len(max_turns) if max_turns else None,
    }


def generate_context(specs: list[dict], patterns: dict, lessons: list[str]) -> str:
    """Gera bloco de contexto para injeção no prompt."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        f"## Contexto de Loops Anteriores (carregado em {now})",
        "",
        f"**Total de loops no projeto:** {len(specs)}",
        "",
    ]

    if specs:
        lines.append("### Histórico recente")
        lines.append("")
        for spec in specs[-3:]:  # Últimos 3
            status_icon = "✅" if "final" in str(spec.get("final_content", "")) else "⏳"
            lines.append(f"- {status_icon} **{spec['id']}**")

            # Tenta extrair o objetivo (primeira linha após "Objetivo e Gatilho")
            content = spec["spec_content"]
            in_objective = False
            for line in content.split("\n"):
                if "Objetivo e Gatilho" in line:
                    in_objective = True
                    continue
                if in_objective and line.strip().startswith("**") and not line.strip().startswith("**O que"):
                    lines.append(f"  - Objetivo: {line.strip()}")
                    break
                if in_objective and line.strip().startswith("##"):
                    break

        lines.append("")

    if lessons:
        lines.append("### Lições aprendidas")
        lines.append("")
        for lesson in lessons[-5:]:
            lines.append(lesson)
        lines.append("")

    if patterns:
        lines.append("### Padrões do projeto")
        lines.append("")
        if patterns["preferred_verifiers"]:
            lines.append("**Verificadores usados anteriormente:**")
            for v in patterns["preferred_verifiers"]:
                lines.append(f"- `{v}`")
            lines.append("")
        if patterns["recurring_forbidden"]:
            lines.append("**Arquivos frequentemente proibidos:**")
            for f in patterns["recurring_forbidden"]:
                lines.append(f)
            lines.append("")
        if patterns["avg_max_turns"]:
            lines.append(f"**Média de turnos por loop:** {patterns['avg_max_turns']}")
            lines.append("")

    if not specs:
        lines.append("📝 *Este é o primeiro loop do projeto. Nenhum contexto anterior disponível.*")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="D.O.R.S. Context Loader")
    parser.add_argument("--project-dir", required=True, help="Diretório raiz do projeto")
    parser.add_argument(
        "--format", choices=["markdown", "json"], default="markdown", help="Formato de saída"
    )
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    if not project_dir.is_dir():
        print(f"Erro: diretório não encontrado: {project_dir}", file=sys.stderr)
        sys.exit(1)

    dors_dir = find_dors_dir(project_dir)

    if not dors_dir:
        if args.format == "json":
            print(json.dumps({"loops": [], "message": "Nenhum loop anterior encontrado"}))
        else:
            print("📝 *Este é o primeiro loop do projeto. Nenhum contexto anterior disponível.*")
        return

    specs = load_specs(dors_dir)
    lessons = extract_lessons(specs)
    patterns = extract_patterns(specs)

    if args.format == "json":
        output = {
            "loops_count": len(specs),
            "lessons": lessons,
            "patterns": patterns,
            "latest_specs": [
                {"id": s["id"], "spec": s["spec_content"][:500]} for s in specs[-3:]
            ],
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print(generate_context(specs, patterns, lessons))


if __name__ == "__main__":
    main()
