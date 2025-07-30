class PinScrapException(Exception):
    """Excepción base para todos los errores de PinScrap."""
    pass

class PinterestInteractionException(PinScrapException):
    """Se produce cuando hay un error al interactuar con Pinterest."""
    pass

class PinNotFoundError(PinScrapException):
    """Se produce cuando no se encuentra un pin específico."""
    pass

class InvalidPinUrlError(PinScrapException):
    """Se produce cuando la URL de un pin no es válida."""
    pass

class RateLimitExceededError(PinScrapException):
    """Se produce cuando se excede el límite de solicitudes a Pinterest."""
    pass

class AuthenticationError(PinScrapException):
    """Se produce cuando hay un error de autenticación con Pinterest."""
    pass

class NetworkError(PinScrapException):
    """Se produce cuando hay un error de red al intentar conectarse a Pinterest."""
    pass

class ScraperError(PinScrapException):
    """Se produce cuando hay un error en el proceso de scraping."""
    pass
