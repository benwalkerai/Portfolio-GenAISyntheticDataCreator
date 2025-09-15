#!/usr/bin/env python3
"""
Synthetic Data Generator - Main Entry Point
Generate synthetic documents and datasets using local Ollama Mistral model
"""

from ui.interface import create_gradio_app

if __name__ == "__main__":
    app = create_gradio_app()
    app.launch(server_name="0.0.0.0", server_port=7890, share=False)
