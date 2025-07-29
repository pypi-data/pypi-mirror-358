"""
PDFReader connector: extracts text from PDF files using PyPDF2.
"""
from .base_connector import BaseConnector
from PyPDF2 import PdfReader
from ..exceptions import ConnectorError

class PDFReader(BaseConnector):
    """Connector that reads a local PDF file and extracts text."""
    def ingest(self, source: str) -> str:
        try:
            reader = PdfReader(source)
            text_chunks = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_chunks.append(page_text)
            return "\n".join(text_chunks)
        except Exception as e:
            raise ConnectorError(f"PDF ingestion failed for '{source}': {e}")