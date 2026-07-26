"""Unitários — validação anti-MIME-spoof de uploads."""

import pytest

from fourpro_api.services.upload_validation import UploadContentError, validate_upload_content


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.ingestion
def test_empty_file_rejected() -> None:
    with pytest.raises(UploadContentError, match="vazio"):
        validate_upload_content(declared_name="a.csv", body=b"")


@pytest.mark.unit
@pytest.mark.ingestion
def test_json_object_and_array_ok() -> None:
    validate_upload_content(declared_name="o.json", body=b'{"a":1}')
    validate_upload_content(declared_name="a.json", body=b"[1,2]")


@pytest.mark.unit
@pytest.mark.security
def test_json_invalid_rejected() -> None:
    with pytest.raises(UploadContentError, match="JSON"):
        validate_upload_content(declared_name="bad.json", body=b"not-json")
    with pytest.raises(UploadContentError, match="JSON"):
        validate_upload_content(declared_name="bad.json", body=b"{broken")


@pytest.mark.unit
@pytest.mark.ingestion
def test_csv_and_txt_utf8_ok() -> None:
    validate_upload_content(declared_name="d.csv", body=b"a,b\n1,2\n")
    validate_upload_content(declared_name="n.txt", body="olá\n".encode())


@pytest.mark.unit
@pytest.mark.security
def test_csv_non_utf8_rejected() -> None:
    with pytest.raises(UploadContentError, match="UTF-8"):
        validate_upload_content(declared_name="bad.csv", body=b"\xff\xfe\x00")


@pytest.mark.unit
@pytest.mark.security
def test_xlsx_and_xls_signatures() -> None:
    validate_upload_content(declared_name="ok.xlsx", body=b"PK\x03\x04" + b"\x00" * 8)
    validate_upload_content(
        declared_name="ok.xls",
        body=b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"\x00" * 4,
    )
    with pytest.raises(UploadContentError, match="XLSX"):
        validate_upload_content(declared_name="fake.xlsx", body=b"not-zip")
    with pytest.raises(UploadContentError, match="XLS"):
        validate_upload_content(declared_name="fake.xls", body=b"not-ole")


@pytest.mark.unit
@pytest.mark.security
def test_unsupported_extension() -> None:
    with pytest.raises(UploadContentError, match="não suportada"):
        validate_upload_content(declared_name="x.exe", body=b"MZ")
