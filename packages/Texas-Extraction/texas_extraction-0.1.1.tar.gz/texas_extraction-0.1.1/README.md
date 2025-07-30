# PDF Table Extractor

A Python module for extracting structured part and temperature data from PDF documents linked in Excel files.

## Features

- Multithreaded downloading of PDFs
- Multiprocessing-based table extraction using PyMuPDF
- Clean merging back into DataFrame
- Export to Excel or TXT

## Installation

```bash
pip install Texas-Extraction

```sample input
from Texas_Extraction import process_excel_with_pdfs
process_excel_with_pdfs(file_path=r"C:\Users\157336\Downloads\TXN Rows.xlsx")