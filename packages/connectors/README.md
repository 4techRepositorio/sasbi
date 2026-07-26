# fourpro-connectors

SPI de conectores de dados (TICKET-015). Implementações: `file`, `postgres`, `rest_json`.

```bash
pip install -e packages/connectors
```

A API e o worker importam `fourpro_connectors.registry`. Credenciais nunca circulam nos DTOs de listagem — só no cofre da API.
