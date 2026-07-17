# Parecer de Correções — Auditoria Independente do Davi (Modelo Canônico)

**Data:** 2026-07-16 (referente à remediação de 13–15/07/2026)
**Autor:** Leonardo (Engenharia de Dados)
**Referência:** *Parecer de Auditoria Independente — Modelo Canônico GEX*, de 2026-07-12 (Davi)
**Escopo:** somente o modelo canônico. Nenhum processo fora do canônico foi tocado.
**Método:** cada achado foi tratado seguindo boas práticas — correção contida no canônico, **validada em produção com query** e alinhada ao que já existe nos processos ativos.

---

## 1. Sumário

Todos os achados da auditoria do Davi foram endereçados. Divididos por natureza:

- **Corrigidos e validados em produção (12).**
- **Caracterizados como comportamento esperado / não-bug (3).**
- **Decisões de negócio (resolvidas no retorno do Gabriel de 15/07) (3).**
- **Resíduos / limitação de origem (documentados) (3).**

**Princípio aplicado:** o canônico não descarta dado (é a fonte da verdade completa); regras de negócio ficam na camada de métrica; e nada que redefine receita/semântica foi alterado sem precedente confirmado ou sem sinalizar decisão.

---

## 2. Corrigidos e validados em produção

| # (auditoria) | Achado | Correção (só canônico) | Antes | Depois (validado) |
|---|---|---|---|---|
| 4 | Câmbio fixo em 5,10 | Filtro do par invertido (bronze é USD→BRL) | constante 5,10 | **72 taxas, 4,887–5,206** |
| 4 | Slug de produto (12,2% vazio) | `lower()` antes do regex + parse de Bottle/Pote | 12,19% vazio | **0,88% vazio** |
| 4 | **IVA invertido** (preço > coletado) | Regra confirmada com Gabriel: coletado = `total_clean`; preço = coletado − IVA | preço $162,08M > coletado $153,7M | **coletado $162,77M = preço $154,4M + IVA; 0 invertidas** |
| 2 | `id_grupo_pedido` CB não une front+upsell | `coalesce(upsellparentreceipt, receiptnumber)` | **0%** dos upsells ligam no front | **97,2%** |
| 3 | `vl_taxa_usd` CB "não é fee" (mediana US$16k) | Dedup da fee por `(id, productitemnumber)` antes de somar | mediana **US$16.347** | mediana **US$49,34** |
| 9/10 | 680 órfãos em `map_produto_gateway` | Filtro de chave vazia | 680 (553 vazios) | **188 (0 vazios)** |
| 11 | `vl_liquido_usd` ausente em `met_transacao_status` | Coluna adicionada (preço − refund − chargeback) | não existia | **0 nulos, 0 erro de fórmula** |
| 8/10 | `cancelamento` distorcendo métrica | **Mantido** no canônico + **isolado** em `vl_cancelamento_usd`, fora da receita líquida | somava junto | **-US$30,58M isolado; receita não distorcida** |
| 4 | `qt_unidades` sempre 1 (BG) | Parse da quantidade real do nome ("6 Bottles"→6) | 100% = 1 | **92% com qtd; qt distintos 2→9; custo $3,02M→$18,11M** |
| — | `cd_tipo_item` = `front` fixo (funil colapsado) | Derivado dos flags reais (`flag_frontend`/`flag_upsell`/`funnel_step`) nos 4 paths | funil irreal | **funil real: 64,7% front / 29,9% upsell / 5,4% bump** |
| 1 (principal) | **`alerta_chargeback` nunca dispara** | Classificado a partir de `cancel_reason` (API): `ChargebackAlert*` → `alerta_chargeback` | **0** eventos | **38.863 eventos** |
| — | `ds_motivo` 100% vazio | Populado com `cancel_reason` da API | **0** preenchidos | **113.729 preenchidos** |
| 4/6 | Dupla-fonte (webhook + API) inativa | `merge_sources` compõe API+webhook sem duplicar; default `orders_raw` | webhook-only (99,99%) | **ativa e permanente; 07-08 recuperado 1.571→3.909** |

