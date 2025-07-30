# PinScrap  स्क्रैप

[![PyPI version](https://badge.fury.io/py/pinscrap.svg)](https://badge.fury.io/py/pinscrap)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Una biblioteca **avanzada y asíncrona** para extraer datos de Pinterest sin necesidad de una API oficial. Diseñada para ser rápida, confiable y fácil de usar.

### ⚠️ Advertencia Importante

Este proyecto realiza scraping en Pinterest. El uso de esta biblioteca debe cumplir con los Términos de Servicio de Pinterest y las leyes de propiedad intelectual aplicables. Úsala de manera responsable y bajo tu propio riesgo.

---

## 🚀 Características Principales

* **Búsqueda Avanzada**: Encuentra pines por palabras clave con soporte para paginación.
* **Información Detallada**: Obtén metadatos completos de cualquier pin.
* **Descarga de Imágenes**: Descarga imágenes en alta calidad de forma asíncrona.
* **Perfiles de Usuario**: Explora los pines de cualquier usuario de Pinterest.
* **Tipado Estático**: Mejor experiencia de desarrollo con tipos anotados.
* **Asíncrono**: Máximo rendimiento con `asyncio` y `Playwright`.
* **Robusto**: Manejo de errores y reintentos automáticos.

## 📦 Instalación

```bash
pip install pinscrap
```

Instala los navegadores necesarios para Playwright:
```bash
playwright install
```

## 🚀 Ejemplos Rápidos

### Búsqueda de Pines

```python
import asyncio
from pinscrap import PinScrapClient

async def main():
    client = PinScrapClient(headless=True)
    try:
        # Buscar pines
        result = await client.search("programación python", limit=5)
        
        print(f"Encontrados {result.pin_count} pines:")
        for i, pin in enumerate(result.pins, 1):
            print(f"\n{i}. {pin.description or 'Sin descripción'}")
            print(f"   URL: {pin.image_url}")
            if pin.creator:
                print(f"   Por: {pin.creator.username}")
    finally:
        await client.close()

asyncio.run(main())
```

### Descargar Imágenes

```python
import asyncio
from pathlib import Path
from pinscrap import PinScrapClient, batch_download

async def main():
    client = PinScrapClient(headless=True)
    try:
        # Buscar pines
        result = await client.search("gatitos", limit=3)
        
        # Descargar imágenes
        download_dir = Path("descargas_gatitos")
        download_dir.mkdir(exist_ok=True)
        
        urls = [pin.image_url for pin in result.pins if pin.image_url]
        downloaded = await batch_download(urls, directory=download_dir)
        
        print(f"\n¡Descargadas {len(downloaded)} imágenes en '{download_dir}/'!")
    finally:
        await client.close()

asyncio.run(main())
```

### Obtener Información de un Pin

```python
import asyncio
from pinscrap import PinScrapClient

async def main():
    client = PinScrapClient(headless=True)
    try:
        pin = await client.get_pin_info("https://www.pinterest.com/pin/1234567890/")
        print(f"Descripción: {pin.description}")
        print(f"Imagen: {pin.image_url}")
        if pin.creator:
            print(f"Creador: {pin.creator.username}")
    finally:
        await client.close()

asyncio.run(main())
```

## 📚 Documentación Completa

### Clase PinScrapClient

#### Métodos Principales

- `search(query: str, limit: int = 50) -> SearchResult`
  - Busca pines en Pinterest.
  - `query`: Término de búsqueda.
  - `limit`: Número máximo de pines a devolver.

- `get_pin_info(pin_url: str) -> Optional[Pin]`
  - Obtiene información detallada de un pin.
  - `pin_url`: URL completa del pin.

- `get_user_pins(username: str, limit: int = 50) -> List[Pin]`
  - Obtiene los pines de un usuario.
  - `username`: Nombre de usuario en Pinterest.
  - `limit`: Número máximo de pines a devolver.

### Funciones de Utilidad

- `download_pin_image(url, directory, filename=None)`
  - Descarga una imagen de un pin.

- `batch_download(urls, directory, max_concurrent=5)`
  - Descarga múltiples imágenes de forma concurrente.

## 🛠️ Manejo de Errores

La biblioteca incluye excepciones específicas para un mejor manejo de errores:

- `PinScrapException`: Clase base para todos los errores.
- `PinterestInteractionException`: Error al interactuar con Pinterest.
- `PinNotFoundError`: No se encontró el pin solicitado.
- `InvalidPinUrlError`: URL de pin inválida.
- `RateLimitExceededError`: Límite de solicitudes excedido.
- `NetworkError`: Error de red.

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Por favor, lee nuestras pautas de contribución antes de enviar un pull request.

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más información.

## 🌟 Desarrollado por Patchyn

Este proyecto es mantenido por el equipo de Patchyn. ¡Gracias por usarlo! ❤️

[![GitHub stats](https://github-readme-stats.vercel.app/api/pin/?username=patchyn&repo=pinscrap&theme=dark)](https://github.com/patchyn/pinscrap)

## 📊 Estadísticas

![GitHub Stats](https://github-readme-stats.vercel.app/api?username=patchyn&show_icons=true&theme=dark)
![Top Langs](https://github-readme-stats.vercel.app/api/top-langs/?username=patchyn&layout=compact&theme=dark)

---

<img src="https://i.postimg.cc/Gm2KTWSY/Produced-By-a-Human-Not-By-AI-Badge-black-2x.png" width="150">