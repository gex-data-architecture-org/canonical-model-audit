# Tasks ClickUp — Canônico BuyGoods (Assinaturas)

**Data:** 2026-07-15 · **Atuação:** Engenharia (Leonardo) · **Escopo:** somente modelo canônico

---

## ▶️ ATUAR AGORA (não bloqueado)

| # | Task | Descrição | Depende de |
|---|---|---|---|
| 1 | Marcar produtos de assinatura (`fl_recorrente`) | Flag em `fct_transacoes` identificando os produtos KIT/recorrentes | — |
| 2 | Criar evento `assinatura_cancelada` | Reclassificar os cancelamentos de assinatura em `fct_eventos_pos_venda` (US$0 de movimento) | — |
| 3 | Nova chave de funil (`conta + user_id + sessid2` + 6h) | Trocar `id_grupo_pedido`, reprocessar e validar agrupamento front+upsell | — |
| 4 | Criar tabela `fct_cobrancas` | "Extrato" de cobranças (1 linha por cobrança); recupera os **US$ 38.504** de receita hoje invisível; reprocessar métricas + validar | 1 |
| 5 | Criar tabela `fct_assinaturas` (versão possível) | Assinaturas ativas/canceladas derivadas do dado atual | 1, 2, 4 |
| 6 | Mitigar risco da API (varredura dirigida) | Re-extração periódica da janela de criação dos pedidos recorrentes não-terminais (cobre refund/cobrança tardios até a BuyGoods liberar `updated_at`) | — |
| 7 | Reprocessar + validar + documentar | Validação em produção (receita, reembolso ≤ coletado, PK única) + documentação pós-entrega | 1–6 |

---

## 🔒 IMPEDIMENTOS (aguardando BuyGoods)

| # | Task | Bloqueado por |
|---|---|---|
| 8 | Completar `fct_assinaturas` (100%: próxima cobrança, dunning, churn) | Endpoint de assinaturas + acesso às telas (RPA) |
| 9 | Conserto definitivo do risco da API (busca por `updated_at`) | Filtro `updated_at` na API de pedidos |
| 10 | Agrupamento de funil 100% (ID de pedido-mãe nativo) | ID de grupo de pedido nativo |
| 11 | Enriquecimento por cliente (LTV, dedup por pessoa) | Endpoint de customers (já pedido em 02/07) |

---

## 📨 DESBLOQUEIO (ação do Davi)

| # | Task | Descrição | Prazo |
|---|---|---|---|
| 12 | Acionar CTO da BuyGoods | Enviar os 4 pedidos: **`updated_at` (URGENTE)**, endpoint de assinaturas, ID de grupo nativo, endpoint de customers | — |
| 13 | Régua da recorrência (FunnelOps) | O que o cliente recebe por ciclo, régua exata e confirmação do dunning | 18/07 |
