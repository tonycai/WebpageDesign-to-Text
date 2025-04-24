import os
import asyncio
from typing import Dict, Any
from pyppeteer import launch

class WebpageRenderer:
    async def capture_screenshot(self, url: str, output_path: str = None) -> Dict[str, Any]:
        if output_path is None:
            output_dir = os.path.join(os.getcwd(), 'output')
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, 'screenshot.png')
        
        browser = await launch()
        page = await browser.newPage()
        
        try:
            await page.goto(url, {'waitUntil': 'networkidle0', 'timeout': 60000})
            
            page_dimensions = await page.evaluate('''() => {
                return {
                    width: document.documentElement.scrollWidth,
                    height: document.documentElement.scrollHeight
                }
            }''')
            
            await page.setViewport({
                'width': page_dimensions['width'],
                'height': page_dimensions['height']
            })
            
            await page.screenshot({'path': output_path, 'fullPage': True})
            
            page_title = await page.title()
            page_metadata = await page.evaluate('''() => {
                const metaTags = {};
                document.querySelectorAll('meta').forEach(meta => {
                    if (meta.name) {
                        metaTags[meta.name] = meta.content;
                    } else if (meta.property) {
                        metaTags[meta.property] = meta.content;
                    }
                });
                return metaTags;
            }''')
            
            return {
                'screenshot_path': output_path,
                'page_title': page_title,
                'page_dimensions': page_dimensions,
                'page_metadata': page_metadata
            }
        finally:
            await browser.close()
    
    def render_webpage(self, url: str, output_path: str = None) -> Dict[str, Any]:
        return asyncio.get_event_loop().run_until_complete(
            self.capture_screenshot(url, output_path)
        )