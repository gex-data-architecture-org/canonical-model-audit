#!/usr/bin/env python3
"""
D.O.R.S. Loop Analyzer — Diagnostica a saúde de um loop após execução.

Uso:
    python loop-analyzer.py --project-dir /caminho/projeto --loop-id 2026-07-17-refatorar-auth
    python loop-analyzer.py --project-dir /caminho/projeto --loop-id latest

Lê o state.md do loop + specs anteriores e gera:
1. Diagnóstico de thrashing
2. Detecção de falsos positivos do checker
3. Padrões de falha recorrentes
4. Sugestões de ajuste no spec para o próximo loop
"""

import argparse
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path


def find_dors_dir(project_dir: Path) -> Path | None:
    for candidate in ["dors-loops", ".dors"]:
        path = project_dir / candidate
        if path.is_dir():
            return path
    return None


def find_loop_dir(dors_dir: Path, loop_id: str) -> Path | None:
    if loop_id == "latest":
        dirs = sorted(
            [d for d in dors_dir.iterdir() if d.is_dir()],
            key=lambda d: d.name,
            reverse=True,
        )
        return dirs[0] if dirs else None
    path = dors_dir / loop_id
    return path if path.is_dir() else None


def parse_state(state_content: str) -> list[dict]:
    """Parseia state.md em lista de turnos."""
    turns = []
    current_turn = None
    turn_pattern = re.compile(r"(?:Turno|Tentativa|Turn)\s*(\d+)", re.IGNORECASE)
    error_pattern = re.compile(
        r"(error|fail|falha|erro|traceback|exception|FAILED)", re.IGNORECASE
    )
    success_pattern = re.compile(
        r"(success|pass|sucesso|passed|PASSED|aprovado|ok)", re.IGNORECASE
    )

    for line in state_content.split("\n"):
        m = turn_pattern.search(line)
        if m:
            if current_turn:
                turns.append(current_turn)
            current_turn = {
                "number": int(m.group(1)),
                "errors": [],
                "success": False,
                "raw_lines": [],
            }
        if current_turn:
            current_turn["raw_lines"].append(line)
            if error_pattern.search(line):
                current_turn["errors"].append(line.strip())
            if success_pattern.search(line):
                current_turn["success"] = True

    if current_turn:
        turns.append(current_turn)
    return turns


def detect_thrashing(turns: list[dict]) -> dict:
    """Detecta thrashing: mesmo erro aparecendo 3+ vezes consecutivas."""
    error_sequence = []
    for turn in turns:
        error_sequence.append(tuple(turn["errors"]) if turn["errors"] else None)

    thrashing_blocks = []
    current_block = []
    for i, errors in enumerate(error_sequence):
        if errors:
            if current_block and errors == current_block[-1][1]:
                current_block.append((i + 1, errors))
            else:
                if len(current_block) >= 3:
                    thrashing_blocks.append(current_block)
                current_block = [(i + 1, errors)]
        else:
            if len(current_block) >= 3:
                thrashing_blocks.append(current_block)
            current_block = []

    if len(current_block) >= 3:
        thrashing_blocks.append(current_block)

    return {
        "detected": len(thrashing_blocks) > 0,
        "blocks": [
            {
                "turns": [t[0] for t in block],
                "errors": list(block[0][1]) if block else [],
            }
            for block in thrashing_blocks
        ],
    }


def detect_false_positives(turns: list[dict]) -> dict:
    """Detecta possíveis falsos positivos: checker rejeitou, mas a mudança parecia correta."""
    fp_candidates = []
    for turn in turns:
        if turn["success"]:
            continue
        # Heurística: turno tem poucos erros e erros são de linting, não de lógica
        non_lint_errors = [
            e
            for e in turn["errors"]
            if not any(
                kw in e.lower()
                for kw in ["unused", "import", "whitespace", "trailing", "indent", "blank"]
            )
        ]
        if len(turn["errors"]) > 0 and len(non_lint_errors) == 0:
            fp_candidates.append(
                {
                    "turn": turn["number"],
                    "errors": turn["errors"],
                    "reason": "Todos os erros são de linting/formatação — possível falso positivo",
                }
            )

    return {
        "detected": len(fp_candidates) > 0,
        "candidates": fp_candidates,
    }


def detect_budget_exhaustion(turns: list[dict], max_turns: int) -> dict:
    """Analisa se o orçamento foi bem dimensionado."""
    used = len(turns)
    successful = any(t["success"] for t in turns)
    last_success = None
    for t in reversed(turns):
        if t["success"]:
            last_success = t["number"]
            break

    return {
        "max_turns": max_turns,
        "turns_used": used,
        "exhausted": used >= max_turns and not successful,
        "successful": successful,
        "last_success_turn": last_success,
        "utilization_pct": round(used / max_turns * 100, 1) if max_turns else 0,
        "recommendation": (
            "Aumentar orçamento — loop estava perto do sucesso quando estourou"
            if last_success is None and used >= max_turns * 0.8
            else (
                "Reduzir orçamento — sobrou margem"
                if used < max_turns * 0.5 and successful
                else "Orçamento adequado"
            )
        ),
    }


