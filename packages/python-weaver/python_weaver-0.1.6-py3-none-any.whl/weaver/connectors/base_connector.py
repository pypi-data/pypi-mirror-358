"""
BaseConnector defines the interface for all ingestion connectors.
"""
from abc import ABC, abstractmethod

class BaseConnector(ABC):
    @abstractmethod
    def ingest(self, source: str) -> str:
        """
        Ingest a source (file path or URL) and return its extracted text content.
        """
        pass