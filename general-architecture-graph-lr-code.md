---
config:
  layout: fixed
---
flowchart TD
    User[User] -->|Provides Webpage URL| Input[Input Handler]
    Input -->|Webpage URL| Renderer[Webpage Renderer & Screenshot Capture]
    Renderer -->|Screenshot Image| GUIAnalysis[GUI Analyzer]
    Renderer -->|Screenshot Image| OCR[Text Extractor OCR]
    GUIAnalysis -->|Structured UI Element Data, Design Styles| LayoutText[Layout-to-Text Converter]
    OCR -->|Extracted Text| LayoutText
    LayoutText -->|Textual UI Representation| LLM[LLM Integration Optional]
    LLM -->|LLM Analysis Optional| Output[Output Handler]
    LayoutText -->|Textual UI Representation| Output
    Output -->|Result: Textual Description, Optional LLM Analysis| User

