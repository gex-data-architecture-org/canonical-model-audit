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
│   ├── parecer-correcoes-auditoria-davi.md
│   ├── parecer-implementacao-assinaturas-canonico.md
│   └── tasks-clickup-canonico-buygoods.md
│
├── reports/                     # Relatórios gerados
└── scripts/                     # Scripts ETL/análise
```

## Documentos da Auditoria

| Documento | Conteúdo |
|-----------|----------|
| `parecer-correcoes-auditoria-davi.md` | Correções aplicadas pós-auditoria: 12 itens corrigidos e validados em produção, 3 caracterizados como comportamento esperado, 3 decisões de negócio resolvidas |
| `parecer-implementacao-assinaturas-canonico.md` | Implementação de assinaturas no modelo canônico: 7 entregas (`fct_cobrancas`, `fct_assinaturas`, nova chave de funil, etc.), +US$ 38,4k de receita recuperada |
| `tasks-clickup-canonico-buygoods.md` | Tasks ClickUp: 7 para atuar agora, 4 impedimentos (aguardando BuyGoods), 2 ações de desbloqueio |

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

### Fluxo de edição

1. **Edite** apenas `skills/<name>/SKILL.md`
2. **Rode** `bash skills/<name>/build.sh`
3. **Commite** as cópias geradas (`.claude/`, `.gemini/`, wrappers raiz)

## Escopo da Auditoria

- Mapeamento das entidades do modelo canônico atual
- Validação de conformidade entre fontes e modelo
- Identificação de gaps, redundâncias e inconsistências
- Recomendações de evolução

---

**GEX Data Architecture** · `gex-data-architecture-org`
