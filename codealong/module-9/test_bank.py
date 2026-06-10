"""Module 9 · Section 1 — coverage.

We test deposit() but NOT withdraw() on purpose. Run:

    pytest --cov=bank --cov-report=term-missing

…and watch `bank.py` come in under 100% with withdraw's lines listed as Missing.
Then add a withdraw test and watch it climb. (`--cov-fail-under=100` would fail now.)
"""

import pytest

from bank import BankAccount, BankError


def test_deposit_increases_balance():
    acct = BankAccount(100.0)
    assert acct.deposit(50) == 150.0


def test_deposit_negative_raises():
    with pytest.raises(BankError):
        BankAccount().deposit(-5)
