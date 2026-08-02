"""
Unit tests for password hashing and verification.
No DB, no async — pure function tests.
"""

import pytest

from app.auth.password import hash_password, verify_password


def test_hash_is_not_plain_text():
    plain = "MySecurePass123!"
    hashed = hash_password(plain)
    assert hashed != plain


def test_verify_correct_password():
    plain = "MySecurePass123!"
    hashed = hash_password(plain)
    assert verify_password(plain, hashed) is True


def test_verify_wrong_password():
    hashed = hash_password("correct-horse-battery")
    assert verify_password("wrong-password", hashed) is False


def test_two_hashes_of_same_password_differ():
    """bcrypt uses random salt — same input should produce different hashes."""
    plain = "SamePassword99"
    h1 = hash_password(plain)
    h2 = hash_password(plain)
    assert h1 != h2
    # But both should verify correctly
    assert verify_password(plain, h1) is True
    assert verify_password(plain, h2) is True


def test_empty_string_hashes_and_verifies():
    """Edge case: empty password should still hash/verify consistently."""
    h = hash_password("")
    assert verify_password("", h) is True
    assert verify_password("x", h) is False
