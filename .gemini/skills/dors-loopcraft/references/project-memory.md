# Project Memory — Memória de Loops no Projeto

## Bootstrap quando a skill entra em um projeto

Quando o usuário instalar/copiar a skill no projeto correto, inicialize a memória local assim:

1. Detecte o project root (`git rev-parse --show-toplevel` quando possível).
2. Crie `dors-loops/` dentro desse project root.
3. Copie os utilitários da skill para `dors-loops/scripts/`.
4. Crie `.dors-registry.json` se ainda não existir.
5. A partir daí, todo novo loop deve salvar `spec.md`, `state.md` e `final.md` em `dors-loops/<loop-id>/`.

Regra: **contexto não é global por padrão**. Ele mora no projeto onde a skill foi instalada/usada, para evitar misturar aprendizados de projetos diferentes.

## Como funciona

O D.O.R.S. Loopcraft aprende com o histórico de loops do projeto.
Cada spec gerado é versionado em `dors-loops/` e vira contexto para o próximo.

## Estrutura de diretórios

```
meu-projeto/
├── dors-loops/                  # Pasta versionada (commite no git!)
│   ├── .dors-registry.json      # Registro de todos os loops
│   ├── scripts/                 # Utilitários locais da skill, copiados no bootstrap
│   │   ├── context-loader.py    # Carrega histórico antes de criar novo loop
│   │   └── loop-analyzer.py     # Analisa state/final depois da execução
│   ├── 2026-07-15-refatorar-auth/
│   │   ├── spec.md              # Contrato operacional (template preenchido)
│   │   ├── state.md             # Log turno-a-turno
│   │   └── final.md             # Sumário pós-loop
│   └── 2026-07-17-migrar-sql/
│       ├── spec.md
│       ├── state.md
│       └── final.md
└── ...
```

## Registry (.dors-registry.json)

Arquivo JSON que indexa todos os loops:

```json
{
  "project": "meu-projeto",
  "loops": [
    {
      "id": "2026-07-15-refatorar-auth",
      "status": "completed",
      "max_turns": 5,
      "turns_used": 3,
      "verification": "pytest --lf -x",
      "lessons": [
        "Checker muito estrito — afrouxar timeout de 5s para 10s",
        "Arquivos de config não estavam nos proibidos — adicionar *.cfg"
      ]
    }
  ],
  "patterns": {
    "common_failures": ["timeout em testes de integração", "flake8 vs ruff conflito"],
    "safe_defaults": {
      "forbidden_paths": ["*.env", "*.key", "migrations/"],
      "preferred_checker": "pytest --lf -x"
    }
  }
}
```

## Scripts que usam esta memória

### `context-loader.py`

Roda na **Etapa 0** (antes da entrevista).
Lê `dors-loops/` e extrai:
- Lições de loops anteriores (ex: "3 loops falharam por timeout")
- Padrões de projeto (ex: "sempre usa pytest como checker")
- Arquivos proibidos recorrentes

Output: bloco de contexto injetado na entrevista.

### `loop-analyzer.py`

Roda **após** cada loop (comando "AMANHÃ").
Lê o `state.md` do loop atual + specs anteriores.
Detecta:
- Thrashing (mesmo erro 3+ vezes)
- Falsos positivos do checker
- Padrões de falha recorrentes entre loops

Output: diagnóstico + sugestões de ajuste no spec.

## Boas práticas

1. **Commite `dors-loops/` no git.** É documentação viva do projeto.
2. **Não apague specs antigos.** Eles são o "cérebro" do contexto.
3. **Após cada loop, preencha `final.md`.** É o que o `context-loader.py` mais valoriza.
4. **Se mudar de orquestrador, mantenha a pasta.** Os scripts são agnósticos de plataforma.
