from concurrent.futures import ProcessPoolExecutor
from typing import List
import logging

from Texas_Extraction.services.ChunkProcessor import ChunkProcessor
from Texas_Extraction.helper.config import Settings

# Configure logger
logger = logging.getLogger(__name__)

class MainProcessor:
    def __init__(self, urls: List, max_process =None):
        """
        Initializes the processor with a list of URLs to process.

        Args:
            urls (List[str]): List of PDF URLs.
        """
        #set max process
        if max_process:
            self.max_process= max_process
        else:
            self.max_process= Settings.MAX_MAIN_PROCESSES.value

        #set urls
        self.urls = urls

        # inialize chunks
        self.chunk_size = Settings.CHUNK_SIZE.value
        self.chunks = self._chunk_urls()

    def _chunk_urls(self):
        """
        Splits the URL list into smaller chunks for parallel processing.

        Returns:
            List[List[str]]: A list of URL chunks.
        """
        logger.info(f"Splitting {len(self.urls)} URLs into chunks of {self.chunk_size}.")
        return [
            self.urls[i:i + self.chunk_size]
            for i in range(0, len(self.urls), self.chunk_size)
        ]

    def process_chunks(self):
        """
        Processes each chunk in parallel using multiprocessing.

        Returns:
            List of parsed results per chunk. Each result is a list of (url, data) tuples.
        """
        if not self.chunks:
            logger.warning("No chunks to process.")
            return []

        logger.info(f"Starting parallel processing of {len(self.chunks)} chunks.")

        with ProcessPoolExecutor(max_workers=self.max_process) as executor:
            results = list(executor.map(ChunkProcessor().get_chunk_data, self.chunks))

        logger.info(f"Finished processing all chunks. Total chunks processed: {len(results)}.")
        return results
