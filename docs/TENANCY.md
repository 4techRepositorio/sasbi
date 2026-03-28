# Tenancy

## Diretrizes
- Toda entidade de negócio sensível deve possuir `tenant_id`.
- Toda consulta deve ser filtrada por contexto do tenant autenticado.
- Não confiar em `tenant_id` vindo do frontend sem validação de sessão.
- A auditoria deve registrar o tenant associado à ação.
