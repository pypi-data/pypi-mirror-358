import asyncio
import random
import json
from typing import List, Optional, Dict, Any, Union
from pathlib import Path
from urllib.parse import urljoin, urlparse, parse_qs
from dataclasses import asdict

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from loguru import logger

from .models import Pin, SearchResult, PinCreator
from .exceptions import (
    PinterestInteractionException,
    PinNotFoundError,
    InvalidPinUrlError,
    RateLimitExceededError
)

# User agents para rotar y evitar bloqueos
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.61"
]

class PinScrapClient:

    def __init__(self, headless: bool = True, scroll_limit: int = 10, timeout: int = 30000):
        """
        Inicializa el cliente de PinScrap.
        
        Args:
            headless (bool): Si es True, el navegador se ejecutará en modo sin cabeza.
            scroll_limit (int): Número de veces que se hará scroll para cargar más pines.
            timeout (int): Tiempo de espera en milisegundos para las operaciones de Playwright.
        """
        self.headless = headless
        self.scroll_limit = scroll_limit
        self.timeout = timeout
        self.base_url = "https://www.pinterest.com"
        self.session = None
        self._browser = None
        self._context = None
        self._page = None

    async def _get_random_user_agent(self) -> str:
        """Devuelve un user agent aleatorio de la lista."""
        return random.choice(USER_AGENTS)

    async def _init_browser(self):
        """Inicializa el navegador y el contexto."""
        if not self._browser or self._browser.is_connected() is False:
            self._browser = await async_playwright().start()
            self._context = await self._browser.chromium.launch(
                headless=self.headless,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            
        if not self._page or self._page.is_closed():
            self._page = await self._context.new_context(
                user_agent=await self._get_random_user_agent(),
                viewport={'width': 1920, 'height': 1080},
                locale='en-US',
                timezone_id='America/New_York',
                extra_http_headers={
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                }
            ).new_page()
            await self._page.set_extra_http_headers({
                'DNT': '1',
                'Upgrade-Insecure-Requests': '1'
            })

    async def close(self):
        """Cierra el navegador y libera recursos."""
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.stop()
        self._page = None
        self._context = None
        self._browser = None

    async def _scroll_page(self, scroll_limit: int):
        """Realiza scroll en la página para cargar más contenido."""
        last_height = 0
        scroll_attempts = 0
        
        while scroll_attempts < scroll_limit:
            # Scroll hacia abajo
            await self._page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            
            # Esperar a que cargue el contenido
            await asyncio.sleep(random.uniform(1.5, 3.0))
            
            # Calcular nueva altura y verificar si hay más contenido
            new_height = await self._page.evaluate('document.body.scrollHeight')
            if new_height == last_height:
                scroll_attempts += 1
                continue
                
            last_height = new_height
            scroll_attempts = 0
            
            # Espera aleatoria entre scrolls
            await asyncio.sleep(random.uniform(0.5, 1.5))

    async def search(self, query: str, limit: int = 50) -> SearchResult:
        """
        Busca pines en Pinterest basado en una consulta.
        
        Args:
            query (str): Término de búsqueda.
            limit (int): Número máximo de pines a devolver.
            
        Returns:
            SearchResult: Objeto con los resultados de la búsqueda.
            
        Raises:
            PinterestInteractionException: Si hay un error al interactuar con Pinterest.
        """
        await self._init_browser()
        pins_data = []
        search_url = f"{self.base_url}/search/pins/?q={query.replace(' ', '+')}"
        
        logger.info(f"Iniciando búsqueda: {query}")
        
        try:
            # Navegar a la URL de búsqueda
            await self._page.goto(
                search_url, 
                wait_until="domcontentloaded", 
                timeout=self.timeout
            )
            
            # Esperar a que los resultados se carguen
            try:
                await self._page.wait_for_selector('div[data-test-id="pin"]', timeout=10000)
            except PlaywrightTimeoutError:
                logger.warning("No se encontraron resultados o la página tardó demasiado en cargar")
                return SearchResult(query=query, pin_count=0, pins=[])
            
            # Hacer scroll para cargar más pines
            await self._scroll_page(self.scroll_limit)
            
            # Extraer información de los pines
            pin_elements = await self._page.locator('div[data-test-id="pin"]').all()
            logger.info(f"Encontrados {len(pin_elements)} pines")
            
            for element in pin_elements[:limit]:
                try:
                    # Obtener datos básicos del pin
                    pin_data = {}
                    
                    # Obtener URL de la imagen
                    img_element = await element.query_selector('img')
                    if img_element:
                        pin_data['image_url'] = await img_element.get_attribute('src')
                        pin_data['description'] = await img_element.get_attribute('alt') or ''
                    
                    # Obtener enlace del pin
                    link_element = await element.query_selector('a')
                    if link_element:
                        pin_href = await link_element.get_attribute('href')
                        if pin_href:
                            pin_data['id'] = pin_href.split('/')[2] if len(pin_href.split('/')) > 2 else "unknown"
                            pin_data['link'] = urljoin(self.base_url, pin_href)
                    
                    # Obtener información del creador si está disponible
                    creator_element = await element.query_selector('[data-test-id="attribution"]')
                    if creator_element:
                        creator_name = await creator_element.text_content()
                        creator_link = await creator_element.get_attribute('href')
                        pin_data['creator'] = {
                            'username': creator_name.strip() if creator_name else 'unknown',
                            'profile_url': urljoin(self.base_url, creator_link) if creator_link else None
                        }
                    
                    # Crear objeto Pin si tenemos suficiente información
                    if 'id' in pin_data and 'image_url' in pin_data:
                        pins_data.append(Pin(**pin_data))
                        
                except Exception as e:
                    logger.warning(f"Error al procesar un pin: {str(e)}")
                    continue
            
            logger.success(f"Búsqueda completada. Encontrados {len(pins_data)} pines para '{query}'")
            return SearchResult(
                query=query,
                pin_count=len(pins_data),
                pins=pins_data
            )
            
        except Exception as e:
            error_msg = f"Error durante la búsqueda: {str(e)}"
            logger.error(error_msg)
            raise PinterestInteractionException(error_msg) from e
        
    async def get_pin_info(self, pin_url: str) -> Optional[Pin]:
        """
        Obtiene información detallada de un pin específico.
        
        Args:
            pin_url (str): URL del pin.
            
        Returns:
            Optional[Pin]: Objeto Pin con la información del pin, o None si no se pudo obtener.
            
        Raises:
            InvalidPinUrlError: Si la URL del pin no es válida.
            PinterestInteractionException: Si hay un error al interactuar con Pinterest.
        """
        if not pin_url or 'pinterest.com/pin/' not in pin_url:
            raise InvalidPinUrlError("URL de pin no válida")
            
        await self._init_browser()
        
        try:
            # Navegar a la URL del pin
            await self._page.goto(
                pin_url,
                wait_until="domcontentloaded",
                timeout=self.timeout
            )
            
            # Esperar a que el contenido principal se cargue
            await self._page.wait_for_selector('div[data-test-id="pin-detail-image"]', timeout=10000)
            
            # Extraer información del pin
            pin_data = {}
            
            # Obtener ID del pin de la URL
            pin_data['id'] = pin_url.split('/')[-2] if pin_url.endswith('/') else pin_url.split('/')[-1]
            
            # Obtener URL de la imagen
            img_element = await self._page.query_selector('div[data-test-id="pin-detail-image"] img')
            if img_element:
                pin_data['image_url'] = await img_element.get_attribute('src')
                pin_data['description'] = await img_element.get_attribute('alt') or ''
            
            # Obtener información del creador
            creator_element = await self._page.query_selector('[data-test-id="attribution"]')
            if creator_element:
                creator_name = await creator_element.text_content()
                creator_link = await creator_element.get_attribute('href')
                pin_data['creator'] = PinCreator(
                    username=creator_name.strip() if creator_name else 'unknown',
                    profile_url=urljoin(self.base_url, creator_link) if creator_link else None
                )
            
            # Obtener enlace original si está disponible
            link_element = await self._page.query_selector('a[data-test-id="attribution-link"]')
            if link_element:
                pin_data['link'] = await link_element.get_attribute('href')
            
            return Pin(**pin_data)
            
        except PlaywrightTimeoutError as e:
            raise PinterestInteractionException("Tiempo de espera agotado al cargar el pin") from e
        except Exception as e:
            error_msg = f"Error al obtener información del pin: {str(e)}"
            logger.error(error_msg)
            raise PinterestInteractionException(error_msg) from e

    async def get_user_pins(self, username: str, limit: int = 50) -> List[Pin]:
        """
        Obtiene los pines de un usuario específico.
        
        Args:
            username (str): Nombre de usuario de Pinterest.
            limit (int): Número máximo de pines a devolver.
            
        Returns:
            List[Pin]: Lista de pines del usuario.
        """
        await self._init_browser()
        user_url = f"{self.base_url}/{username}/pins/"
        pins = []
        
        try:
            # Navegar al perfil del usuario
            await self._page.goto(
                user_url,
                wait_until="domcontentloaded",
                timeout=self.timeout
            )
            
            # Esperar a que los pines se carguen
            try:
                await self._page.wait_for_selector('div[data-test-id="pin"]', timeout=10000)
            except PlaywrightTimeoutError:
                logger.warning("No se encontraron pines para este usuario")
                return []
            
            # Hacer scroll para cargar más pines
            await self._scroll_page(self.scroll_limit)
            
            # Extraer información de los pines
            pin_elements = await self._page.locator('div[data-test-id="pin"]').all()
            logger.info(f"Encontrados {len(pin_elements)} pines para el usuario {username}")
            
            for element in pin_elements[:limit]:
                try:
                    # Obtener datos básicos del pin
                    pin_data = {}
                    
                    # Obtener URL de la imagen
                    img_element = await element.query_selector('img')
                    if img_element:
                        pin_data['image_url'] = await img_element.get_attribute('src')
                        pin_data['description'] = await img_element.get_attribute('alt') or ''
                    
                    # Obtener enlace del pin
                    link_element = await element.query_selector('a')
                    if link_element:
                        pin_href = await link_element.get_attribute('href')
                        if pin_href:
                            pin_data['id'] = pin_href.split('/')[2] if len(pin_href.split('/')) > 2 else "unknown"
                            pin_data['link'] = urljoin(self.base_url, pin_href)
                    
                    # Añadir información del creador
                    pin_data['creator'] = PinCreator(
                        username=username,
                        profile_url=f"{self.base_url}/{username}/"
                    )
                    
                    # Crear objeto Pin si tenemos suficiente información
                    if 'id' in pin_data and 'image_url' in pin_data:
                        pins.append(Pin(**pin_data))
                        
                except Exception as e:
                    logger.warning(f"Error al procesar un pin: {str(e)}")
                    continue
            
            return pins
            
        except Exception as e:
            error_msg = f"Error al obtener los pines del usuario {username}: {str(e)}"
            logger.error(error_msg)
            raise PinterestInteractionException(error_msg) from e