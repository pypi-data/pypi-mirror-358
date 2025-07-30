from .core import process_excel_with_pdfs, MainProcessor
from .services.PDFParser import extract_pdf_data
from .utils.FileTools import FileTools

__version__ = "0.1.1"
__author__ = "Hamdi Emad"
__description__ = "A module for extracting data from PDFs linked in Excel files."