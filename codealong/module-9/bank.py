"""Module 9 code-along — a tiny module to MEASURE.

`deposit()` gets tested; `withdraw()` is deliberately left UNtested, so
`pytest --cov=bank --cov-report=term-missing` reveals the gap (Section 1).
"""


class BankError(Exception):
    pass


class BankAccount:
    def __init__(self, balance: float = 0.0):
        self.balance = balance

    def deposit(self, amount: float) -> float:
        if amount < 0:
            raise BankError("deposit must be positive")
        self.balance += amount
        return self.balance

    def withdraw(self, amount: float) -> float:        # <- no test reaches this → coverage gap
        if amount > self.balance:
            raise BankError("insufficient funds")
        self.balance -= amount
        return self.balance
