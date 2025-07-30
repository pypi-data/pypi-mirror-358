import asyncio
from playwright.async_api import async_playwright
from typing import List
from loguru import logger

from .models import Pin
from .exceptions import PinterestInteractionException

class PinScrapClient:

    def __init__(self, headless: bool = True, scroll_limit: int = 5):
        self.headless = headless
        self.scroll_limit = scroll_limit
        self.base_url = "https://www.pinterest.com"

    async def search(self, query: str) -> List[Pin]:
        pins_data = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            
            search_url = f"{self.base_url}/search/pins/?q={query}"
            logger.info(f"Navegando a: {search_url}")

            try:
                await page.goto(search_url, wait_until="load", timeout=60000)
                await page.wait_for_selector('div[data-grid-item="true"]', timeout=30000)
            except Exception as e:
                await browser.close()
                raise PinterestInteractionException(f"No se pudo cargar la página de búsqueda o encontrar el contenedor de pines: {e}")

            logger.info("Página cargada. Empezando scroll para cargar más pines...")

            for _ in range(self.scroll_limit):
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(2)

            logger.info("Scroll finalizado. Extrayendo datos de los pines...")

            pin_elements = await page.locator('div[data-grid-item="true"]').all()
            
            for element in pin_elements:
                try:
                    img_locator = element.locator('img')
                    pin_id_raw = await element.locator('a').first.get_attribute('href')
                    
                    pin_id = pin_id_raw.split('/')[2] if pin_id_raw and len(pin_id_raw.split('/')) > 2 else "unknown"
                    image_url = await img_locator.get_attribute('src')
                    description = await img_locator.get_attribute('alt')

                    if image_url and image_url.startswith('http'):
                        pin_model = Pin(
                            id=pin_id,
                            image_url=image_url,
                            description=description
                        )
                        pins_data.append(pin_model)
                except Exception as e:
                    logger.warning(f"No se pudo procesar un pin. Error: {e}")

            await browser.close()
            logger.success(f"Se encontraron y procesaron {len(pins_data)} pines para la búsqueda '{query}'.")
            return pins_data
            