"""
URLScraper connector: fetches a web page and extracts visible text using BeautifulSoup.
"""
from .base_connector import BaseConnector
import requests
from bs4 import BeautifulSoup
from ..exceptions import ConnectorError

class URLScraper(BaseConnector):
    """Connector that fetches a URL and extracts its text content."""
    def ingest(self, source: str) -> str:
        try:
            response = requests.get(source, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            # Extract text, joining blocks with spaces
            return soup.get_text(separator=' ', strip=True)
        except Exception as e:
            raise ConnectorError(f"URL scraping failed for '{source}': {e}")
