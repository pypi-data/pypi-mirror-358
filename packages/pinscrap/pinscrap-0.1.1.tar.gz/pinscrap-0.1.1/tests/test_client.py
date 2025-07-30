import pytest
from pathlib import Path
from pinscrap import PinScrapClient
from pinscrap.models import Pin

@pytest.fixture
def mock_pinterest_search_page(page):
    html_content = """
    <!DOCTYPE html>
    <html>
    <body>
        <div data-grid-item="true">
            <a href="/pin/12345/">
                <img src="https://i.pinimg.com/564x/image1.jpg" alt="Description for pin 1">
            </a>
        </div>
        <div data-grid-item="true">
            <a href="/pin/67890/">
                <img src="https://i.pinimg.com/564x/image2.jpg" alt="Description for pin 2">
            </a>
        </div>
    </body>
    </html>
    """
    
    page.route(
        "https://www.pinterest.com/search/pins/?q=testquery",
        lambda route: route.fulfill(
            status=200,
            content_type="text/html; charset=utf-8",
            body=html_content
        )
    )
    return page

@pytest.mark.asyncio
async def test_search_parses_pins_correctly(mock_pinterest_search_page):
    client = PinScrapClient()
    client._page = mock_pinterest_search_page
    
    results = await client._scrape_page_data()
    
    assert len(results) == 2
    assert isinstance(results[0], Pin)
    
    assert results[0].id == "12345"
    assert str(results[0].image_url) == "https://i.pinimg.com/564x/image1.jpg"
    assert results[0].description == "Description for pin 1"
    
    assert results[1].id == "67890"
    assert str(results[1].image_url) == "https://i.pinimg.com/564x/image2.jpg"
    assert results[1].description == "Description for pin 2"


@pytest.mark.slow
@pytest.mark.asyncio
async def test_real_search_integration():
    client = PinScrapClient(headless=True, scroll_limit=1)
    
    try:
        search_results = await client.search("python programming")
        
        assert search_results.pin_count > 0
        assert len(search_results.pins) > 0
        
        first_pin = search_results.pins[0]
        assert isinstance(first_pin, Pin)
        assert first_pin.id is not None
        assert str(first_pin.image_url).startswith("http")
        
    finally:
        await client.close()
        