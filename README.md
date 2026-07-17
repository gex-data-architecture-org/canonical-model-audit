# canonical-model-audit

Auditoria do modelo canônico da equipe de Dados GEX.

## Estrutura

```
/
├── README.md                           # este arquivo
├── AGENTS.md                           # Codex CLI (OpenAI)
├── CLAUDE.md                           # Claude Code (Anthropic)
├── GEMINI.md                           # Gemini CLI (Google)
├── .cursor/rules/                      # Cursor IDE
├── .github/copilot-instructions.md     # GitHub Copilot
├── docs/                               # Documentação e artefatos da auditoria
├── reports/                            # Relatórios gerados
├── scripts/                            # Scripts de extração, validação e análise
└── skills/
    └── dors-loopcraft/
        ├── content.md                  # 🔷 CANONICAL — fonte única da verdade
        ├── SKILL.md                    # Hermes Agent (YAML frontmatter + conteúdo)
        ├── build.sh                    # Regenera todos os wrappers abaixo
        ├── references/                 # Referências compartilhadas
        ├── scripts/                    # Scripts auxiliares
        └── templates/                  # Templates
```

## Modelo Agnóstico de Skills

Cada skill tem uma **fonte canônica única** em `content.md` (markdown puro, sem metadados proprietários). Os wrappers para cada agente são **gerados** a partir dela:

| Agente | Arquivo | Formato |
|--------|---------|---------|
| **Hermes Agent** | `skills/<name>/SKILL.md` | YAML frontmatter + markdown |
| **Claude Code** | `CLAUDE.md` (raiz) | Markdown puro |
| **Codex CLI** | `AGENTS.md` (raiz) | Markdown puro |
| **Gemini CLI** | `GEMINI.md` (raiz) | Markdown puro |
| **Cursor** | `.cursor/rules/<name>.mdc` | Markdown puro |
| **GitHub Copilot** | `.github/copilot-instructions.md` | Markdown puro |

### Fluxo de edição

1. **Edite** apenas o arquivo canônico: `skills/<name>/content.md`
2. **Regenere** os wrappers: `bash skills/<name>/build.sh`
3. **Commite** tudo junto

Nunca edite os wrappers diretamente — eles são sobrescritos pelo build.

## Escopo da Auditoria

- Mapeamento das entidades do modelo canônico atual
- Validação de conformidade entre fontes e modelo
- Identificação de gaps, redundâncias e inconsistências
- Recomendações de evolução

---

**GEX Data Architecture** · `gex-data-architecture-org`
