"""
PinScrap - Una biblioteca de Python para extraer datos de Pinterest sin necesidad de API.

Esta biblioteca permite:
- Buscar pines por palabras clave
- Obtener información detallada de pines específicos
- Descargar imágenes de pines
- Obtener pines de usuarios específicos

Ejemplo de uso:
    ```python
    import asyncio
    from pinscrap import PinScrapClient, download_pin_image

    async def main():
        # Crear una instancia del cliente
        client = PinScrapClient(headless=True)
        
        try:
            # Buscar pines
            result = await client.search("python programming")
            print(f"Encontrados {result.pin_count} pines")
            
            # Descargar la primera imagen
            if result.pins:
                pin = result.pins[0]
                print(f"Descargando: {pin.description}")
                await download_pin_image(pin.image_url, "downloads")
                
                # Obtener información detallada de un pin
                pin_info = await client.get_pin_info(pin.link)
                print(f"Información del pin: {pin_info}")
        finally:
            # Cerrar el navegador
            await client.close()

    # Ejecutar la función asíncrona
    asyncio.run(main())
    ```
"""

__version__ = "1.0.0"

# Importar las clases y funciones principales
from .client import PinScrapClient
from .models import Pin, SearchResult, PinCreator
from .utils import download_pin_image, batch_download, download_file

# Importar excepciones
from .exceptions import (
    PinScrapException,
    PinterestInteractionException,
    PinNotFoundError,
    InvalidPinUrlError,
    RateLimitExceededError,
    AuthenticationError,
    NetworkError,
    ScraperError,
    DownloadError,
    UnsupportedFileTypeError
)

# Exportar las clases y funciones principales
__all__ = [
    # Clases principales
    'PinScrapClient',
    'Pin',
    'SearchResult',
    'PinCreator',
    
    # Funciones de utilidad
    'download_pin_image',
    'batch_download',
    'download_file',
    
    # Excepciones
    'PinScrapException',
    'PinterestInteractionException',
    'PinNotFoundError',
    'InvalidPinUrlError',
    'RateLimitExceededError',
    'AuthenticationError',
    'NetworkError',
    'ScraperError',
    'DownloadError',
    'UnsupportedFileTypeError',
]
