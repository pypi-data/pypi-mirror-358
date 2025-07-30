# utils/data_utils.py
import pandas as pd

import logging

logger = logging.getLogger(__name__)

def extract_unique_urls(df: pd.DataFrame):
    try:
        urls = df['PDF_LATEST'].dropna().unique().tolist()
        logger.info(f"Found {len(urls)} unique PDF URLs.")
        return urls
    except KeyError as e:
        logger.error(f"Column 'PDF_LATEST' not found: {e}")
        return []

def merge_results_into_dataframe(df: pd.DataFrame, results):
    result_dict = dict(results)
    df['Extracted_Data'] = df['PDF_LATEST'].map(result_dict)
    return df

def expand_extracted_data(df: pd.DataFrame):
    logger.info("Expanding 'Extracted_Data' column into parts and temps.")
    try:
        df['Extracted_Data'] = df['Extracted_Data'].apply(
            lambda x: list(zip(*x)) if isinstance(x, list) else x
        )

        exploded_df = df.explode("Extracted_Data", ignore_index=True)
        exploded_df[['PARTS', 'TEMPS']] = pd.DataFrame(
            exploded_df['Extracted_Data'].apply(
                lambda x: [None, None] if pd.isna(x) else (x[0], x[1])
            ).tolist(), columns=['PARTS', 'TEMPS']
        )
        exploded_df.drop(columns='Extracted_Data', inplace=True)
        return exploded_df
    except Exception as e:
        logger.error(f"Error expanding data: {e}", exc_info=True)
        raise
