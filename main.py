#!/usr/bin/env python3
"""Main entry point for the Synthetic Data Generator UI.

Starts the Gradio web interface for generating datasets and documents via
local LLMs.
"""

from ui.interface import create_gradio_app
from config.logging_config import setup_logging

if __name__ == "__main__":
    # Initialize logging
    setup_logging()
    
    # Create and launch the Gradio web application
    app = create_gradio_app()
    app.launch(server_name="0.0.0.0", server_port=7860, share=False)
