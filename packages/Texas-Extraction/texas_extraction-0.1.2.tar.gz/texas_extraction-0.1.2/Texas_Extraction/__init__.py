from .core import process_excel_with_pdfs, MainProcessor
from .services.PDFParser import extract_pdf_data
from .utils.FileTools import FileTools
from Texas_Extraction.services.RequestsService import RequestHandler

__version__ = "0.1.2"
__author__ = "Hamdi Emad"
__description__ = "A module for extracting data from PDFs linked in Excel files."