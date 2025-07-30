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
            results = {}
            for page in doc.pages():
                text = page.get_text()
                if "PACKAGE OPTION ADDENDUM" in text:
                    tables_data = _get_table(page)
                    results.update(_double_check_parts(tables_data, text))
            return url, results
    except Exception as e:
        logger.error("Error extracting PDF content for URL %s: %s", url, e, exc_info=True)
        return url, {}


def _double_check_parts(tables_data: list, full_text: str):
    """
    Validates each part name exists in the full text using case-insensitive matching.

    Args:
        tables_data (list): list of (part, temp) from table extraction.
        full_text (str): Full raw text of the PDF page.

    Returns:
        list[tuple]: Updated dict with matched or original part names.
    """
    results = {}

    for part, temp in tables_data:
        if not part:
            continue
        # escape special cahrs in part
        escaped_part = re.escape(part.strip())

        #match missed aprts
        match_missed_part = re.search(rf"\w*{escaped_part}\w*", full_text, re.IGNORECASE)
        if match_missed_part:
            results[match_missed_part.group().strip()] = temp
        else:
            results[part] = temp

        #match excat part
        #cause the part maybe found excat and missig in same table like this case: M38510/65702BCA , JM38510/65702BCA,
        #so need to save both parts
        #match missed aprts
        match_excat_part = re.search(rf"\s{escaped_part}\s", full_text, re.IGNORECASE)
        if match_excat_part:
            results[match_excat_part.group().strip()] = temp
        else:
            results[part] = temp

    return results


def _get_table(page: fitz.Page):
    """
    Extracts the first column as parts and any op-temp column from the table.

    Args:
        page (fitz.Page): PDF page object.

    Returns:
        Dict: Dictionary of {part: temperature}.
    """
    results = []
    try:
        tables = page.find_tables().tables
        for table in tables:
            df_table = table.to_pandas()
            if df_table.empty:
                continue

            # First column = part numbers
            parts_column = df_table.iloc[:, 0].astype(str).str.strip()
            if parts_column.dropna().empty:
                continue

            # Find op temp column
            temp_col_name = None
            for col in df_table.columns:
                if "op temp" in col.lower():
                    temp_col_name = col
                    break

            # Get temps
            if temp_col_name:
                temp_values = df_table[temp_col_name]
            else:
                temp_values = [None] * len(df_table)

            # Build result dict
            for part, temp in zip(parts_column, temp_values):
                results.append( (part, str(temp).strip() if pd.notna(temp) else None))

    except Exception as e:
        logger.exception("Error processing table on page: %s", e)

    return results