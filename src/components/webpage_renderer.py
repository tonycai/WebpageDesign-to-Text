import os
import asyncio
import urllib.parse
from datetime import datetime
from typing import Dict, Any, Optional
from pyppeteer import launch

class WebpageRenderer:
    async def capture_screenshot(self, url: str, output_path: str = None, config: Dict[str, Any] = None) -> Dict[str, Any]:
        # Parse the configuration settings
        if config is None:
            config = {}
        
        wait_time = config.get('wait_time', 2)
        device_type = config.get('device', 'desktop')
        viewport = config.get('viewport', {'width': 1920, 'height': 1080})
        
        # Generate output path if not provided
        if output_path is None:
            output_dir = os.path.join(os.getcwd(), 'screenshot')
            os.makedirs(output_dir, exist_ok=True)
            
            # Create a unique filename based on domain and timestamp
            domain = self._extract_domain(url)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(output_dir, f"{domain}__{timestamp}.png")
        else:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Docker-compatible launch options
        browser = await launch({
            'headless': True,
            'args': [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--single-process',
                '--disable-gpu'
            ]
        })
        
        page = await browser.newPage()
        
        try:
            # Set viewport based on configuration
            await page.setViewport({
                'width': viewport['width'],
                'height': viewport['height'],
                'deviceScaleFactor': 1,
                'isMobile': device_type.lower() == 'mobile',
                'hasTouch': device_type.lower() == 'mobile'
            })
            
            # Navigate to URL with timeout and wait until parameter
            await page.goto(url, {'waitUntil': 'networkidle0', 'timeout': 60000})
            
            # Optional wait for dynamic content
            if wait_time > 0:
                await asyncio.sleep(wait_time)
            
            # Get page dimensions for full screenshot
            page_dimensions = await page.evaluate('''() => {
                return {
                    width: document.documentElement.scrollWidth,
                    height: document.documentElement.scrollHeight
                }
            }''')
            
            # Update viewport to match page dimensions for full screenshot
            await page.setViewport({
                'width': page_dimensions['width'],
                'height': page_dimensions['height']
            })
            
            # Take screenshot
            await page.screenshot({'path': output_path, 'fullPage': True})
            
            # Collect page metadata
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
            
            # Collect additional page information
            page_info = await page.evaluate('''() => {
                return {
                    domain: window.location.hostname,
                    url: window.location.href,
                    favicon: document.querySelector('link[rel="icon"]')?.href || null,
                    language: document.documentElement.lang || 'en'
                }
            }''')
            
            return {
                'screenshot_path': output_path,
                'page_title': page_title,
                'page_dimensions': page_dimensions,
                'page_metadata': page_metadata,
                'page_info': page_info
            }
        finally:
            await browser.close()
    
    def render_webpage(self, url: str, output_path: str = None, config: Dict[str, Any] = None) -> Dict[str, Any]:
        return asyncio.get_event_loop().run_until_complete(
            self.capture_screenshot(url, output_path, config)
        )
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain name from URL, removing www. if present."""
        try:
            parsed_url = urllib.parse.urlparse(url)
            domain = parsed_url.netloc or parsed_url.path
            # Remove www. if present
            if domain.startswith('www.'):
                domain = domain[4:]
            # Remove port if present
            if ':' in domain:
                domain = domain.split(':', 1)[0]
            return domain
        except Exception:
            # Fallback to a safe default if parsing fails
            return "webpage"