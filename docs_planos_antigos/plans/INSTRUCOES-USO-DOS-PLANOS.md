# Instruções — como usar os planos separados

Estes ficheiros servem para **executar o projeto em passos pequenos**, com contexto mínimo no Cursor (ou com várias pessoas/agentes).

---

## 1. Onde está cada coisa

| O quê | Onde |
|--------|------|
| Índice de todos os sub-planos | [README.md](README.md) |
| Visão, regras, marcos comerciais, riscos | [00-VISAO-E-GOVERNANCA.md](00-VISAO-E-GOVERNANCA.md) |
| Ferramentas OSS e diagramas | [00-STACK-E-FLUXOS.md](00-STACK-E-FLUXOS.md) |
| **Um passo = um ficheiro** | Pasta [sub-planos/](sub-planos/) → `P0-01.md`, `P0-02.md`, … |
| Plano completo num só ficheiro (opcional) | [PLANO-MAESTRE-BI-SaaS-Por-Fases.md](PLANO-MAESTRE-BI-SaaS-Por-Fases.md) |
| Vários agentes em paralelo | [PLANO-MULTI-AGENTES.md](PLANO-MULTI-AGENTES.md) |

---

## 2. Ordem padrão (um de cada vez)

1. Abra o índice [README.md](README.md).
2. Comece por **P0-01** e siga a lista **até P0-07**.
3. Depois **P1-01** … **P1-06**, e assim por diante.
4. **Não avance** para o próximo ID se o **critério de Saída** do ficheiro atual não estiver cumprido.

Sub-planos marcados como **(Opcional)** no título ou no plano mestre podem ser saltados sem travar o núcleo (ex.: P3-05).

---

## 3. Como pedir execução no Cursor (uma única tarefa)

**Passo A.** Abra o ficheiro do passo, por exemplo:

`docs/plans/sub-planos/P0-01.md`

**Passo B.** Na conversa, escreva com clareza, por exemplo:

> Executa **apenas** o sub-plano **P0-01**. Usa o conteúdo do ficheiro aberto. Não avances para P0-02 neste mesmo pedido.

**Passo C.** Quando terminar, peça um resumo do que foi feito e **como testar** (3–8 linhas), e registe no `CHANGELOG.md` ou em `docs/releases/` se já existir.

**Evite:** “faz toda a fase 0” num único pedido, a menos que queira um PR grande e difícil de rever.

---

## 4. O que colar no chat (modelos prontos)

**Início de fase**

```text
Contexto: projeto Data_4tech BI SaaS, monorepo em /opt/data_4tech (ou o teu caminho).
Executa só o sub-plano P0-01. Ficheiro: docs/plans/sub-planos/P0-01.md
Critério: cumpre a "Saída" desse ficheiro antes de parar.
```

**Correção / ajuste**

```text
Sub-plano P2-04 já implementado. Revisa apenas segurança e multitenancy do loader Bronze.
Não alteres P2-05 neste pedido.
```

---

## 5. Multitenancy e contratos (crítico)

Antes de **P2-04** e **P3-01**, o **P0-05** (decisão Postgres: schema por tenant vs RLS) deve estar **fecho e documentado** em `docs/adr/`. Todos os agentedevem seguir o mesmo ADR.

---

## 6. Segredos e ambientes

- Nunca commitar `.env` com passwords.
- Manter `.env.example` com chaves **sem** valores reais.
- Cada sub-plano que toque em integração deve indicar **quais variáveis** são necessárias.

---

## 7. Windows vs Linux

Se o código estiver em **`C:\Desenvolvimento\Data_4tech`**, a estrutura é a mesma: `docs\plans\sub-planos\P0-01.md`, etc. Ajuste apenas caminhos nos comandos (`docker compose`, `npm`, etc.).

---

## 8. Resumo em uma frase

**Um ficheiro = um incremento fechado; um pedido = um ID; verificar Saída antes do próximo ID.**
