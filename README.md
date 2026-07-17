# canonical-model-audit

Auditoria do modelo canônico da equipe de Dados GEX.

## Estrutura

```
/
├── skills/                      🔷 CANONICAL — Agent Skills open standard
│   └── dors-loopcraft/
│       ├── SKILL.md             # YAML frontmatter + markdown (fonte única)
│       ├── build.sh             # Sync para todas as plataformas
│       ├── references/          # Material de referência
│       ├── scripts/             # Scripts auxiliares
│       └── templates/           # Templates
│
├── .claude/skills/              ← Claude Code (cópia gerada)
├── .gemini/skills/              ← Gemini CLI (cópia gerada)
├── CLAUDE.md                    ← Claude Code project context
├── AGENTS.md                    ← Codex CLI project context
├── GEMINI.md                    ← Gemini CLI project context
├── .cursor/rules/               ← Cursor IDE
├── .github/copilot-instructions.md  ← GitHub Copilot
│
├── docs/                        # Documentação da auditoria
├── reports/                     # Relatórios gerados
└── scripts/                     # Scripts ETL/análise
```

## Modelo Agnóstico de Skills

Seguimos o padrão **[Agent Skills](https://agentskills.io)** — spec aberta criada pela Anthropic e adotada por múltiplos agentes.

### Como funciona

| Plataforma | Onde a skill vive | Como carrega |
|------------|-------------------|--------------|
| **Hermes Agent** | `skills/<name>/` | Auto-discovery do diretório `skills/` |
| **Claude Code** | `.claude/skills/<name>/` | `/dors-loopcraft` ou auto-load |
| **Gemini CLI** | `.gemini/skills/<name>/` | Auto-discovery |
| **Codex CLI** | `AGENTS.md` (raiz) | Project context |
| **Cursor** | `.cursor/rules/<name>.mdc` | Project rules |
| **GitHub Copilot** | `.github/copilot-instructions.md` | Project instructions |

### Formato canônico (Agent Skills spec)

```yaml
---
name: nome-da-skill        # required: lowercase, hyphens, max 64
description: "..."         # required: what + when to use, max 1024
license: MIT               # optional
compatibility: "..."       # optional: environment requirements
metadata:                  # optional: arbitrary key-value
  version: "1.0"
  author: "..."
---

# Corpo em markdown
...
```

### Fluxo de edição

1. **Edite** apenas `skills/<name>/SKILL.md`
2. **Rode** `bash skills/<name>/build.sh`
3. **Commite** as cópias geradas (`.claude/`, `.gemini/`, wrappers raiz)

> Nunca edite `.claude/skills/` ou `.gemini/skills/` diretamente — são cópias do canônico.

## Escopo da Auditoria

- Mapeamento das entidades do modelo canônico atual
- Validação de conformidade entre fontes e modelo
- Identificação de gaps, redundâncias e inconsistências
- Recomendações de evolução

---

**GEX Data Architecture** · `gex-data-architecture-org`
