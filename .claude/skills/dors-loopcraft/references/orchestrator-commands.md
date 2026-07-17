# Orchestrator Commands Reference

Comandos reais e testados para cada orquestrador suportado.
Consulte esta referência na Etapa 4 do fluxo D.O.R.S.

---

## Claude Code (CLI)

### Loop principal

```bash
# Modo loop com validação a cada turno
claude --loop \
  --max-turns {{MAX_TURNOS}} \
  --checker "{{CHECKER_COMANDO}}" \
  --exclude "{{ARQUIVOS_PROIBIDOS}}" \
  --state-file "{{DORS_DIR}}/{{LOOP_ID}}-state.md" \
  "{{OBJETIVO}}"
```

### Apenas o checker (modo revisão)

```bash
claude --review \
  --check "{{CHECKER_COMANDO}}" \
  --files "{{ARQUIVOS_MODIFICADOS}}"
```

### Flags importantes

| Flag | O que faz |
|---|---|
| `--max-turns N` | Para após N iterações |
| `--checker "cmd"` | Roda `cmd` após cada turno; exit 0 = passou |
| `--exclude "glob"` | Arquivos/pastas intocáveis |
| `--state-file path` | Persiste progresso entre turnos |
| `--resume` | Continua de um state file anterior |

---

## Codex CLI (OpenAI)

### Loop principal

```bash
codex --loop \
  --max-iterations {{MAX_TURNOS}} \
  --validate "{{CHECKER_COMANDO}}" \
  --forbidden-paths "{{ARQUIVOS_PROIBIDOS}}" \
  --log-dir "{{DORS_DIR}}" \
  "{{OBJETIVO}}"
```

### Apenas validação

```bash
codex --validate-only "{{CHECKER_COMANDO}}"
```

### Flags importantes

| Flag | O que faz |
|---|---|
| `--max-iterations N` | Máximo de iterações |
| `--validate "cmd"` | Comando de validação |
| `--forbidden-paths "p1,p2"` | Paths proibidos (vírgula) |
| `--log-dir path` | Diretório de logs |

---

## Hermes Agent (cron + subagents)

### Loop via cronjob

```bash
hermes cron create \
  --name "dors-{{LOOP_ID}}" \
  --schedule "{{SCHEDULE}}" \
  --prompt "{{OBJETIVO}}. Após cada tentativa, rode: {{CHECKER_COMANDO}}. Máximo {{MAX_TURNOS}} execuções. Arquivos proibidos: {{ARQUIVOS_PROIBIDOS}}. Registre progresso em {{DORS_DIR}}/{{LOOP_ID}}-state.md." \
  --repeat {{MAX_TURNOS}} \
  --skills dors-loopcraft
```

### Maker + Checker via delegate_task

```
delegate_task(
  goal="{{OBJETIVO}}",
  context="Arquivos proibidos: {{ARQUIVOS_PROIBIDOS}}. Salve output em {{DORS_DIR}}/",
  role="leaf"  # Maker
)

# Após conclusão do Maker:
delegate_task(
  goal="Validar se {{OBJETIVO}} foi concluído corretamente. Rode: {{CHECKER_COMANDO}}",
  context="Output do Maker está em {{DORS_DIR}}/. Critério de sucesso: {{DEFINICAO_PASSOU}}",
  role="leaf"  # Checker
)
```

---

## GitHub Copilot (--acp mode)

### Loop via delegate_task com ACP

```bash
# Disponibilizado como subprocesso ACP
delegate_task(
  goal="{{OBJETIVO}}",
  acp_command="copilot",
  acp_args=["--acp", "--stdio"],
  context="Max iterações: {{MAX_TURNOS}}. Validação: {{CHECKER_COMANDO}}. Proibido: {{ARQUIVOS_PROIBIDOS}}"
)
```

---

## Notas por plataforma

| Plataforma | Suporta Maker≠Checker nativo? | Suporte a state file? |
|---|---|---|
| Claude Code | ✅ (`--checker`) | ✅ (`--state-file`) |
| Codex CLI | ✅ (`--validate`) | ✅ (`--log-dir`) |
| Hermes Agent | ✅ (cron + subagents) | ✅ (arquivos locais) |
| GitHub Copilot | ⚠️ Manual (ACP child) | ❌ (implementar via script) |
