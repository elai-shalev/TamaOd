from abc import ABC, abstractmethod


class DataRetrievalError(Exception):
    """Exception raised when data retrieval from an external service fails."""

    def __init__(
        self, message: str, status_code: int | None = None
    ):
        """Initialize the exception.

        Args:
            message: Error message describing what went wrong.
            status_code: Optional HTTP status code if the error came from
                an HTTP request.
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class BaseNominativeQuery(ABC):
    """Abstract base class for API services."""

    @abstractmethod
    def fetch_data(
        self, street: str, house_number: int
    ) -> tuple[float, float]:
        """Fetch data from the API.

        Args:
            street: Street name.
            house_number: House number.

        Returns:
            A tuple of (longitude, latitude) coordinates.

        Raises:
            DataRetrievalError: If the data retrieval fails.
        """


class BaseGISNQuery(ABC):
    """Abstract base class for API services."""

    @abstractmethod
    def fetch_data(self, coordinate, radius: int):
        """Fetch data from the API."""
