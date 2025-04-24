#!/usr/bin/env python3

import os
import sys
import argparse
import yaml
from typing import Dict, Any, Optional

from src.components.input_handler import InputHandler
from src.components.webpage_renderer import WebpageRenderer
from src.components.ocr_extractor import OCRExtractor
from src.components.gui_analyzer import GUIAnalyzer
from src.components.layout_to_text_converter import LayoutToTextConverter
from src.components.llm_integration import LLMIntegration
from src.components.output_handler import OutputHandler

def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from a YAML file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        print(f"Error loading config file: {e}")
        return {}

def process_webpage(url: str, 
                   config: Dict[str, Any], 
                   output_dir: Optional[str] = None,
                   use_llm: bool = False,
                   analysis_type: str = "general",
                   custom_prompt: Optional[str] = None) -> Dict[str, Any]:
    """
    Process a webpage and convert it to textual description.
    
    Args:
        url: The URL of the webpage to process
        config: Configuration dictionary
        output_dir: Directory to save output files
        use_llm: Whether to use LLM for analysis
        analysis_type: Type of LLM analysis to perform
        custom_prompt: Custom prompt for LLM analysis
    
    Returns:
        Dictionary containing processing results
    """
    try:
        # Initialize components
        input_handler = InputHandler()
        webpage_renderer = WebpageRenderer()
        
        # Get OCR credentials from config
        ocr_credentials = config.get('google_cloud_credentials', None)
        ocr_extractor = OCRExtractor(credentials_path=ocr_credentials)
        
        gui_analyzer = GUIAnalyzer()
        layout_converter = LayoutToTextConverter()
        output_handler = OutputHandler(output_dir=output_dir)
        
        # Process URL
        processed_url = input_handler.process_url(url)
        
        # Render webpage and capture screenshot
        print(f"Rendering webpage: {url}")
        render_results = webpage_renderer.render_webpage(processed_url)
        screenshot_path = render_results['screenshot_path']
        print(f"Screenshot captured: {screenshot_path}")
        
        # Extract text with OCR
        print("Extracting text using OCR...")
        ocr_results = ocr_extractor.extract_text(screenshot_path)
        print(f"Extracted {len(ocr_results.get('text_blocks', []))} text blocks")
        
        # Analyze GUI elements
        print("Analyzing GUI elements...")
        gui_results = gui_analyzer.analyze_screenshot(screenshot_path)
        print(f"Detected {len(gui_results.get('ui_elements', []))} UI elements")
        
        # Convert layout to text
        print("Converting layout to textual description...")
        conversion_results = layout_converter.convert_to_text(
            ui_analysis=gui_results,
            ocr_results=ocr_results,
            page_info=render_results
        )
        
        # Analyze with LLM if requested
        llm_results = None
        if use_llm:
            if 'anthropic_api_key' in config:
                llm_integration = LLMIntegration(api_key=config['anthropic_api_key'])
                print(f"Analyzing textual description with Claude ({analysis_type} analysis)...")
                llm_results = llm_integration.analyze_webpage_description(
                    textual_description=conversion_results['textual_description'],
                    analysis_type=analysis_type,
                    custom_prompt=custom_prompt
                )
            else:
                print("Warning: Anthropic API key not found in config, skipping LLM analysis")
        
        # Prepare final results
        results = {
            'url': url,
            'screenshot_path': screenshot_path,
            'textual_description': conversion_results['textual_description'],
            'structured_description': conversion_results['structured_description'],
            'json_output': conversion_results['json_output']
        }
        
        if llm_results:
            results['llm_analysis'] = llm_results
        
        # Save results
        saved_files = output_handler.save_results(results, url)
        results['saved_files'] = saved_files
        
        # Display results
        output_handler.display_results(results)
        
        return results
    
    except Exception as e:
        print(f"Error processing webpage: {e}")
        return {'error': str(e)}

def main():
    parser = argparse.ArgumentParser(description="Convert webpage designs to textual descriptions")
    parser.add_argument("url", help="URL of the webpage to analyze")
    parser.add_argument("-c", "--config", default="config.yaml", help="Path to configuration file")
    parser.add_argument("-o", "--output", help="Output directory")
    parser.add_argument("-l", "--llm", action="store_true", help="Use LLM for analysis")
    parser.add_argument("-a", "--analysis", default="general", 
                        choices=["general", "ux", "accessibility", "structure"],
                        help="Type of LLM analysis to perform")
    parser.add_argument("-p", "--prompt", help="Custom prompt for LLM")
    
    args = parser.parse_args()
    
    # Load configuration
    config_path = args.config
    if not os.path.exists(config_path):
        print(f"Config file not found: {config_path}")
        config = {}
    else:
        config = load_config(config_path)
    
    # Process webpage
    process_webpage(
        url=args.url,
        config=config,
        output_dir=args.output,
        use_llm=args.llm,
        analysis_type=args.analysis,
        custom_prompt=args.prompt
    )

if __name__ == "__main__":
    main()