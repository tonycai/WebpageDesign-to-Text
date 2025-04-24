from typing import Dict, Any, List
from google.cloud import vision
import io

class OCRExtractor:
    def __init__(self, credentials_path: str = None):
        self.client = vision.ImageAnnotatorClient.from_service_account_json(
            credentials_path) if credentials_path else vision.ImageAnnotatorClient()
    
    def extract_text(self, image_path: str) -> Dict[str, Any]:
        with io.open(image_path, 'rb') as image_file:
            content = image_file.read()
        
        image = vision.Image(content=content)
        
        response = self.client.text_detection(image=image)
        
        if response.error.message:
            raise Exception(f"Error in OCR text extraction: {response.error.message}")
            
        texts = response.text_annotations
        
        # The first entry contains the entire extracted text
        full_text = texts[0].description if texts else ""
        
        # Get all text blocks with their bounding boxes
        text_blocks = []
        for text in texts[1:]:  # Skip the first one as it's the full text
            vertices = [(vertex.x, vertex.y) for vertex in text.bounding_poly.vertices]
            text_blocks.append({
                'text': text.description,
                'bounding_box': vertices
            })
        
        return {
            'full_text': full_text,
            'text_blocks': text_blocks
        }
    
    def detect_labels(self, image_path: str) -> List[str]:
        with io.open(image_path, 'rb') as image_file:
            content = image_file.read()
        
        image = vision.Image(content=content)
        
        response = self.client.label_detection(image=image)
        
        if response.error.message:
            raise Exception(f"Error in label detection: {response.error.message}")
            
        return [label.description for label in response.label_annotations]