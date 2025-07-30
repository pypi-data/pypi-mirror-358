import requests
from requests.adapters import HTTPAdapter, Retry
import io
import os
import logging

from Texas_Extraction.helper.config import Settings

# Configure logger
logger = logging.getLogger(__name__)

class RequestHandler:
    def __init__(
        self,
        headers = None,
        timeout: int = 10,
        retry_attempts: int = 3
    ):
        """
        Initializes a request handler with retry logic and custom headers.

        Args:
            headers (Optional[dict]): Custom headers. Defaults to standard browser-like headers.
            timeout (int): Timeout in seconds for each request.
            retry_attempts (int): Number of times to retry failed requests.
        """
        self.timeout = timeout

        # Setup session with retries
        self.session = requests.Session()
        retries = Retry(
            total=retry_attempts,
            backoff_factor=10,  # Exponential backoff (10s, 20s, 40s)
            status_forcelist=[500, 502, 503, 504, 429, 403],  # Retry on these statuses
            allowed_methods=('GET',)
        )
        self.session.mount('https://',  HTTPAdapter(max_retries=retries))
        self.session.mount('http://', HTTPAdapter(max_retries=retries))

        # Set default headers
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) Gecko/20100101 Firefox/138.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Dest': 'iframe',
            'Sec-Fetch-Site': 'same-site',
        }
        self.session.headers.update(self.headers)

    def get_auto_engine_server_urls(self, url):
        # make url as auto engine server path
        try:
            if "http://download.siliconexpert.com" in url:
                auto_engine_url= os.path.join(Settings.AUTO_ENGINE_SERVER.value, url.replace("http://download.siliconexpert.com", ''))
                # check if this url exist in auto engine
                if os.path.exists(auto_engine_url):
                    print(auto_engine_url)
                    with open(auto_engine_url, 'rb') as file:
                        return file.read()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed reading from auto engine '{url}': {e}", exc_info=True)
            return None
                
    def get_requests_url(self, url):
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return io.BytesIO(response.content)
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for URL '{url}': {e}", exc_info=True)
            return None

            
    def get(self, url: str):
        """
        Sends a GET request to the specified URL.

        Args:
            url (str): The URL to fetch.

        Returns:
            Tuple[str, Optional[BytesIO]]: A tuple of (url, BytesIO content), or (url, None) on failure.
        """
        logger.debug(f"Fetching URL: {url}")
        
        # check url in auton engine first
        auto_enigne_data= self.get_auto_engine_server_urls(url)
        if auto_enigne_data:
            return url, auto_enigne_data
        # if not get as http request
        else:
            return url, self.get_requests_url(url)
        