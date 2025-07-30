class PinScrapException(Exception):
    pass

class ScraperException(PinScrapException):
    pass

class PinterestInteractionException(ScraperException):
    pass
