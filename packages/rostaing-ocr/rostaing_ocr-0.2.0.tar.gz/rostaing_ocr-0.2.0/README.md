# Rostaing OCR, created by Davila Rostaing.

A Python OCR package for extracting text from scanned and native images or PDFs, designed for integration into AI applications such as LLMs and RAG, and to produce clean plain text (`.txt`) and Markdown (`.md`) files.

## Features

-   Converts images (PNG, JPG, etc.) and PDFs into text.
-   Includes image preprocessing (grayscale conversion) to improve OCR accuracy.
-   Processes multiple files in a single run, consolidating the output.
-   Generates output in both plain text (`.txt`) and Markdown (`.md`) formats.
-   Optional flag to print extracted content directly to the console for quick inspection.

## System Prerequisites: Tesseract OCR

**Important:** This package requires the **Tesseract OCR engine** to be installed on your system. `rostaing-ocr` is a Python wrapper that calls the `tesseract` command-line tool. You must install it and its language packs first.

### Windows Installation Guide (Recommended)

1.  **Download the Installer**: Go to the official [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) repository. They provide the most up-to-date and reliable installers for Windows.
2.  **Run the Installer**: Start the installation process.
3.  **Crucial Step - Add to PATH**: On the "Select Additional Tasks" screen, make sure to check the box for **"Add Tesseract to system PATH"**. This is essential for Python to be able to find and execute Tesseract.
4.  **Select Languages**: On the "Select additional language data" screen, expand the list and select the languages you will need for OCR (e.g., check `French` for `fra`, `English` is usually included by default).
5.  **Complete Installation**: Finish the installation and, to be safe, restart your command prompt, terminal, or IDE to ensure the system's PATH variable is updated.

### macOS (via Homebrew)

```bash
brew install tesseract
```
You can add language packs by installing `tesseract-lang`.

### Linux (Debian/Ubuntu)

```bash
sudo apt update
sudo apt install tesseract-ocr

# Also install the language packs you need. For French:
sudo apt install tesseract-ocr-fra
```

## Installation

### Best Practice: Use a Virtual Environment

To keep project dependencies isolated and avoid conflicts with other Python projects on your system, it is highly recommended to use a virtual environment.

With a standard Python installation, you can create and activate a new environment using the following commands:

**On macOS/Linux:**
```bash
# Create an environment named '.venv' in your project directory
python3 -m venv .venv

# Activate the environment
source .venv/bin/activate
```

**On Windows:**
```bash
# Create an environment named '.venv' in your project directory
python -m venv .venv

# Activate the environment
.venv\Scripts\activate
```

### Install the Package

Once Tesseract is set up and your virtual environment is activated, you can install the package from PyPI:

```bash
pip install rostaing-ocr
```

## Usage

Here is a basic example of how to use the `RostaingOCR` class.

```python
from rostaing_ocr import RostaingOCR

# --- Example 1: Process a single file ---
# This will create 'my_result.txt' and 'my_result.md' in the current directory.
extractor = RostaingOCR(
    input_path_or_paths="path/to/my_document.pdf",
    output_basename="my_result", # Optionel
    print_to_console=True # Optionel
)

# You can print to get a summary of the operation.
print(extractor)

# --- Example 2: Process multiple files and print to console ---
# This will process both files, save a consolidated output, and also print the results.
multi_extractor = RostaingOCR(
    input_path_or_paths=["document1.png", "scan_page_2.pdf"],
    output_basename="combined_report", # Optionel
    print_to_console=True, # Optionel
    languages=['fra', 'eng'] # Specify languages for Tesseract # Optionel
)

# You can print the object to get a summary of the operation.
print(multi_extractor)
```

## Application for LLM and RAG Pipelines

Large Language Models (LLMs) like GPT-4 or Llama understand text, not images or scanned documents. A vast amount of valuable knowledge is locked away in unstructured formats such as PDFs of research papers, scanned invoices, or legal contracts.

**`Rostaing OCR` serves as the crucial first step in any data ingestion pipeline for Retrieval-Augmented Generation (RAG) systems.** It bridges the gap by converting this inaccessible visual data into clean, structured text that LLMs can process.

By using `Rostaing OCR`, you can automate the process of building a knowledge base from your documents:

1.  **Input**: A directory of `Scanned PDFs` or `Images`.
2.  **Extraction (Rostaing OCR)**: Convert all documents into clean `Markdown/Text`.
3.  **Processing**: The text output can be fed into text splitters and then embedding models.
4.  **Indexing**: The resulting vectors are stored in a vector database (e.g., Chroma, Pinecone, FAISS) for efficient retrieval.

In short, `Rostaing OCR` unlocks your documents, making them ready for any modern AI stack.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Useful Links
- Github: https://github.com/Rostaing/rostaing-ocr
- Pypi: https://pypi.org/project/rostaing-ocr/
- Linkedin: https://www.linkedin.com/in/davila-rostaing/
- YouTube: [youtube.com/@RostaingAI?sub_confirmation=1](https://youtube.com/@rostaingai?si=b7jqDY4qh3_AMSXE)