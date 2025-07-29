
class WeaverError(Exception):
    """Base class for all weaver errors."""

class DatabaseError(WeaverError):
    """Raised for database-related issues."""

class ConnectorError(WeaverError):
    """Raised when a connector (PDF/URL) fails."""

class AgentError(WeaverError):
    """Raised when task execution via LLM fails."""                
    
class ValidationError(WeaverError):
    """Raised when data validation (e.g., CSV import) fails."""     