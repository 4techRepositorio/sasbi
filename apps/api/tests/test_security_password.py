"""Testes mínimos do hash de senha (TICKET-001)."""

from fourpro_api.core.security import hash_password, verify_password


def test_hash_password_round_trip() -> None:
    h = hash_password("my-secret-password")
    assert h != "my-secret-password"
    assert verify_password("my-secret-password", h) is True


def test_verify_password_rejects_wrong_plaintext() -> None:
    h = hash_password("correct-horse-battery")
    assert verify_password("wrong", h) is False