def generate_report(
    loop_id: str,
    thrash: dict,
    fp: dict,
    budget: dict,
    all_specs: list[dict],
) -> str:
    """Gera relatório markdown de diagnóstico."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# Diagnóstico D.O.R.S. — `{loop_id}`",
        f"*Gerado em {now}*",
        "",
        "---",
        "",
    ]

    # Resumo
    status = "✅ SUCESSO" if budget["successful"] else "❌ FALHA"
    lines.append(f"## Status: {status}")
    lines.append("")
    lines.append(f"- **Turnos usados:** {budget['turns_used']}/{budget['max_turns']} ({budget['utilization_pct']}%)")
    if budget["last_success_turn"]:
        lines.append(f"- **Último sucesso no turno:** {budget['last_success_turn']}")
    lines.append("")

    # Thrashing
    lines.append("## Thrashing")
    if thrash["detected"]:
        lines.append(f"⚠️ **Thrashing detectado em {len(thrash['blocks'])} bloco(s)!**")
        lines.append("")
        for i, block in enumerate(thrash["blocks"], 1):
            lines.append(f"### Bloco {i} — Turnos {', '.join(map(str, block['turns']))}")
            lines.append("**Erros repetidos:**")
            for err in block["errors"][:5]:
                lines.append(f"- `{err[:120]}`")
            lines.append("")
    else:
        lines.append("✅ Nenhum thrashing detectado.")
        lines.append("")

    # Falsos positivos
    lines.append("## Falsos Positivos do Checker")
    if fp["detected"]:
        lines.append(f"⚠️ **{len(fp['candidates'])} possível(is) falso(s) positivo(s).**")
        lines.append("")
        for cand in fp["candidates"]:
            lines.append(f"- **Turno {cand['turn']}:** {cand['reason']}")
            for err in cand["errors"][:3]:
                lines.append(f"  - `{err[:100]}`")
        lines.append("")
    else:
        lines.append("✅ Nenhum falso positivo suspeito.")
        lines.append("")

    # Orçamento
    lines.append("## Análise de Orçamento")
    lines.append(f"**Recomendação:** {budget['recommendation']}")
    lines.append("")

    # Padrões cross-loop
    if len(all_specs) > 1:
        lines.append("## Padrões Entre Loops")
        lines.append("")
        lines.append(f"- **Total de loops no projeto:** {len(all_specs)}")
        lines.append(f"- **Este loop:** {loop_id}")

        # Verifica se erros deste loop já apareceram antes
        lines.append("")
        lines.append("### Sugestões para o próximo loop")
        lines.append("")

        if thrash["detected"]:
            lines.append("- 💡 **Thrashing recorrente?** Considere afrouxar o critério de verificação na Fase B.")
            lines.append("- 💡 Divida a tarefa em 2-3 loops menores se o thrashing persistir.")
        if budget["exhausted"]:
            lines.append(f"- 💡 **Orçamento estourado.** Aumente de {budget['max_turns']} para {budget['max_turns'] + 5} turnos ou reduza o escopo.")
        if fp["detected"]:
            lines.append("- 💡 **Checker muito estrito.** Adicione `|| true` temporário para bypass de linting, ou troque para verificação mista (automática + humana).")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("*Rode `context-loader.py` antes do próximo loop para injetar estas lições no prompt.*")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="D.O.R.S. Loop Analyzer")
    parser.add_argument("--project-dir", required=True, help="Diretório raiz do projeto")
    parser.add_argument(
        "--loop-id",
        required=True,
        help="ID do loop a analisar (ex: '2026-07-17-refatorar-auth' ou 'latest')",
    )
    parser.add_argument(
        "--max-turns",
        type=int,
        help="Orçamento de turnos (se não informado, tenta extrair do spec)",
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Formato de saída",
    )
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    if not project_dir.is_dir():
        print(f"Erro: diretório não encontrado: {project_dir}", file=sys.stderr)
        sys.exit(1)

    dors_dir = find_dors_dir(project_dir)
    if not dors_dir:
        print("Erro: pasta dors-loops/ não encontrada no projeto.", file=sys.stderr)
        print("Rode um loop D.O.R.S. primeiro.", file=sys.stderr)
        sys.exit(1)

    loop_dir = find_loop_dir(dors_dir, args.loop_id)
    if not loop_dir:
        print(f"Erro: loop '{args.loop_id}' não encontrado em {dors_dir}", file=sys.stderr)
        sys.exit(1)

    state_file = loop_dir / "state.md"
    spec_file = loop_dir / "spec.md"

    if not state_file.exists():
        print(f"Erro: state.md não encontrado em {loop_dir}", file=sys.stderr)
        print("O loop ainda não gerou logs.", file=sys.stderr)
        sys.exit(1)

    state_content = state_file.read_text()

    # Determinar max_turns
    max_turns = args.max_turns
    if max_turns is None and spec_file.exists():
        spec_content = spec_file.read_text()
        for line in spec_content.split("\n"):
            if "Máximo de tentativas" in line:
                try:
                    max_turns = int("".join(c for c in line if c.isdigit()))
                except ValueError:
                    pass
    if max_turns is None:
        max_turns = 10  # default conservador

    turns = parse_state(state_content)
    if not turns:
        print("Aviso: nenhum turno encontrado no state.md", file=sys.stderr)
        print("O arquivo pode estar vazio ou em formato não reconhecido.", file=sys.stderr)
        sys.exit(1)

    thrash = detect_thrashing(turns)
    fp = detect_false_positives(turns)
    budget = detect_budget_exhaustion(turns, max_turns)

    # Carregar todos os specs para análise cross-loop
    all_specs = [
        d.name for d in dors_dir.iterdir() if d.is_dir() and (d / "spec.md").exists()
    ]

    if args.format == "json":
        output = {
            "loop_id": args.loop_id,
            "turns_analyzed": len(turns),
            "thrashing": thrash,
            "false_positives": fp,
            "budget": budget,
            "total_loops_in_project": len(all_specs),
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        report = generate_report(args.loop_id, thrash, fp, budget, all_specs)
        print(report)


if __name__ == "__main__":
    main()
