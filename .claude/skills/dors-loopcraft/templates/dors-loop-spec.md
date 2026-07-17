# Contrato Operacional de Loop — D.O.R.S.

> **Loop ID:** `{{LOOP_ID}}`
> **Data de criação:** `{{DATA}}`
> **Orquestrador alvo:** `{{ORQUESTRADOR}}`
> **Projeto:** `{{PROJETO}}`

---

## 1. Objetivo e Gatilho

**O que este loop deve alcançar:**

{{OBJETIVO}}

**O que dispara cada iteração:**

{{GATILHO}}

**Critério de parada por sucesso:**

{{CRITERIO_SUCESSO}}

---

## 2. Verificação de Sucesso

**Tipo:** {{TIPO_VERIFICACAO}} *(Determinística / Testes / Visual / Mista)*

**Comando de verificação:**

```bash
{{COMANDO_VERIFICACAO}}
```

**O que significa "passou":**

{{DEFINICAO_PASSOU}}

---

## 3. Guardrails

### Orçamento

| Parâmetro | Valor |
|---|---|
| Máximo de tentativas (turnos) | {{MAX_TURNOS}} |
| Timeout por tentativa | {{TIMEOUT}} |
| Estratégia ao estourar orçamento | {{ESTRATEGIA_FALHA}} |

### Arquivos e pastas PROIBIDOS

```
{{ARQUIVOS_PROIBIDOS}}
```

### Paradas de emergência

O loop deve ABORTAR IMEDIATAMENTE se:

- {{EMERGENCIA_1}}
- {{EMERGENCIA_2}}
- Thrashing detectado: mesmo erro 3x consecutivas → parar e reportar

---

## 4. Arquitetura Maker vs Checker

```
┌──────────────┐     ┌──────────────┐
│   MAKER      │────▶│   CHECKER    │
│ (agente que  │     │ (agente que  │
│  modifica)   │◀────│  valida)     │
└──────────────┘     └──────────────┘
   erro → retry         ok → avança
```

**Maker (quem faz):**
- Agente: {{MAKER_AGENTE}}
- Responsabilidade: modificar código, gerar arquivos, executar mudanças

**Checker (quem revisa):**
- Agente: {{CHECKER_AGENTE}} *(DEVE ser diferente do Maker)*
- Responsabilidade: rodar verificação, validar saída, aprovar/rejeitar
- Comando: {{CHECKER_COMANDO}}

---

## 5. Memória no Disco

**Pasta de memória do projeto:** `{{DORS_DIR}}`

**Pasta deste loop:** `{{DORS_DIR}}/{{LOOP_ID}}/`

**Arquivos gerados por este loop:**

| Arquivo | Conteúdo |
|---|---|
| `{{DORS_DIR}}/{{LOOP_ID}}/spec.md` | Este contrato |
| `{{DORS_DIR}}/{{LOOP_ID}}/state.md` | Log de cada tentativa (turno, ação, resultado) |
| `{{DORS_DIR}}/{{LOOP_ID}}/final.md` | Sumário pós-loop (sucesso/falha, lições) |
| `{{DORS_DIR}}/.dors-registry.json` | Índice dos loops do projeto para carregar contexto no próximo loop |

---

## 6. Contexto de Loops Anteriores

{{CONTEXTO_ANTERIOR}}

---

## 7. Comandos Prontos (Plug-and-Play)

### Para rodar HOJE

{{COMANDO_PRINCIPAL}}

### Para analisar AMANHÃ

```bash
python {{DORS_DIR}}/scripts/loop-analyzer.py \
  --project-dir {{PROJECT_DIR}} \
  --loop-id {{LOOP_ID}}
```

O analyzer lê os logs deste loop + specs anteriores e sugere ajustes para o próximo.

---

## 8. Check-list Pré-Execução

- [ ] Maker e Checker são agentes diferentes
- [ ] Arquivos proibidos estão listados explicitamente
- [ ] Comando de verificação foi testado manualmente 1x
- [ ] Orçamento de turnos é compatível com a complexidade
- [ ] Pasta `dors-loops/` existe e tem permissão de escrita
