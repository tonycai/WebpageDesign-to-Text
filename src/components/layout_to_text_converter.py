from typing import Dict, Any, List
import json

class LayoutToTextConverter:
    def __init__(self):
        pass
    
    def convert_to_text(self, 
                       ui_analysis: Dict[str, Any], 
                       ocr_results: Dict[str, Any], 
                       page_info: Dict[str, Any]) -> Dict[str, Any]:
        
        # Extract key information
        ui_elements = ui_analysis.get('ui_elements', [])
        color_palette = ui_analysis.get('color_palette', [])
        layout_pattern = ui_analysis.get('layout_pattern', 'unknown')
        image_dimensions = ui_analysis.get('image_dimensions', {'width': 0, 'height': 0})
        
        full_ocr_text = ocr_results.get('full_text', '')
        text_blocks = ocr_results.get('text_blocks', [])
        
        page_title = page_info.get('page_title', '')
        page_metadata = page_info.get('page_metadata', {})
        
        # Create structured description
        structured_description = {
            'page_title': page_title,
            'layout_pattern': layout_pattern,
            'color_palette': self._describe_color_palette(color_palette),
            'ui_elements': self._describe_ui_elements(ui_elements, text_blocks, image_dimensions),
            'metadata': self._describe_metadata(page_metadata)
        }
        
        # Generate human-readable textual description
        textual_description = self._generate_textual_description(structured_description)
        
        return {
            'structured_description': structured_description,
            'textual_description': textual_description,
            'json_output': json.dumps(structured_description, indent=2)
        }
    
    def _describe_color_palette(self, color_palette: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not color_palette:
            return {'description': 'No color information available'}
        
        primary_colors = []
        for color in color_palette:
            color_desc = {
                'hex': color.get('hex', '#000000'),
                'percentage': round(color.get('percentage', 0), 2)
            }
            primary_colors.append(color_desc)
        
        return {
            'primary_colors': primary_colors,
            'description': f'The page primarily uses {len(primary_colors)} colors: ' + 
                          ', '.join([f"{color['hex']} ({color['percentage']}%)" for color in primary_colors[:3]])
        }
    
    def _describe_ui_elements(self, 
                             ui_elements: List[Dict[str, Any]], 
                             text_blocks: List[Dict[str, Any]], 
                             image_dimensions: Dict[str, int]) -> List[Dict[str, Any]]:
        
        if not ui_elements:
            return [{'type': 'unknown', 'description': 'No UI elements detected'}]
        
        width, height = image_dimensions.get('width', 0), image_dimensions.get('height', 0)
        described_elements = []
        
        for element in ui_elements:
            element_type = element.get('type', 'unknown')
            bbox = element.get('bounding_box', [])
            
            # Skip if bounding box is invalid
            if not bbox or len(bbox) < 4:
                continue
            
            # Calculate relative position
            left, top = bbox[0]
            right, bottom = bbox[2]
            
            rel_left = left / width if width else 0
            rel_top = top / height if height else 0
            rel_right = right / width if width else 0
            rel_bottom = bottom / height if height else 0
            
            # Determine position description
            position = self._get_position_description(rel_left, rel_top, rel_right, rel_bottom)
            
            # Find text within this UI element
            element_text = self._find_text_in_element(bbox, text_blocks)
            
            described_elements.append({
                'type': element_type,
                'position': position,
                'size_percentage': {
                    'width': round((rel_right - rel_left) * 100, 1),
                    'height': round((rel_bottom - rel_top) * 100, 1)
                },
                'text_content': element_text,
                'description': self._generate_element_description(element_type, position, element_text)
            })
        
        return described_elements
    
    def _find_text_in_element(self, 
                             element_bbox: List[tuple], 
                             text_blocks: List[Dict[str, Any]]) -> str:
        
        if not element_bbox or not text_blocks:
            return ""
        
        # Extract element coordinates
        e_left, e_top = element_bbox[0]
        e_right, e_bottom = element_bbox[2]
        
        contained_text = []
        
        for block in text_blocks:
            text = block.get('text', '')
            block_bbox = block.get('bounding_box', [])
            
            if not block_bbox or len(block_bbox) < 4:
                continue
            
            # Extract text block coordinates
            t_left, t_top = block_bbox[0]
            t_right, t_bottom = block_bbox[2]
            
            # Check if text block is mostly inside the element
            if (e_left <= t_left and t_right <= e_right and 
                e_top <= t_top and t_bottom <= e_bottom):
                contained_text.append(text)
            
        return " ".join(contained_text)
    
    def _get_position_description(self, 
                                 rel_left: float, 
                                 rel_top: float, 
                                 rel_right: float, 
                                 rel_bottom: float) -> Dict[str, Any]:
        
        # Calculate center point
        center_x = (rel_left + rel_right) / 2
        center_y = (rel_top + rel_bottom) / 2
        
        # Horizontal position
        if center_x < 0.33:
            h_pos = "left"
        elif center_x >= 0.33 and center_x <= 0.66:
            h_pos = "center"
        else:
            h_pos = "right"
        
        # Vertical position
        if center_y < 0.33:
            v_pos = "top"
        elif center_y >= 0.33 and center_y <= 0.66:
            v_pos = "middle"
        else:
            v_pos = "bottom"
        
        return {
            'horizontal': h_pos,
            'vertical': v_pos,
            'description': f"{v_pos} {h_pos}"
        }
    
    def _describe_metadata(self, metadata: Dict[str, str]) -> Dict[str, Any]:
        relevant_meta = {}
        
        # Extract relevant metadata
        for key, value in metadata.items():
            # Skip empty values
            if not value:
                continue
                
            # Include common meta tags
            if key in ['description', 'keywords', 'author', 'viewport']:
                relevant_meta[key] = value
            elif 'og:' in key:  # Open Graph tags
                relevant_meta[key] = value
            elif 'twitter:' in key:  # Twitter Card tags
                relevant_meta[key] = value
        
        if not relevant_meta:
            return {'description': 'No relevant metadata available'}
        
        return {
            'tags': relevant_meta,
            'description': f"The page includes {len(relevant_meta)} metadata tags, including: " + 
                          ", ".join(list(relevant_meta.keys())[:3] if relevant_meta else [])
        }
    
    def _generate_element_description(self, 
                                     element_type: str, 
                                     position: Dict[str, Any], 
                                     text_content: str) -> str:
        
        pos_desc = position.get('description', '')
        
        if text_content:
            if len(text_content) > 100:
                text_snippet = text_content[:97] + "..."
            else:
                text_snippet = text_content
            
            return f"A {element_type} in the {pos_desc} of the page containing: '{text_snippet}'"
        else:
            return f"A {element_type} in the {pos_desc} of the page"
    
    def _generate_textual_description(self, structured_description: Dict[str, Any]) -> str:
        page_title = structured_description.get('page_title', 'Untitled Page')
        layout_pattern = structured_description.get('layout_pattern', 'unknown')
        color_palette = structured_description.get('color_palette', {})
        ui_elements = structured_description.get('ui_elements', [])
        
        # Build the description
        lines = []
        
        # Page title and layout
        lines.append(f"# {page_title}")
        lines.append("")
        lines.append(f"This webpage uses a {layout_pattern} design.")
        lines.append("")
        
        # Color palette
        color_desc = color_palette.get('description', 'No color information available')
        lines.append(f"## Color Palette")
        lines.append(color_desc)
        lines.append("")
        
        # UI Elements
        lines.append("## UI Elements")
        
        # Group elements by type
        element_types = {}
        for element in ui_elements:
            elem_type = element.get('type', 'unknown')
            if elem_type not in element_types:
                element_types[elem_type] = []
            element_types[elem_type].append(element)
        
        # Describe each type of element
        for elem_type, elements in element_types.items():
            lines.append(f"### {elem_type.replace('_', ' ').title()} ({len(elements)})")
            
            for i, element in enumerate(elements):
                desc = element.get('description', '')
                lines.append(f"- {desc}")
            
            lines.append("")
        
        return "\n".join(lines)