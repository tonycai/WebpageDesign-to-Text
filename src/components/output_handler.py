import os
import json
from typing import Dict, Any
from datetime import datetime

class OutputHandler:
    def __init__(self, output_dir: str = None):
        if output_dir is None:
            output_dir = os.path.join(os.getcwd(), 'output')
        
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def save_results(self, 
                    results: Dict[str, Any], 
                    url: str, 
                    include_timestamp: bool = True) -> Dict[str, str]:
        """
        Save the analysis results to files in the output directory.
        
        Args:
            results: The results to save
            url: The URL of the webpage that was analyzed
            include_timestamp: Whether to include a timestamp in the filename
        
        Returns:
            Dictionary of file paths for each saved file
        """
        # Create a safe filename from the URL
        safe_name = self._url_to_safe_filename(url)
        
        if include_timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"{safe_name}_{timestamp}"
        else:
            base_filename = safe_name
        
        saved_files = {}
        
        # Extract components to save
        textual_description = results.get('textual_description', '')
        structured_description = results.get('structured_description', {})
        llm_analysis = results.get('llm_analysis', {})
        
        # Save textual description
        if textual_description:
            text_path = os.path.join(self.output_dir, f"{base_filename}.md")
            with open(text_path, 'w') as f:
                f.write(textual_description)
            saved_files['textual_description'] = text_path
        
        # Save structured description as JSON
        if structured_description:
            json_path = os.path.join(self.output_dir, f"{base_filename}.json")
            with open(json_path, 'w') as f:
                json.dump(structured_description, f, indent=2)
            saved_files['structured_description'] = json_path
        
        # Save LLM analysis if available
        if llm_analysis:
            analysis_path = os.path.join(self.output_dir, f"{base_filename}_analysis.md")
            with open(analysis_path, 'w') as f:
                f.write(f"# Analysis of {url}\n\n")
                
                analysis_type = llm_analysis.get('analysis_type', 'general')
                f.write(f"## {analysis_type.capitalize()} Analysis\n\n")
                
                response = llm_analysis.get('response', '')
                f.write(response)
            
            saved_files['llm_analysis'] = analysis_path
        
        return saved_files
    
    def display_results(self, results: Dict[str, Any]) -> None:
        """
        Display the results to stdout.
        
        Args:
            results: The results to display
        """
        textual_description = results.get('textual_description', '')
        
        if textual_description:
            print("\n" + "=" * 80)
            print(textual_description)
            print("=" * 80 + "\n")
        
        # If LLM analysis is available, display it
        llm_analysis = results.get('llm_analysis', {})
        if llm_analysis and 'response' in llm_analysis:
            print("\nLLM ANALYSIS:")
            print("-" * 80)
            print(llm_analysis['response'])
            print("-" * 80 + "\n")
        
        # Display saved file paths
        saved_files = results.get('saved_files', {})
        if saved_files:
            print("\nResults saved to:")
            for file_type, file_path in saved_files.items():
                print(f"- {file_type}: {file_path}")
    
    def _url_to_safe_filename(self, url: str) -> str:
        """Convert a URL to a safe filename."""
        # Remove protocol and www
        filename = url.lower().replace('http://', '').replace('https://', '').replace('www.', '')
        
        # Replace non-alphanumeric characters with underscores
        filename = ''.join(c if c.isalnum() or c == '.' else '_' for c in filename)
        
        # Truncate if too long
        if len(filename) > 50:
            filename = filename[:50]
        
        return filename