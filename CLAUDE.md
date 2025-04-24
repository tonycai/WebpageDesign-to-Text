# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
WebpageDesign-to-Text: A Python tool that converts webpage designs to structured textual descriptions for UX research, web development, accessibility auditing, and AI/LLM applications.

## Technology Stack
- Python
- Pyppeteer (Puppeteer for Python)
- Google Cloud Vision API
- Anthropic API (Claude)
- TensorFlow/PyTorch (for GUI analysis)

## Commands
- Install: `pip install -r requirements.txt`
- Run: `python main.py [URL]`
- Test: `pytest tests/`

## Code Style Guidelines
- Follow PEP 8 for Python code style
- Use type hints for all function parameters and return values
- Organize imports: standard library → third-party packages → local modules
- Use descriptive variable/function names (snake_case)
- Handle errors with try/except blocks for API calls and external services
- Document code with docstrings (Google style)
- Maintain modular architecture separating concerns as outlined in general-architecture.md