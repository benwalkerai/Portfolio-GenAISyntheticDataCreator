"""Gradio UI for generating datasets and documents."""

import gradio as gr
from typing import List, Tuple, Optional, Any, Dict, Union
from config.settings import file_format_options, REPORTLAB_AVAILABLE
from utils.helpers import update_options, generate_synthetic_data

def create_gradio_app() -> gr.Blocks:
    """Create and configure the Gradio interface."""
    
    with gr.Blocks(title="Synthetic Data Generator", theme=gr.themes.Base()) as app:
        # Main header and description
        gr.Markdown("# Synthetic Data Generator")
        gr.Markdown("Generate synthetic documents and datasets with configurable settings.")
        
        with gr.Tabs():
            with gr.Tab("Generator"):
                with gr.Row():
                    with gr.Column(scale=1):
                        # File format selection dropdown
                        # Dynamically populated from settings.py configuration
                        file_format = gr.Dropdown(
                            choices=list(file_format_options.keys()),
                            label="File Format",
                            value="Excel Spreadsheet (.xlsx)"
                        )

                        # Subject input field - textbox for documents, dropdown for Excel/CSV
                        # Text input for free-form subject specification (used for documents)
                        subject_input_text = gr.Textbox(
                            label="Subject/Topic",
                            value="",
                            info="Used to generate column headers and data content",
                            lines=2,
                            visible=False  # Initially hidden, shown for document formats
                        )
                        
                        # Dropdown for predefined dataset types (used for Excel/CSV)
                        subject_input_dropdown = gr.Dropdown(
                            label="Select Dataset Type",
                            choices=[
                                "Product Catalogue",
                                "Financial Transactions", 
                                "Sales Figures",
                                "Sales Orders",
                                "Employee Information"
                            ],
                            value="Product Catalogue",
                            visible=True  # Initially visible, hidden for document formats
                        )

                        # Dynamic size options (will be updated based on format)
                        # Size input for rows (Excel/CSV) or pages (documents)
                        size_input = gr.Number(
                            label="Number of Rows (1-100,000)",
                            value=100,
                            minimum=1,
                            maximum=100000,
                            step=1
                        )
                        
                        # Number input for column count (used for Excel/CSV formats)
                        content_input_number = gr.Number(
                            label="Number of Columns (1-100)",
                            value=10,
                            minimum=1,
                            maximum=100,
                            step=1,
                            visible=True  # Initially visible for Excel/CSV
                        )
                        
                        # Dropdown for document type selection (used for document formats)
                        content_input_dropdown = gr.Dropdown(
                            label="Document Type",
                            choices=["whitepaper", "article", "report", "proposal", "design"],
                            value="article",
                            visible=False  # Initially hidden, shown for document formats
                        )

                        # Advanced options accordion for data quality customization
                        with gr.Accordion("Advanced Options", open=False):
                            # Data correlation and consistency options
                            enforce_correlations = gr.Checkbox(
                                label="Enforce correlations (totals, ages, dates)", 
                                value=True,
                                info="Ensures logical relationships between related fields"
                            )
                            prevent_future = gr.Checkbox(
                                label="Prevent future dates", 
                                value=True,
                                info="Ensures all generated dates are in the past"
                            )
                            apply_distributions = gr.Checkbox(
                                label="Apply realistic distributions", 
                                value=True,
                                info="Uses statistical distributions for more realistic data"
                            )
                            
                            # Data completeness and noise options
                            add_missingness = gr.Checkbox(
                                label="Introduce missing values", 
                                value=False,
                                info="Adds realistic missing data patterns"
                            )
                            missingness_rate = gr.Slider(
                                0.0, 0.3, value=0.05, step=0.01, 
                                label="Missingness rate (max 30%)",
                                info="Percentage of values to make missing"
                            )
                            add_noise = gr.Checkbox(
                                label="Add light noise/typos to text", 
                                value=False,
                                info="Introduces realistic typos and variations"
                            )
                            noise_level = gr.Slider(
                                0.0, 0.2, value=0.05, step=0.01, 
                                label="Noise level (max 20%)",
                                info="Intensity of noise/typos to add"
                            )

                        # Primary action button for data generation
                        generate_btn = gr.Button("Generate Synthetic Data", variant="primary", size="lg")

                    with gr.Column(scale=1):
                        # Output section for generated files and status
                        output_file = gr.File(label="Generated File")
                        status_text = gr.Textbox(
                            label="Status", 
                            interactive=False, 
                            lines=6, 
                            scale=1,
                            info="Shows generation progress and any errors"
                        )
                        preview_table = gr.Dataframe(
                            label="Preview (first 10 rows)", 
                            interactive=False
                        )

                        # Process information for user guidance
                        gr.Markdown("""
                        ### Generation Process
                        **For Excel/CSV Files:**
                        1. Column headers are generated based on your subject
                        2. System detects data types for each column  
                        3. Values are generated to match each column type
                        4. File is generated and ready for download
                        """)

                # Event handlers - toggle between number and dropdown inputs
                def update_ui_for_format(file_format_val: str) -> List[gr.update]:
                    """
                    Update UI components based on selected file format.
                    
                    This function dynamically shows/hides and configures UI components
                    based on whether the selected format is document-based (pages) or
                    data-based (rows/columns). It handles the transition between different
                    input types and updates labels and constraints accordingly.
                    
                    Args:
                        file_format_val (str): The selected file format from the dropdown.
                                             Must be a key from file_format_options.
                    
                    Returns:
                        List[gr.update]: List of Gradio update objects to modify UI components.
                                       Order: [size_input, content_input_number, content_input_dropdown,
                                             subject_input_text, subject_input_dropdown, preview_table]
                    
                    Example:
                        >>> updates = update_ui_for_format("Excel Spreadsheet (.xlsx)")
                        >>> # Updates will show row/column inputs and hide document inputs
                    """
                    # Get configuration for the selected format
                    config = file_format_options.get(file_format_val, {})
                    
                    # Check if this format uses dropdowns for content selection
                    uses_dropdown = config.get("uses_dropdowns", False)
                    
                    # Check if this is a spreadsheet format (Excel/CSV)
                    is_excel_csv = file_format_val in ["Excel Spreadsheet (.xlsx)", "CSV File (.csv)"]
                    
                    if uses_dropdown:
                        # Document format: show pages and document type
                        # Configure UI for document-based formats (Word, Text, PDF)
                        return [
                            # Update size input for pages
                            gr.update(
                                label=config["size_label"], 
                                value=config["size_default"], 
                                minimum=1, 
                                maximum=config["size_max"]
                            ),
                            # Hide column number input
                            gr.update(visible=False),
                            # Show document type dropdown
                            gr.update(
                                visible=True, 
                                choices=config["content_options"], 
                                value=config["content_options"][0]  # Use first option as default
                            ),
                            # Show text input for free-form subject
                            gr.update(visible=True),
                            # Hide predefined dataset dropdown
                            gr.update(visible=False, value="Product Catalogue"),
                            # Hide preview table for documents
                            gr.update(visible=False)
                        ]
                    else:
                        # Data format: show rows and columns
                        # Configure UI for data-based formats (Excel, CSV)
                        return [
                            # Update size input for rows
                            gr.update(
                                label=config["size_label"], 
                                value=config["size_default"], 
                                minimum=1, 
                                maximum=config["size_max"]
                            ),
                            # Show column number input
                            gr.update(
                                visible=True, 
                                label=config["content_label"], 
                                value=config["content_default"], 
                                minimum=1, 
                                maximum=config["content_max"]
                            ),
                            # Hide document type dropdown
                            gr.update(visible=False),
                            # Hide text input for free-form subject
                            gr.update(visible=False),
                            # Show predefined dataset dropdown
                            gr.update(visible=True, value="Product Catalogue"),
                            # Show preview table for data formats
                            gr.update(visible=True)
                        ]
                
                # Event handler for file format changes
                # Updates UI components when user selects different file format
                file_format.change(
                    fn=update_ui_for_format,
                    inputs=[file_format],
                    outputs=[size_input, content_input_number, content_input_dropdown, subject_input_text, subject_input_dropdown, preview_table]
                )

                # Generate button wrapper function - handles different input types
                def generate_wrapper(
                    file_format_val: str, 
                    size_val: int, 
                    content_num_val: int, 
                    content_drop_val: str, 
                    subject_text_val: str, 
                    subject_drop_val: str, 
                    enforce_corr: bool, 
                    prevent_fut: bool, 
                    apply_dist: bool, 
                    add_miss: bool, 
                    miss_rate: float, 
                    add_noi: bool, 
                    noi_level: float
                ) -> Tuple[Optional[str], str, Optional[Any]]:
                    """
                    Wrapper function for data generation that handles different input types.
                    
                    This function acts as a bridge between the UI and the data generation
                    logic. It determines which input values to use based on the selected
                    file format and passes them to the generation function.
                    
                    Args:
                        file_format_val (str): Selected file format
                        size_val (int): Size value (rows or pages)
                        content_num_val (int): Column count for data formats
                        content_drop_val (str): Document type for document formats
                        subject_text_val (str): Free-form subject text
                        subject_drop_val (str): Predefined dataset type
                        enforce_corr (bool): Whether to enforce data correlations
                        prevent_fut (bool): Whether to prevent future dates
                        apply_dist (bool): Whether to apply realistic distributions
                        add_miss (bool): Whether to add missing values
                        miss_rate (float): Rate of missing values (0.0-0.3)
                        add_noi (bool): Whether to add noise/typos
                        noi_level (float): Level of noise (0.0-0.2)
                    
                    Returns:
                        Tuple[Optional[str], str, Optional[Any]]: 
                        - Generated file path (or None if error)
                        - Status message
                        - Preview data (or None if not applicable)
                    """
                    # Get configuration for the selected format
                    config = file_format_options.get(file_format_val, {})
                    uses_dropdown = config.get("uses_dropdowns", False)
                    is_excel_csv = file_format_val in ["Excel Spreadsheet (.xlsx)", "CSV File (.csv)"]
                    
                    # Select appropriate content and subject values based on format
                    content_val = content_drop_val if uses_dropdown else content_num_val
                    subject_val = subject_drop_val if is_excel_csv else subject_text_val
                    
                    # Call the data generation function with selected parameters
                    result = generate_synthetic_data(
                        file_format_val, size_val, content_val, subject_val, 
                        enforce_corr, prevent_fut, apply_dist, add_miss, 
                        miss_rate, add_noi, noi_level
                    )
                    
                    # Ensure we always return 3 values (file, status, preview)
                    # Handle cases where generation function returns only 2 values
                    if len(result) == 2:
                        return result[0], result[1], None
                    return result

                # Event handler for generate button click
                # Connects all UI inputs to the generation wrapper function
                generate_btn.click(
                    fn=generate_wrapper,
                    inputs=[
                        file_format, size_input, content_input_number, content_input_dropdown, 
                        subject_input_text, subject_input_dropdown, enforce_correlations, 
                        prevent_future, apply_distributions, add_missingness, missingness_rate, 
                        add_noise, noise_level
                    ],
                    outputs=[output_file, status_text, preview_table]
                )
    
    return app