import httpx
import asyncio
from pathlib import Path
from loguru import logger

async def download_pin_image(url: str, directory: Path = Path("pinscrap_downloads")):
    try:
        directory.mkdir(parents=True, exist_ok=True)
        
        filename = url.split("/")[-1].split("?")[0]
        filepath = directory / filename

        async with httpx.AsyncClient(http2=True, follow_redirects=True) as client:
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()

            with open(filepath, 'wb') as file:
                file.write(response.content)
            
            logger.success(f"Imagen descargada exitosamente en {filepath}")
            return str(filepath)
            
    except httpx.HTTPStatusError as e:
        logger.error(f"Error HTTP {e.response.status_code} al descargar {url}")
    except Exception as e:
        logger.error(f"Fallo inesperado al descargar {url}: {e}")
    
    return None
    