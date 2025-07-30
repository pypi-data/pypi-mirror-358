from enum import Enum


class AccountType(str, Enum):
    CERTIFICATE = "Certificate"
    CHECKING = "Checking"
    DDALOAN = "DdaLoan"
    LOAN = "Loan"
    NONE = "None"
    SAVINGS = "Savings"
    UNKNOWN = "Unknown"

    def __str__(self) -> str:
        return str(self.value)
