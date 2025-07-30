import os
import re
import uuid
import hashlib
import asyncio
import aiohttp
import aiofiles
from pathlib import Path
from typing import Optional, Union, Dict, Any, List
from urllib.parse import urlparse, unquote
from loguru import logger

# Tamaño del buffer para descargas
CHUNK_SIZE = 65536  # 64KB

# Tipos MIME de imágenes soportadas
SUPPORTED_IMAGE_TYPES = {
    'image/jpeg': '.jpg',
    'image/png': '.png',
    'image/webp': '.webp',
    'image/gif': '.gif',
}

# Headers por defecto para las peticiones HTTP
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.pinterest.com/',
    'DNT': '1',
}

class DownloadError(Exception):
    """Excepción para errores durante la descarga de archivos."""
    pass

class UnsupportedFileTypeError(DownloadError):
    """Se produce cuando se intenta descargar un tipo de archivo no soportado."""
    pass

def generate_unique_filename(url: str, content_type: Optional[str] = None) -> str:
    """
    Genera un nombre de archivo único basado en la URL y el tipo de contenido.
    
    Args:
        url: URL de la imagen
        content_type: Tipo MIME del contenido (opcional)
        
    Returns:
        str: Nombre de archivo único
    """
    # Extraer el nombre del archivo de la URL
    parsed_url = urlparse(url)
    path = unquote(parsed_url.path)
    filename = os.path.basename(path).split('?')[0]
    
    # Si no hay extensión y tenemos el tipo de contenido, usarla
    if '.' not in filename and content_type in SUPPORTED_IMAGE_TYPES:
        ext = SUPPORTED_IMAGE_TYPES[content_type]
        filename = f"{filename}{ext}" if not filename.endswith(ext) else filename
    
    # Si aún no hay extensión, usar .jpg por defecto
    if '.' not in filename:
        filename = f"{filename}.jpg"
    
    # Generar un hash único para evitar colisiones
    name_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    name, ext = os.path.splitext(filename)
    
    return f"{name}_{name_hash}{ext}"

async def download_file(
    url: str, 
    directory: Union[str, Path] = Path("pinscrap_downloads"),
    filename: Optional[str] = None,
    session: Optional[aiohttp.ClientSession] = None,
    headers: Optional[Dict[str, str]] = None,
    verify_ssl: bool = True
) -> Optional[Path]:
    """
    Descarga un archivo desde una URL y lo guarda en el directorio especificado.
    
    Args:
        url: URL del archivo a descargar
        directory: Directorio donde se guardará el archivo
        filename: Nombre del archivo (opcional, se generará si no se proporciona)
        session: Sesión de aiohttp (opcional)
        headers: Headers HTTP personalizados (opcional)
        verify_ssl: Verificar certificados SSL
        
    Returns:
        Path: Ruta al archivo descargado o None si falla
    """
    # Convertir el directorio a Path si es necesario
    if isinstance(directory, str):
        directory = Path(directory)
    
    # Asegurarse de que el directorio existe
    directory.mkdir(parents=True, exist_ok=True)
    
    # Usar los headers por defecto si no se proporcionan
    if headers is None:
        headers = DEFAULT_HEADERS
    
    # Bandera para indicar si debemos cerrar la sesión al final
    close_session = False
    
    try:
        # Crear una nueva sesión si no se proporciona una
        if session is None:
            timeout = aiohttp.ClientTimeout(total=60)
            session = aiohttp.ClientSession(headers=headers, timeout=timeout)
            close_session = True
        
        # Realizar la petición HEAD para obtener información del archivo
        async with await session.head(url, allow_redirects=True, ssl=verify_ssl) as response:
            if response.status != 200:
                logger.error(f"Error HTTP {response.status} al acceder a {url}")
                return None
            
            # Obtener el tipo de contenido
            content_type = response.headers.get('Content-Type', '').split(';')[0].strip().lower()
            
            # Verificar si el tipo de archivo es soportado
            if content_type and content_type not in SUPPORTED_IMAGE_TYPES:
                raise UnsupportedFileTypeError(f"Tipo de archivo no soportado: {content_type}")
            
            # Generar un nombre de archivo si no se proporciona uno
            if not filename:
                content_disposition = response.headers.get('Content-Disposition', '')
                if 'filename=' in content_disposition:
                    # Extraer el nombre del archivo del encabezado Content-Disposition
                    filename = re.findall('filename="?(.+)"?', content_disposition)[0]
                else:
                    # Generar un nombre basado en la URL y el tipo de contenido
                    filename = generate_unique_filename(url, content_type)
            
            # Asegurarse de que el nombre del archivo sea seguro
            filename = "".join(c if c.isalnum() or c in '._- ' else '_' for c in filename)
            filepath = directory / filename
            
            # Si el archivo ya existe, devolver su ruta
            if filepath.exists():
                logger.info(f"El archivo ya existe: {filepath}")
                return filepath
            
            # Descargar el archivo en bloques
            async with session.get(url, ssl=verify_ssl) as download_response:
                if download_response.status != 200:
                    raise DownloadError(f"Error HTTP {download_response.status} al descargar {url}")
                
                # Escribir el archivo en bloques
                async with aiofiles.open(filepath, 'wb') as f:
                    async for chunk in download_response.content.iter_chunked(CHUNK_SIZE):
                        await f.write(chunk)
                
                logger.success(f"Archivo descargado exitosamente en {filepath}")
                return filepath
                
    except aiohttp.ClientError as e:
        logger.error(f"Error de red al descargar {url}: {e}")
        raise DownloadError(f"Error de red: {e}") from e
    except Exception as e:
        logger.error(f"Error inesperado al descargar {url}: {e}")
        raise DownloadError(f"Error inesperado: {e}") from e
    finally:
        # Cerrar la sesión si la creamos nosotros
        if close_session and session and not session.closed:
            await session.close()

async def download_pin_image(
    url: str, 
    directory: Union[str, Path] = Path("pinscrap_downloads"),
    filename: Optional[str] = None,
    session: Optional[aiohttp.ClientSession] = None
) -> Optional[Path]:
    """
    Descarga una imagen de un pin de Pinterest.
    
    Args:
        url: URL de la imagen del pin
        directory: Directorio donde se guardará la imagen
        filename: Nombre del archivo (opcional)
        session: Sesión de aiohttp (opcional)
        
    Returns:
        Path: Ruta a la imagen descargada o None si falla
    """
    try:
        return await download_file(url, directory, filename, session)
    except Exception as e:
        logger.error(f"Error al descargar la imagen del pin: {e}")
        return None

async def batch_download(
    urls: List[str], 
    directory: Union[str, Path] = Path("pinscrap_downloads"),
    max_concurrent: int = 5
) -> List[Path]:
    """
    Descarga múltiples archivos de forma concurrente.
    
    Args:
        urls: Lista de URLs a descargar
        directory: Directorio donde se guardarán los archivos
        max_concurrent: Número máximo de descargas concurrentes
        
    Returns:
        List[Path]: Lista de rutas a los archivos descargados
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    downloaded_files = []
    
    async def download_with_semaphore(url):
        async with semaphore:
            try:
                filepath = await download_pin_image(url, directory)
                if filepath:
                    downloaded_files.append(filepath)
                return filepath
            except Exception as e:
                logger.error(f"Error al descargar {url}: {e}")
                return None
    
    # Ejecutar las descargas de forma concurrente
    tasks = [download_with_semaphore(url) for url in urls]
    await asyncio.gather(*tasks, return_exceptions=True)
    
    return downloaded_files