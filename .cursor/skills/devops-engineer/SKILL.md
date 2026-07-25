---
name: devops-engineer
description: Especialista DevOps (Docker, Compose, K8s, Traefik/Nginx, Cloudflare, CI/CD, observabilidade). Usar ao criar/alterar Dockerfile, compose, stacks Portainer, pipelines, backup/restore, monitoramento ou deploy.
---

# Skill: DevOps Engineer

Operação e infraestrutura para a plataforma SaaS multitenant 4Pro_BI — aplicações **containerizadas**, **monitoradas**, **escaláveis**, **observáveis** e **seguras**.

## Stack relevante

- Docker / Docker Compose / Portainer stacks (`infra/compose`, `infra/portainer`)
- Kubernetes (quando o ambiente exigir orquestração além de Compose)
- Traefik / Nginx (proxy reverso; `apps/web` usa Nginx)
- Cloudflare (DNS, TLS edge, WAF — quando aplicável ao ambiente)
- CI/CD — GitHub Actions (`.github/workflows`)
- Linux, PostgreSQL, Redis, RabbitMQ (ou Celery + Redis conforme o módulo)
- Prometheus, Grafana, Loki (ou stack equivalente documentada no repo)

Respeitar a regra de reset/stack: `.cursor/rules/10-container-reset.mdc`. Deploy recomendado: `infra/portainer/stack-4pro-bi.yml` + scripts `scripts/stack-*.sh`.

## Objetivos de toda aplicação / serviço

| Qualidade | Expectativa |
| --- | --- |
| Containerizada | Dockerfile reproduzível; multi-stage quando reduzir ataque/tamanho |
| Monitorada | Healthcheck + métricas (Prometheus ou equivalente) |
| Escalável | Stateless onde possível; volumes só para dados; worker separado |
| Observável | Logs estruturados, correlation/request id, dashboards mínimos |
| Segura | Segredos só por env; portas mínimas; rede interna; sem root desnecessário |

## Entregáveis obrigatórios (checklist)

Ao criar ou alterar deploy de um serviço, **sempre** gerar ou atualizar:

1. **Dockerfile** — build determinístico; `.dockerignore`; utilizador não-root quando viável
2. **docker-compose** / stack Portainer — serviços, `depends_on` com health
3. **healthcheck** — em todos os serviços críticos (API, web, Postgres, Redis, filas, object storage)
4. **restart policy** — `unless-stopped` (ou política K8s equivalente: restart/liveness)
5. **logs** — driver/config documentada; sem segredos/PII em claro; retenção referida
6. **network** — rede bridge/nomeada por stack; comunicação service-to-service sem expor ao host
7. **volumes** — dados persistentes nomeados; paths documentados
8. **backup** — script/procedimento para Postgres (e volumes críticos); retenção
9. **restore** — procedimento testável documentado
10. **rollback** — como voltar imagem/tag ou compose anterior sem downtime se possível
11. **monitoramento** — health + métricas; alertas mínimos documentados
12. **README** — estrutura de deploy, variáveis, ordem de subida, smoke pós-deploy

## Proibições

1. Nunca expor portas desnecessárias no host — só o que o utilizador/proxy precisa (web/API pública); Postgres/Redis/broker ficam na rede interna em produção.
2. Nunca hardcodar segredos — JWT, passwords, tokens só via environment / secrets do CI ou Portainer.
3. Nunca usar `down -v` / apagar volumes sem pedido explícito de limpar dados.
4. Nunca misturar marcas OSS na UX de utilizador final (ver `docs/ARCHITECTURE.md` § Aceleradores); nomes técnicos em `infra/` e ADRs são OK.
5. Nunca fazer deploy grande sem plano (feature grande → plano/ticket primeiro).
6. Nunca confiar só no frontend para isolamento de rede/tenant.

## Padrões Compose / stack

```yaml
# Padrão mínimo por serviço de aplicação
services:
  exemplo:
    image: ${EXEMPLO_IMAGE:-fourpro/exemplo:tag}
    restart: unless-stopped
    env_file: .env
    environment:
      DATABASE_URL: ${DATABASE_URL}
    networks:
      - fourpro
    healthcheck:
      test: ["CMD-SHELL", "curl -fsS http://127.0.0.1:8000/api/v1/health || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
    # ports: só se precisar no host; preferir proxy interno
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```

