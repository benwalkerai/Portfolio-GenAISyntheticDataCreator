# Synthetic Data Generator

Synthetic data generation app using **Local LLMs** (Ollama, llama.cpp, etc.) with a Gradio web interface. Generates datasets and documents in multiple formats for testing and development.

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Gradio](https://img.shields.io/badge/UI-Gradio-orange)

## Features

### Data Generation
- **CSV & Excel Files**: Generate structured tabular data
- **Schema Detection**: LLM-powered column header generation based on subject matter
- **Statistical Distributions**: Log-normal distributions for salaries, power-law for transactions
- **Temporal Consistency**: Date ranges with seasonal patterns
- **Geographic Consistency**: Validated country-city relationships
- **Correlation Preservation**: Related fields maintain relationships

### Document Generation
- **Multiple Formats**: Word (.docx), PDF (.pdf), Text (.txt), Markdown (.md)
- **Document Types**: Whitepapers, articles, reports, proposals, design documents
- **Formatting**: Automatic styling and structure
- **Iterative Generation**: Handles long-form content with multiple LLM calls

### Additional Features
- **Product Catalog Generator**: Fast-path for product data
- **Domain Constraints**: Category-specific validation rules (electronics, automotive, etc.)
- **Data Quality Options**: Control correlations and error patterns
- **Preview & Validation**: Real-time data preview before download
- **Batch Processing**: CLI support for automated generation

## Requirements

- **Python**: 3.8 or higher
- **Local LLM Server**: REQUIRED. You must have a local LLM server running (e.g., [Ollama](https://ollama.ai) or [llama.cpp](https://github.com/ggerganov/llama.cpp)).
- **Memory**: 4GB RAM minimum (8GB+ recommended for 7B models)
- **Storage**: ~500MB for dependencies

## Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd GenAISyntheticDataCreator
```

### 2. Configure Environment

Copy the example environment file:
```bash
cp .env.example .env
```
Edit `.env` to point to your local LLM server:
```ini
LLM_API_BASE=http://localhost:11434/v1  # For Ollama
# LLM_API_BASE=http://localhost:8080/v1  # For llama-server
LLM_API_KEY=ollama
LLM_MODEL=llama3.1:8b  # Match your loaded model
```

### 3. Run with uv (Recommended)

This project supports `uv` for fast dependency management.

```bash
# Install dependencies and run
uv run main.py
```

### Alternative: Standard Pip

```bash
pip install -r requirements.txt
python main.py
```

The application will launch at `http://localhost:7860`

### 4. Run with Docker

You can run the application in a container. Note that to access a local LLM running on your host machine from inside the container, you may need to use `host.docker.internal` as the host in your `.env` file (e.g., `http://host.docker.internal:11434/v1`).

```bash
# Build and start
docker-compose up --build
```

## Usage Guide

### Web Interface

1. **Select File Format**: Choose from Excel, CSV, Word, PDF, Text, or Markdown
2. **Enter Subject**: Describe your data (e.g., "Employee salary records")
3. **Set Parameters**:
   - **Data Files**: Specify rows and columns
   - **Documents**: Specify number of pages and document type
4. **Configure LLM**:
   - Verify model name and URL in the settings accordion if needed.
5. **Advanced Options** (optional):
   - Enable temporal coherence for time-series data
   - Add correlations between related fields
   - Include realistic error patterns
6. **Generate**: Click generate and wait for completion
7. **Preview & Download**: Review data and download the file

### Command Line Interface

You can generate data without the UI using `create_data.py`.

**Basic Usage:**
```bash
uv run create_data.py [OPTIONS]
```

**Common Examples:**

Generate a large customer CSV:
```bash
uv run create_data.py --csv --subject "Customer CRM records" --rows 5000 --columns 25
```

Generate a generic Excel product catalog:
```bash
uv run create_data.py --xlsx --subject "Office Supplies" --rows 200 --columns 10
```

Generate a 10-page whitepaper in Word format:
```bash
uv run create_data.py --docx --subject "Future of AI" --pages 10 --doc-type whitepaper
```

**Options Reference:**

| Category | Flag | Description |
|----------|------|-------------|
| **Format** | `--csv`, `--xlsx` | Output format for tabular data |
| | `--docx`, `--pdf`, `--txt`, `--md` | Output format for documents |
| **Data** | `--rows INT` | Number of rows (default: 100) |
| | `--columns INT` | Number of columns (default: 10) |
| **Docs** | `--pages INT` | Number of pages (default: 3) |
| | `--doc-type TEXT` | generic, whitepaper, article, report, proposal, design |
| **General** | `--subject "TEXT"` | **Required**. Topic to guide generation |
| | `-d`, `--dest PATH` | Output directory (default: current dir) |
| **Realism** | `--no-correlations` | Disable logical data relationships |
| | `--missingness FLOAT` | Rate of missing values (0.0 - 0.3) |


## Architecture

```
synthetic-data-generator/
├── config/
│   ├── settings.py              # Application configuration
│   └── logging_config.py        # Logging setup
├── generators/
│   ├── data_generator.py        # Main orchestrator
│   ├── document_generator.py    # Document generation
│   ├── excel_generator.py       # Excel data orchestrator
│   ├── constants.py             # Static data & reference tables
│   ├── llm_utils.py             # LLM interaction layer
│   ├── value_generators.py      # Single-value generators (names, IDs, dates)
│   ├── schema_templates.py      # Fallback schemas
│   ├── validators.py            # Data quality validation
│   ├── employee_generator.py    # Employee dataset generation
│   ├── product_generator.py     # Product catalog generation
│   └── sales_generator.py       # Sales transaction generation
├── ui/
│   └── interface.py             # Gradio web interface
├── utils/
│   ├── helpers.py               # Utility functions
│   └── product_constraints.py   # Product business rules
├── tests/
│   ├── test_document_cleaning.py
│   └── test_markdown_conversion.py
├── main.py                      # Web UI entry point
├── create_data.py               # CLI entry point
└── requirements.txt             # Python dependencies
```

## Configuration

### LLM Settings

Use the `.env` file to control your LLM connection. The application uses the standard OpenAI API format, which is compatible with most local servers.

- **LLM_API_BASE**: The endpoint URL (must include `/v1` usually).
- **LLM_MODEL**: The exact model name string.

## Contributing

Contributions are welcome!
- Additional file formats (JSON, Parquet, SQL)
- More document types (presentations, spreadsheets)
- Enhanced validation rules

## License

This project is licensed under the MIT License.

## Acknowledgments

- Built with [Gradio](https://gradio.app) for the web interface
- Powered by Local LLMs (Ollama, llama.cpp)
- Uses [OpenAI API](https://github.com/openai/openai-python) for standardized communication

---

**Version**: 1.0.0  
**Author**: [Ben Walker](https://github.com/benwalkerai)