# fourpro-connectors

SPI e plugins de fontes de dados para a plataforma 4Pro_BI (TICKET-015).

## Conteúdo

- `fourpro_connectors.base` — `BaseConnector` (capabilities, validate_config, test_connection, discover, sample_schema, extract)
- `fourpro_connectors.registry` — registo de tipos de conector
- Plugins: `file`, `postgres`, `mysql`, `sqlserver`, `rest_json`, `s3_compatible`
- Segurança: allowlist URL / bloqueio de IPs privados (REST), SQL só com identificadores validados + queries parametrizadas, segredos nunca logados

## Extract

`extract(...)` escreve CSV ou JSON num `stage_path` e devolve `ExtractResult` (caminho, formato, tamanho, metadados). O worker cria `FileIngestion` e reutiliza o pipeline de parse.

## Instalação

```bash
pip install -e ./packages/connectors
# opcional SQL / S3:
pip install -e "./packages/connectors[sql,s3]"
```

## Testes unitários do pacote

```bash
cd packages/connectors && pytest
```
