"""
Result.py
---------
Defines a generic response wrapper for inter-service communication.
"""

from typing import Optional, List, Any
from pydantic import BaseModel, Field
from isloth_python_common_lib.types.ErrorMessage import ErrorMessage


class Result(BaseModel):
    """
    Represents the outcome of a service operation, including metadata and errors.

    Attributes
    ----------
    success : bool
        Indicates whether the operation was successful.
    message : str
        A description or context of the result.
    data : Any, optional
        Payload or response data.
    errors : List[ErrorMessage], optional
        A list of error details if the operation failed.
    """
    success: bool = Field(default=True)
    message: str
    data: Optional[Any] = None
    errors: Optional[List[ErrorMessage]] = None

    def add_error(self, error: ErrorMessage) -> int:
        """
        Adds a single error message to the result.

        Parameters
        ----------
        error : ErrorMessage
            The error message to add.

        Returns
        -------
        int
            The total number of errors after addition.
        """
        if self.errors is None:
            self.errors = []
        self.errors.append(error)
        return len(self.errors)

    def add_errors(self, errors: List[ErrorMessage]) -> int:
        """
        Adds multiple error messages to the result.

        Parameters
        ----------
        errors : list of ErrorMessage
            A list of error messages to add.

        Returns
        -------
        int
            The total number of errors after addition.
        """
        if self.errors is None:
            self.errors = []
        self.errors.extend(errors)
        return len(self.errors)

    def clear_errors(self) -> None:
        """
        Clears all error messages.
        """
        self.errors = []

    def is_success(self) -> bool:
        """
        Checks if the result indicates success.

        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        return self.success

    def has_errors(self) -> bool:
        """
        Checks whether any errors exist.

        Returns
        -------
        bool
            True if errors are present, False otherwise.
        """
        return bool(self.errors)

    def get_errors_size(self) -> int:
        """
        Gets the number of recorded errors.

        Returns
        -------
        int
            Count of errors.
        """
        return len(self.errors or [])
