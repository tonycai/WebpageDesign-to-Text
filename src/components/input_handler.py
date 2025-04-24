from urllib.parse import urlparse

class InputHandler:
    def validate_url(self, url: str) -> bool:
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def process_url(self, url: str) -> str:
        if not self.validate_url(url):
            raise ValueError("Invalid URL provided")
        
        return url