- Preferir `depends_on` com `condition: service_healthy` para DB/cache.
- Em produção Portainer: não publicar Postgres/Redis no host; MinIO/API só se necessário e com ACL.
- Variáveis: documentar em `.env.example` / `.env.production.example` sem valores reais de produção.

## CI/CD (GitHub Actions)

- Gates existentes em `.github/workflows/ci.yml` devem continuar verdes.
- Imagens: build com tag imutável (SHA/semver); evitar `latest` em produção.
- Secrets só via GitHub Secrets / OIDC — nunca em YAML.
- Deploy: preferir pull + recreate controlado; documentar zero-downtime (rolling / health antes de cortar tráfego).
- Lint de workflows: `scripts/lint-github-actions.sh` quando alterar Actions.

## Backup, restore e rollback

| Operação | Mínimo esperado |
| --- | --- |
| Backup | Dump Postgres (`pg_dump`) agendável; opcional snapshot de volumes MinIO/uploads; destino e retenção documentados |
| Restore | Passos numerados; validar health + smoke API após restore |
| Rollback | Tag/imagem anterior + redeploy; migrações Alembic — documentar se forward-only e como mitigar |
| Zero-downtime | Quando possível: healthcheck verde antes de rotear; workers drenar tarefas; evitar `down -v` |

Scripts de stack existentes: `scripts/stack-up.sh`, `stack-down.sh`, `stack-ps.sh`, `stack-logs.sh`. Novos scripts de backup/restore devem viver em `scripts/` ou `infra/scripts/` com README.

## Observabilidade

- Health: `/api/v1/health` (API); equivalentes para web/Nginx e dependências.
- Métricas: endpoint/expositor operacional (não no portal do cliente) ou integração Compose documentada (Prometheus/Grafana).
- Logs: agregação (Loki ou equivalente) quando o ambiente tiver stack; senão json-file com rotação.
- Alinhar com TICKET-013 (observabilidade enterprise) e `docs/SECURITY.md` (retenção, sem PII).

## Proxy, TLS e Cloudflare

- Nginx/Traefik como único edge público quando possível; API atrás do proxy.
- `RATE_LIMIT_TRUST_PROXY=true` **só** com proxy de confiança (ver `infra/portainer/README.md`).
- TLS terminado no edge (Cloudflare/Traefik) ou no proxy local; nunca commitar certificados.

## Fluxo de trabalho DevOps

1. Confirmar objetivo e ambiente (dev Compose vs Portainer vs K8s).
2. Mapear portas, redes, volumes e segredos necessários.
3. Escrever/ajustar Dockerfile + compose/stack com healthcheck, restart, logging, network.
4. Documentar README de deploy (subida, smoke, rollback, backup/restore).
5. Garantir variáveis em `.env.example` (sem segredos reais).
6. Validar localmente: `compose config`, up, health, smoke (`GET /api/v1/health`).
7. Atualizar CI se o contrato de build/deploy mudar.
8. Registar decisões relevantes em `docs/ARCHITECTURE.md` ou ADR quando forem estruturais.

## Alinhamento com o repo

- Stacks: `infra/portainer/`, Compose dev: `infra/compose/`
- Reset/redeploy: `.cursor/rules/10-container-reset.mdc`
- Segurança: `.cursor/rules/06-security.mdc`
- Arquitetura / aceleradores OSS: `docs/ARCHITECTURE.md`
- Agente: `docs/AGENTS.md` § DevOps Engineer
- Observabilidade planeada: `docs/plans/TICKET-013-observability-enterprise-detailed-plan.md`

## Definition of done

Deploy/serviço considerado pronto quando:

- [ ] Dockerfile + compose/stack atualizados
- [ ] healthcheck + restart policy em serviços críticos
- [ ] network e volumes definidos; portas host mínimas
- [ ] config só por environment; `.env.example` atualizado
- [ ] logs com rotação; sem segredos em claro
- [ ] procedimento de backup + restore documentado
- [ ] procedimento de rollback (e nota de migrações) documentado
- [ ] README de deploy / estrutura clara
- [ ] monitoramento mínimo (health ± métricas) referido
- [ ] atualização sem downtime documentada quando aplicável
- [ ] smoke pós-deploy definido
