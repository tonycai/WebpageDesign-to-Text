from typing import Dict, Any, Optional
import anthropic

class LLMIntegration:
    def __init__(self, api_key: str):
        self.client = anthropic.Client(api_key=api_key)
    
    def analyze_webpage_description(self, 
                                  textual_description: str, 
                                  analysis_type: str = "general",
                                  custom_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Send webpage description to Claude for analysis.
        
        Args:
            textual_description: The textual description of the webpage
            analysis_type: Type of analysis to perform (general, ux, accessibility, structure)
            custom_prompt: Optional custom prompt to override the default analysis prompts
        
        Returns:
            Dictionary containing the analysis results
        """
        
        if custom_prompt:
            prompt = custom_prompt
        else:
            prompt = self._get_analysis_prompt(analysis_type)
        
        full_prompt = f"{prompt}\n\nHere is the textual description of the webpage:\n\n{textual_description}"
        
        try:
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=4000,
                messages=[
                    {"role": "user", "content": full_prompt}
                ]
            )
            
            return {
                'analysis_type': analysis_type,
                'prompt': prompt,
                'response': response.content[0].text
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'analysis_type': analysis_type,
                'prompt': prompt
            }
    
    def _get_analysis_prompt(self, analysis_type: str) -> str:
        """Get the appropriate prompt based on the analysis type."""
        
        prompts = {
            "general": """Analyze this textual description of a webpage and provide insights about:
1. Overall structure and layout
2. Main UI components and their organization
3. Potential usability considerations
4. Any notable design patterns used""",
            
            "ux": """Analyze this textual description of a webpage from a UX perspective and provide:
1. Strengths of the current design
2. Potential usability issues that might exist
3. Suggestions for improvement based on UX best practices
4. Assessment of information hierarchy and content organization""",
            
            "accessibility": """Analyze this textual description of a webpage from an accessibility perspective and provide:
1. Potential accessibility concerns based on the description
2. Suggestions for improving accessibility
3. Areas that should be prioritized for a detailed accessibility audit
4. WCAG guidelines that might be relevant to consider""",
            
            "structure": """Analyze this textual description of a webpage's structure and provide:
1. A high-level component breakdown
2. Assessment of the layout strategy used
3. How the UI elements relate to each other
4. Suggestions for structural improvements"""
        }
        
        return prompts.get(analysis_type, prompts["general"])