**Reconciliação:** `fct_transacoes` = `met_transacao_status` (1:1 exata); `id_transacao` (PK) **100% único** (0 duplicatas, mesmo com a dupla-fonte).

---

## 3. Caracterizados — comportamento esperado, não é bug

| # | Achado | Diagnóstico (com evidência) |
|---|---|---|
| 8 | Eventos órfãos BG | **100% explicados:** 83% são `cancelamento` (decisão), 17% são refund/chargeback de venda fora da janela (limitação de origem), <1% é freshness. Nenhum é defeito. |
| 1 | Risco de dupla contagem 57,4% BG | **Receita segura:** soma por `id_transacao` (PK único) = sem dupla contagem. A colisão é do `id_grupo_pedido`, idêntico ao processo existente; só afeta agrupamento de funil. |
| 4 | `dt_evento_utc` = data da venda | **Limitação de origem:** o webhook só traz `rr_createdate`. Mitigado onde a API cobre (dupla-fonte ativa). |

---

## 4. Decisões de negócio — resolvidas no retorno do Gabriel (15/07)

As 3 decisões pendentes da auditoria foram respondidas pelo Gabriel e implementadas:

1. **Cancelamento** → manter isolado (o `cancel` do webhook é fechamento de ciclo de refund; o dinheiro já foi abatido). Cancel de assinatura passou a evento próprio `assinatura_cancelada` (US$0).
2. **Retry** → a premissa não existe no dado (100% dos pedidos aprovados; não há cobrança recusada entrando). Nada a fazer.
3. **Chave de funil** → `conta + user_id + sessid2` + corte de 6h. Colisão caiu de 5.696 para 983 grupos.

*(Detalhes e a implementação completa das assinaturas estão no parecer companheiro: "Parecer de Implementação — Assinaturas no Modelo Canônico".)*

---

## 5. Resíduos / limitação de origem

| # | Item | Situação |
|---|---|---|
| 7 | Buraco jun/jul ClickBank | Falha de extração na origem (API Analytics CB); reprocessar não recupera — precisa re-extração. |
| 12/13 | `cd_status_entrega` CB NULL; `dim_afiliado` sem nome | Limitações de origem (o gateway não emite o dado). |
| 5 | DDL do vault desatualizado | **FEITO:** schema real versionado em `gex-infra-aws/docs/schema-real-canonico-prod.md`. |

---

## 6. Conclusão

**Tudo que era corrigível dentro do modelo canônico foi corrigido e validado em produção**, sem impacto em nenhum processo externo. O ponto mais relevante que **não** é bug — o "risco de dupla contagem de receita" — **não se materializa** (PK única). E o "principal defeito" da auditoria (`alerta_chargeback` que nunca disparava) está **resolvido** (38.863 alertas classificados).

As 3 decisões de negócio que restavam foram **resolvidas no retorno do Gabriel** e implementadas (ver parecer companheiro de assinaturas). Os itens remanescentes são **limitações de origem** (extração ClickBank, campos que o gateway não envia), documentados.

---

### Anexo — evidências de validação (prod)
- BuyGoods `fct`: câmbio `count(distinct)=72` (4,887–5,206); produto vazio 0,88%; `coletado > preço` (162,77 > 154,4M), 0 invertidas; `count(*) − count(distinct id_transacao) = 0`.
- ClickBank: upsells em grupo com front = 97,2%; mediana `vl_taxa_usd` chargeback = US$49,34.
- Map: órfãos = 188; vazios = 0.
- `alerta_chargeback`=38.863; `ds_motivo` preenchido=113.729.
- Funil real: 64,7% front / 29,9% upsell / 5,4% bump; dupla-fonte ativa (07-08 recuperado).
