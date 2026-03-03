import gradio as gr
from config.settings import file_format_options, REPORTLAB_AVAILABLE
from utils.helpers import update_options, generate_synthetic_data

def create_gradio_app():
    
    with gr.Blocks(title="Synthetic Data Generator", theme=gr.themes.Base()) as app:
        gr.Markdown("# Synthetic Data Generator")
        gr.Markdown("Generate synthetic documents and datasets with configurable settings.")
        
        with gr.Tabs():
            with gr.Tab("Generator"):
                with gr.Row():
                    with gr.Column(scale=1):
                        file_format = gr.Dropdown(
                            choices=list(file_format_options.keys()),
                            label="File Format",
                            value="Excel Spreadsheet (.xlsx)"
                        )

                        subject_input_text = gr.Textbox(
                            label="Subject/Topic",
                            value="",
                            info="Used to generate column headers and data content",
                            lines=2,
                            visible=False
                        )
                        
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
                            visible=True
                        )

                        size_input = gr.Number(
                            label="Number of Rows (1-100,000)",
                            value=100,
                            minimum=1,
                            maximum=100000,
                            step=1
                        )
                        
                        content_input_number = gr.Number(
                            label="Number of Columns (1-100)",
                            value=10,
                            minimum=1,
                            maximum=100,
                            step=1,
                            visible=True
                        )
                        
                        content_input_dropdown = gr.Dropdown(
                            label="Document Type",
                            choices=["whitepaper", "article", "report", "proposal", "design"],
                            value="article",
                            visible=False
                        )

                        with gr.Accordion("Advanced Options", open=False):
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

                        generate_btn = gr.Button("Generate Synthetic Data", variant="primary", size="lg")

                    with gr.Column(scale=1):
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

                        gr.Markdown("""
                        ### Generation Process
                        **For Excel/CSV Files:**
                        1. Column headers are generated based on your subject
                        2. System detects data types for each column  
                        3. Values are generated to match each column type
                        4. File is generated and ready for download
                        """)

                def update_ui_for_format(file_format_val):
                    
                    config = file_format_options.get(file_format_val, {})
                    
                    uses_dropdown = config.get("uses_dropdowns", False)
                    
                    is_excel_csv = file_format_val in ["Excel Spreadsheet (.xlsx)", "CSV File (.csv)"]
                    
                    if uses_dropdown:
                        return [
                            gr.update(
                                label=config["size_label"], 
                                value=config["size_default"], 
                                minimum=1, 
                                maximum=config["size_max"]
                            ),
                            gr.update(visible=False),
                            gr.update(
                                visible=True, 
                                choices=config["content_options"], 
                                value=config["content_options"][0]
                            ),
                            gr.update(visible=True),
                            gr.update(visible=False, value="Product Catalogue"),
                            gr.update(visible=False)
                            ]
                    else:
                        return [
                            gr.update(
                                label=config["size_label"], 
                                value=config["size_default"], 
                                minimum=1, 
                                maximum=config["size_max"]
                            ),
                            gr.update(
                                visible=True, 
                                label=config["content_label"], 
                                value=config["content_default"], 
                                minimum=1, 
                                maximum=config["content_max"]
                            ),
                            gr.update(visible=False),
                            gr.update(visible=False),
                            gr.update(visible=True, value="Product Catalogue"),
                            gr.update(visible=True)
                        ]
                
                file_format.change(
                    fn=update_ui_for_format,
                    inputs=[file_format],
                    outputs=[size_input, content_input_number, content_input_dropdown, subject_input_text, subject_input_dropdown, preview_table]
                )

                def generate_wrapper(
                    file_format_val, 
                    size_val, 
                    content_num_val, 
                    content_drop_val, 
                    subject_text_val, 
                    subject_drop_val, 
                    enforce_corr, 
                    prevent_fut, 
                    apply_dist, 
                    add_miss, 
                    miss_rate, 
                    add_noi, 
                    noi_level
                ):
                    
                    config = file_format_options.get(file_format_val, {})
                    uses_dropdown = config.get("uses_dropdowns", False)
                    is_excel_csv = file_format_val in ["Excel Spreadsheet (.xlsx)", "CSV File (.csv)"]
                    
                    content_val = content_drop_val if uses_dropdown else content_num_val
                    subject_val = subject_drop_val if is_excel_csv else subject_text_val
                    
                    result = generate_synthetic_data(
                        file_format_val, size_val, content_val, subject_val, 
                        enforce_corr, prevent_fut, apply_dist, add_miss, 
                        miss_rate, add_noi, noi_level
                    )
                    
                    if len(result) == 2:
                        return result[0], result[1], None
                    return result

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