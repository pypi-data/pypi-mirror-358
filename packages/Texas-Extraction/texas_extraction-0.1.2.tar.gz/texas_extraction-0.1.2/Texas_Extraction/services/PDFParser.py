import fitz  # PyMuPDF
import re
import pandas as pd
import logging
from typing import Dict, Optional, Tuple, Any

# Configure logger
logger = logging.getLogger(__name__)

def extract_pdf_data(url_bytes: Tuple[str, Any]):
    """
    Extract structured data from PDF content if it contains 'PACKAGE OPTION ADDENDUM'.

    Args:
        url_bytes (Tuple[str, BytesIO]): A tuple containing URL and PDF content as bytes or BytesIO.

    Returns:
        Tuple[str, Dict]: The URL and extracted dictionary mapping parts to temperatures.
    """
    url, byts = url_bytes

    if byts is None:
        logger.warning("Empty content received for URL: %s", url)
        return url, {}

    try:
        with fitz.open(stream=byts) as doc:
            pages_data = {}
            for page in doc.pages():
                text = page.get_text()
                if "PACKAGE OPTION ADDENDUM" in text:
                    tables_data = _get_table_data(page)
                    if tables_data:

                        for key, values in tables_data.items():
                            if key in pages_data:
                                pages_data[key].extend(values)
                            else:
                                pages_data[key]= values
            return url, list(pages_data.values())
    except Exception as e:
        logger.error("Error extracting PDF content for URL %s: %s", url, e, exc_info=True)
        return url, []

def _get_header_index(header, columns: list, page:fitz.Page):
    columns_index=[]
    
    for index, cell in enumerate(header.cells):
        
        for column in columns:  
            
            if column.lower() in page.get_textbox(cell).lower():
                columns_index.append(index)

    return columns_index

def clean_text(text):
    outlier= re.search('\n\w{0,2}$', text)
    if outlier:
        return text.replace(outlier.group(), '')
    return text

def _get_data_based_on_column_index(body, column_index:int, page:fitz.Page):
    
    result= []
    
    for row in body:   
        # cell postions
        x0, y0, x1, y1 = row.cells[column_index]    
        
        # reduce x0 which is left and increase x1 which is right to got incomplete parts
        x0= x0-2
        x1= x1+2

        text= page.get_textbox((x0, y0, x1, y1))
        
        if text:
            cleaned_text= clean_text(text).strip()
            result.append(cleaned_text)
        
    return result


def _get_table_data(page: fitz.Page, columns: list= ["Orderable", '°C']):
    """
    Extracts the first column as parts and any op-temp column from the table.

    Args:
        page (fitz.Page): PDF page object.

    Returns:
        Dict: Dictionary of {part: temperature}.
    """
    results = {}
    try:
        tables = page.find_tables().tables
        for table in tables:
            
            rows= table.rows
            header, body= rows[0], rows[1:]

            columns_indexs= _get_header_index(header= header, columns= columns, page= page)

            data= {
                column: _get_data_based_on_column_index(body=body, column_index= column, page= page) 
                for column in columns_indexs
                }
            
            if data:
                # fill results from data extract form each table
                for key, values in data.items():
                    if key in results:
                        results[key].extend(values)
                    else:
                        results[key]= values
    except Exception as e:
        logger.exception("Error processing table on page: %s", e)

    return results