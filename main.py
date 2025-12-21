#!/usr/bin/env python3
"""
Synthetic Data Generator - Main Entry Point

This is the primary entry point for the Synthetic Data Generator application.
It launches the Gradio web interface that provides an intuitive UI for generating
synthetic data files and documents using local Ollama LLM models.

Features:
- Web-based interface for easy data generation
- Support for CSV and Excel data files
- Document generation (Word, PDF, Text, Markdown)
- Real-time preview and validation
- Advanced options for data realism
- Local LLM integration via Ollama

Usage:
    python main.py

The application will start a web server accessible at http://localhost:7860
and provide a user-friendly interface for generating synthetic data.

Author: Ben Walker (https://github.com/benwalkerai)
Version: 1.0.0
"""

from ui.interface import create_gradio_app
from config.logging_config import setup_logging

if __name__ == "__main__":
    # Initialize logging
    setup_logging()
    
    # Create and launch the Gradio web application
    app = create_gradio_app()
    app.launch(server_name="0.0.0.0", server_port=7860, share=False)
