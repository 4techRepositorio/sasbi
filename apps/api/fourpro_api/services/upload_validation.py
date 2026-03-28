import json
from pathlib import Path


class UploadContentError(Exception):
    """Conteúdo não corresponde à extensão declarada."""


def validate_upload_content(*, declared_name: str, body: bytes) -> None:
    """Validação mínima anti-MIME-spoof: conteúdo vs extensão."""
    if not body:
        raise UploadContentError("Ficheiro vazio")

    ext = Path(declared_name or "").suffix.lower().lstrip(".")
    if ext == "json":
        text = body[: 512 * 1024].decode("utf-8", errors="strict").lstrip()
        if not text.startswith("{") and not text.startswith("["):
            raise UploadContentError("JSON inválido: esperado objeto ou array")
        try:
            json.loads(body.decode("utf-8", errors="strict"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise UploadContentError("JSON inválido") from e
    elif ext in ("csv", "txt"):
        try:
            body[: 64 * 1024].decode("utf-8", errors="strict")
        except UnicodeDecodeError as e:
            raise UploadContentError("Conteúdo não é texto UTF-8 válido para CSV/TXT") from e
    elif ext == "xlsx":
        if not body.startswith(b"PK\x03\x04"):
            raise UploadContentError("XLSX inválido: esperado arquivo ZIP (Office Open XML)")
    elif ext == "xls":
        if not body.startswith(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"):
            raise UploadContentError("XLS inválido: assinatura OLE2 não encontrada")
    else:
        raise UploadContentError(f"Extensão não suportada: {ext}")
