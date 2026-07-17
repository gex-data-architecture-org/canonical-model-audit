# Parecer de Implementação — Assinaturas no Modelo Canônico

**Data:** 2026-07-16 (referente à implementação de 2026-07-15)
**Autor:** Leonardo (Engenharia de Dados)
**Referência:** Memo do Gabriel de 15/07 (assinaturas, cancelamento, retry & chave de funil) — retorno da auditoria
**Escopo:** somente o modelo canônico. `fct_transacoes` permanece imutável. Nada fora do canônico foi alterado.
**Método:** cada entrega foi codificada, deployada via CD, executada e **validada em produção com query**.

---

## 1. Contexto

Após o retorno da auditoria do Gabriel, ficou confirmado que **vendemos assinatura** (produtos "Kit 5 Potes", sku `KITBUNDLEBG9`, recorrência: trial US$29 → US$169/mês até o cliente cancelar) e que o modelo canônico **não tratava recorrência**. Validei o impacto no dado real: **US$ 38.504 em cobranças de ciclos posteriores ficavam invisíveis** (o modelo registrava só a 1ª cobrança) — causa direta do achado "reembolso maior que o valor cobrado" da auditoria.

As 3 dúvidas anteriores foram resolvidas (cancelamento isolado, retry inexistente no dado, chave de funil definida) e a descoberta de assinatura gerou um plano de 7 entregas, todas **executadas e validadas** em 15/07.

---

## 2. O que foi implementado (7 entregas)

| # | Entrega | Descrição técnica | Resultado validado em prod |
|---|---|---|---|
| 1 | **`fl_recorrente`** em `fct_transacoes` | Flag por `sku=KITBUNDLEBG9` ou `codename` contendo KIT (nos 2 paths API+webhook) | 5.582 pedidos marcados |
| 2 | Evento **`assinatura_cancelada`** | Cancel de produto recorrente vira evento próprio com `vl_evento_usd=0` (não movimenta receita) | 3.589 eventos, US$ 0 |
| 3 | Nova **chave de funil** | `conta + user_id + sessid2` + sessionização de 6h pós-merge (corta reuso do cookie) | Colisão 5.696 → **983** grupos; 129.393 funis front+upsell |
| 4 | Tabela **`fct_cobrancas`** (nova) | 1 linha por cobrança: ato vem da `fct_transacoes`; ciclos recorrentes expandidos do `orders_raw` (N de "(N charges)", valor=(acumulado−ato)/(N−1), data aproximada) | 627 mil cobranças; `SUM` recupera **+US$ 38,4 mil** |
| 5 | Tabela **`fct_assinaturas`** (nova) | 1 linha por assinatura; deriva de `fct_transacoes` + `fct_cobrancas` + evento de cancelamento | 5.582 assinaturas (3.337 ativas / 2.245 canceladas), PK única |
| 6 | Mitigação do risco da API | `fct_cobrancas` faz rebuild total lendo o `orders_raw` atual — captura ciclos de pedidos antigos sem depender do `updated_at` | — |
| 7 | Reprocessar métricas | `met_transacao_status` + `met_vendas_diario` reprocessados | `fct` = `met` = 625.210 (reconciliação exata) |

---

## 3. Decisão de modelagem central

A recuperação da receita das assinaturas **não alterou a `fct_transacoes`** (que continua imutável, registrando o "ato" da compra). Em vez disso:

- **pedido ≠ cobrança:** a `fct_transacoes` guarda o pedido; a `fct_cobrancas` guarda cada cobrança.
- **"quanto o pedido pagou" = `SUM(fct_cobrancas)`** — é onde os US$ 38,4 mil de ciclos recorrentes aparecem.

Isso segue exatamente o desenho proposto pelo Gabriel ("nada é atualizado; o total pago é a soma das cobranças") e evita qualquer risco à receita histórica já consolidada.

---

## 4. Integridade e orquestração

- **Reconciliação:** `fct_transacoes` = `met_transacao_status` = **625.210** (1:1 exata).
- **PK 100% única** em todas as tabelas (0 duplicatas), inclusive nas 2 novas.
- **Receita da `fct_transacoes` inalterada** (US$ 168,5M) — as flags e a nova chave são aditivas.
- **Pipeline diário:** as 2 tabelas novas já estão plugadas no Step Functions `gex-canonical-daily-prod` — `fct_cobrancas` no **estágio 2** (após as transações) e `fct_assinaturas` no **estágio 3** (após as cobranças). O scheduler roda **todo dia às 23:00 (America/Sao_Paulo)**. Ou seja, atualizam-se sozinhas.

---

## 5. O que fica bloqueado — depende da BuyGoods (via Davi)

Entregue na "versão possível"; sinalizado no próprio dado (`fl_dado_incompleto=1`, `fl_data_aproximada=1`):

| Item | O que falta | Depende de |
|---|---|---|
| `fct_assinaturas` 100% | Data da próxima cobrança, dunning, churn preciso | Endpoint de assinaturas + acesso às telas (RPA) |
| Data real das cobranças de ciclo | Hoje é aproximada (venda + 30×n); a fonte não traz a data | Endpoint de assinaturas |
| Cobranças de ciclo de pedidos antigos sempre atuais | Busca incremental por mudança | Filtro `updated_at` na API |
| Agrupamento de funil 100% | Hoje ~99,3% (heurística) | ID de grupo de pedido nativo |
| Enriquecimento por cliente | LTV, dedup por pessoa | Endpoint de customers |

---

## 6. Monitoramento diário

Foi estabelecido um **health-check diário** do pipeline canônico, a ser rodado após a conclusão dos processos da AWS: verifica o status do Step Functions, o status de cada job Glue, o frescor do dado (última partição) e a integridade (reconciliação `fct`=`met`, PK única).

**Resíduo sob monitoramento:** 1 linha (de 627 mil) de cobrança de ciclo com data aproximada projetada à frente (`fl_data_aproximada=1`) — imaterial (0,0002%, sem efeito em receita), em acompanhamento para regularização automática no rebuild.

---

## 7. Conclusão

Tudo o que dependia de engenharia no retorno da auditoria do Gabriel foi **implementado, deployado e validado em produção** em 15/07, sem impacto em nenhum processo fora do modelo canônico. O modelo passou a tratar assinatura corretamente (2 tabelas fato novas), recuperou os ~US$ 38 mil de receita recorrente antes invisível, e manteve a `fct_transacoes` imutável e a receita histórica intacta.

Os itens restantes são **dependências externas da BuyGoods** (4 pedidos ao CTO, sendo o filtro `updated_at` o prioritário), já documentados e sinalizados no próprio dado.

---

### Anexo — commits (branch main, via CD)
`fl_recorrente` · `assinatura_cancelada` · chave de funil · `fct_cobrancas` (tabela+job) · `fct_assinaturas` (tabela+job) · fix PK · fix data de ciclo — de `9d1a749` a `820223c`.

### Anexo — evidências de validação (prod, 15/07)
- `fl_recorrente`=5.582 · `assinatura_cancelada`=3.589 (US$0) · colisão de funil 983 · funis front+upsell 129.393.
- `fct_cobrancas`: `SUM`=US$168,56M vs `fct` US$168,52M → +US$38.388 recuperados.
- `fct_assinaturas`: 5.582 (3.337 ativas / 2.245 canceladas), PK única, 0 dup.
- Reconciliação `fct`=`met`=625.210; jobs canônicos todos SUCCEEDED.
