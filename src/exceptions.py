class NeoException(Exception):
    """Base exception for all Neo-related errors"""
    pass


class TransactionFailedException(NeoException):
    """Raised when a transaction fails on-chain"""
    
    def __init__(self, message: str, tx_hash: str = None, exception: str = None):
        self.tx_hash = tx_hash
        self.exception = exception
        super().__init__(message)


class ContractValidationException(NeoException):
    """Raised when pre-transaction validation fails"""
    pass


class ConfigurationException(NeoException):
    """Raised when configuration is invalid or missing"""
    pass


class WitnessException(NeoException):
    """Raised when witness/signature verification fails"""
    pass
