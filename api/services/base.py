from abc import ABC, abstractmethod

class BaseNominativeQuery(ABC):
    """Abstract base class for API services."""

    @abstractmethod
    def fetch_data(self, street: str, house_number: int):
        """Fetch data from the API."""
        pass
    
class BaseGISNQuery(ABC):
    """Abstract base class for API services."""

    @abstractmethod
    def fetch_data(self):
        """Fetch data from the API."""
        pass