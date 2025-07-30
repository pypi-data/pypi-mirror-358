import logging
import time

from Texas_Extraction.utils.DataUtils import extract_unique_urls, merge_results_into_dataframe, expand_extracted_data
from Texas_Extraction.utils.FileTools import FileTools
from Texas_Extraction.services.MainProcessor import MainProcessor
from Texas_Extraction.services.OracleConnection import OracleConnection
from Texas_Extraction.helper import Queries

logger = logging.getLogger(__name__)

def process_excel_with_pdfs(file_path: str, max_processes = None):
    """
    End-to-end pipeline to read Excel file, download PDFs, extract data, and save output.

    Args:
        file_path (str): Path to input Excel file.
    
    Returns:
        pd.DataFrame: Final DataFrame with exploded parts and temps.
    """
    logger.info(f"Starting processing for file: {file_path}")
    start_time = time.time()

    # Step 1: Load input data
    file_tools = FileTools(file_path)
    df = file_tools.read()
    logger.info(f"Loaded DataFrame with {len(df)} rows.")

    # Step 2: Extract unique URLs
    urls = extract_unique_urls(df)
    if not urls:
        logger.warning("No valid URLs found in the file.")
        return df  # or raise exception depending on use case

    # Step 3: Process PDF chunks
    try:
        main_processor = MainProcessor(urls=urls, max_process= max_processes)
        results = main_processor.process_chunks()
        logger.info("Finished processing all PDFs.")
    except Exception as e:
        logger.error(f"Error during PDF processing: {e}", exc_info=True)
        raise 
    # Step 4: Merge results back into DataFrame
    updated_df = merge_results_into_dataframe(df, results)
    
    # Step 5: Expand dictionary into parts and temps
    exploded_df = expand_extracted_data(updated_df)

    # Step 6: Save output
    file_tools.export_to_txt(exploded_df)

    end_time = time.time() - start_time
    running_time = format_duration(end_time)

    try:
        # step 7: insert status inro DB
        with OracleConnection() as connection:

            total_row= exploded_df['PDF_LATEST'].nunique()
            total_extracted= exploded_df.loc[exploded_df['PARTS'].notna(), 'PDF_LATEST'].nunique()
            total_invalid= total_row - total_extracted

            query= Queries.insert_query(total_rows= total_row, num_done= total_extracted, num_broken= total_invalid, runningtime= end_time)
            connection.commit_data(query= query)
    except Exception as e:
        logger.error(f"error conneting with DB: {e}", exc_info= True)

    logger.info(f"Results successfully saved. Total time: {running_time}")
    print(f"Results successfully saved. Total time: {running_time}")
    return exploded_df


def format_duration(seconds: float) -> str:
    """Formats seconds into HH:MM:SS."""
    hours, remainder = divmod(int(seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"