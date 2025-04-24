@startuml
skinparam backgroundColor #EEEFAF
skinparam handwritten true
skinparam defaultFontName Arial

actor User
boundary "Input Handler" as Input
control "Webpage Renderer & Screenshot Capture" as Renderer
control "GUI Analyzer" as GUIAnalysis
control "Text Extractor (OCR)" as OCR
control "Layout-to-Text Converter" as LayoutText
boundary "LLM Integration (Optional)" as LLM
boundary "Output Handler" as Output

User -> Input : Provides Webpage URL
Input -> Renderer : Webpage URL
Renderer -> GUIAnalysis : Screenshot Image
Renderer -> OCR : Screenshot Image
GUIAnalysis -> LayoutText : Structured UI Element Data, Design Styles
OCR -> LayoutText : Extracted Text
LayoutText -> LLM : Textual UI Representation
LLM -> Output : LLM Analysis (Optional)
LayoutText -> Output : Textual UI Representation
Output -> User : Result (Textual Description, Optional LLM Analysis)

@enduml
