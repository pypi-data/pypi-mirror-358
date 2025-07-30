import asyncio
from pinscrap import PinScrapClient, download_image
from loguru import logger

async def main():
    client = PinScrapClient(headless=False, scroll_limit=3)

    try:
        pins = await client.search("cyberpunk city")
        
        if not pins:
            logger.warning("No se encontraron pines.")
            return

        logger.info(f"Primer pin encontrado: ID={pins[0].id}, Desc={pins[0].description}")
        
        tasks = []
        for pin in pins[:5]: 
            tasks.append(download_image(pin.image_url))
        
        await asyncio.gather(*tasks)

    except Exception as e:
        logger.error(f"Ocurrió un error en la ejecución: {e}")

if __name__ == "__main__":
    asyncio.run(main())