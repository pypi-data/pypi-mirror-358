from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import List
from Texas_Extraction.helper.config import Settings
import logging
from Texas_Extraction.services.RequestsService import RequestHandler
from Texas_Extraction.services.PDFParser import extract_pdf_data  # Using the improved standalone function

# Configure logger
logger = logging.getLogger(__name__)

class ChunkProcessor:
    def __init__(self):
        self.session = RequestHandler()

    def get_chunk_data(self, chunk: List):
        """
        Downloads and parses a chunk of PDF URLs.

        Args:
            chunk (List[str]): A list of PDF URLs to process.

        Returns:
            List[Tuple]: A list of (url, parsed_data) results.
        """
        logger.info(f"Processing chunk with {len(chunk)} URLs.")
        downloaded = self._download_pdfs(chunk)
        if not downloaded:
            logger.warning("No valid PDFs downloaded in this chunk.")
            return []

        parsed = self._parsing_pdfs(downloaded)
        return parsed

    def _download_pdfs(self, urls: List):
        """
        Downloads PDF content concurrently using multithreading.

        Args:
            urls (List[str]): List of URLs to download.

        Returns:
            List[Tuple]: List of (url, BytesIO) pairs.
        """
        logger.debug(f"Downloading {len(urls)} PDFs concurrently.")
        with ThreadPoolExecutor(max_workers=Settings.MAX_THREADS.value) as executor:
            results = list(executor.map(self.session.get, urls))

        # Filter out None responses (failed downloads)
        valid_results = [r for r in results if r is not None and r[1] is not None]
        logger.info(f"Successfully downloaded {len(valid_results)} out of {len(urls)} PDFs.")
        return valid_results

    def _parsing_pdfs(self, urls_and_bytes: List):
        """
        Parses PDFs using multiprocessing for CPU-bound tasks.

        Args:
            urls_and_bytes (List[Tuple]): List of (url, BytesIO) pairs.

        Returns:
            List[Tuple]: List of (url, extracted_data) results.
        """
        logger.debug(f"Parsing {len(urls_and_bytes)} PDFs using multiprocessing.")
        with ProcessPoolExecutor(max_workers=Settings.MAX_POOLS.value) as pool:
            results = list(pool.map(extract_pdf_data, urls_and_bytes))

        logger.info(f"Finished parsing {len(results)} PDFs.")
        return results