#!/usr/bin/env python3

from ui.interface import create_gradio_app
from config.logging_config import setup_logging

if __name__ == "__main__":
    setup_logging()
    app = create_gradio_app()
    app.launch(server_name="0.0.0.0", server_port=7861, share=False)
