# Verification Menu — Cardápio de Verificação

Lista expandida das opções de verificação oferecidas na Fase B da entrevista.
Cada opção inclui exemplos concretos, vantagens e riscos.

---

## Opção 1 — Determinística (Comando)

### O que é
Um comando shell que retorna exit code 0 (sucesso) ou ≠0 (falha).
O checker roda este comando após cada tentativa do Maker.

### Exemplos

| Linguagem / Framework | Comando | O que verifica |
|---|---|---|
| Python + pytest | `pytest tests/ -x --tb=short` | Todos os testes passam, para no primeiro erro |
| Python + pytest (só falhos) | `pytest --lf -x` | Só re-roda testes que falharam antes |
| Python + ruff | `ruff check src/ && ruff format --check src/` | Linting + formatação |
| TypeScript | `npx tsc --noEmit && npx eslint src/` | Compilação + linting |
| Rust | `cargo test && cargo clippy -- -D warnings` | Testes + clippy sem warnings |
| Go | `go test ./... && go vet ./...` | Testes + análise estática |
| Shell scripts | `shellcheck script.sh` | Linting de shell |
| Docker | `docker build -t test . && docker run --rm test` | Build + smoke test |
| Genérico | `make test` ou `make check` | O que o projeto já usa |

### Vantagens
- Rápido, inequívoco (passou ou não passou)
- Zero ambiguidade: exit code 0 = sucesso

### Riscos
- Comando mal calibrado pode ter falsos positivos (ex: testes quebrados que não eram do Maker)
- Não detecta problemas de design, só quebra funcional

---

## Opção 2 — Test-Driven (Testes)

### O que é
O Maker gera um teste NOVO antes de modificar o código. O checker:
1. Roda só o teste novo → deve falhar (RED)
2. Roda o teste novo + código → deve passar (GREEN)
3. Roda TODOS os testes → devem passar (sem regressão)

### Exemplo de comando do Checker

```bash
# Fase RED: só o novo teste, esperado FAIL
pytest tests/test_nova_feature.py -v && echo "RED_FAILED" && exit 1 || echo "RED_OK"

# Fase GREEN: novo teste + código
pytest tests/test_nova_feature.py -v

# Fase REGRESSION: todos os testes
pytest tests/ -x
```

### Vantagens
- Garante cobertura de teste para a mudança
- RED-GREEN-REGRESSION é difícil de "hackear"

### Riscos
- Mais lento que opção 1
- Maker pode gerar teste fraco que sempre passa

---

## Opção 3 — Visual/Manual (Aprovação Humana)

### O que é
Após cada tentativa, o Maker para e pede aprovação humana.
O loop só avança quando o humano digita "ok" ou equivalente.

### Exemplo de fluxo

```
[Maker] Modifiquei src/auth.py, git diff:
+ def validate_token(t):
+     return jwt.decode(t, SECRET)

[Checker — Humano] Revise as mudanças acima.
Digite 'ok' para aprovar, 'reject' para rejeitar, ou 'skip' para pular esta iteração.
```

### Vantagens
- Segurança máxima (humano no loop)
- Ideal para código crítico (pagamentos, auth, infra)

### Riscos
- Lento (depende de resposta humana)
- Não escala para 50+ iterações
- Humano pode aprovar sem revisar de verdade

---

## Opção 4 — Mista (Comando + Humano)

### O que é
Combina Opção 1 (comando automático) + Opção 3 (aprovação humana).
O checker automático roda primeiro. Se passar, pausa para o humano.

### Exemplo de fluxo

```
[Turno N]
Maker: modificou 3 arquivos

Checker automático:
$ pytest tests/ -x --tb=short
========================= 47 passed in 2.3s =========================
✅ Verificação automática passou.

[Humano] 3 arquivos modificados:
- src/auth.py
- src/models.py
- tests/test_auth.py

Digite 'ok' para avançar, 'reject' para rejeitar, 'diff' para ver diff completo.
```

### Vantagens
- Segurança do humano + velocidade do automático
- Humano só vê mudanças que já passaram no automático

### Riscos
- Complexidade maior de setup
- Ponto de lentidão se humano demorar

---

## Como escolher

| Cenário | Recomendação |
|---|---|
| Refatoração grande, sem risco de quebrar | Opção 1 (determinística) |
| Feature nova, precisa de cobertura | Opção 2 (test-driven) |
| Código de pagamento, auth, ou infra crítica | Opção 3 (visual) ou 4 (mista) |
| CI/CD pipeline, sem humano disponível | Opção 1 ou 2 |
| Primeiro loop do projeto (aprendendo) | Opção 4 (mista) |
