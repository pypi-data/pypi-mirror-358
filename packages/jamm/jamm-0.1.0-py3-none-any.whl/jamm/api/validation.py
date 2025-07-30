from typing import Any, Dict, List, Optional, Union, Set, Callable
import re
from datetime import datetime


class RequestValidator:
    """Utility class for validating API request parameters."""

    @staticmethod
    def validate_required(params: Dict, required: List[str]) -> None:
        """
        Validate that all required parameters are provided.

        Args:
            params: Dictionary of parameters
            required: List of required parameter names

        Raises:
            ValueError: If any required parameter is missing
        """
        missing = [
            param for param in required if param not in params or params[param] is None
        ]
        if missing:
            raise ValueError(f"Missing required parameters: {', '.join(missing)}")

    @staticmethod
    def validate_enum(name: str, value: Any, allowed_values: Set[Any]) -> None:
        """
        Validate that a value is one of the allowed values.

        Args:
            name: Parameter name
            value: Parameter value
            allowed_values: Set of allowed values

        Raises:
            ValueError: If the value is not in the allowed values
        """
        if value not in allowed_values:
            allowed_str = ", ".join(repr(v) for v in allowed_values)
            raise ValueError(
                f"Invalid value for '{name}'. Got: {repr(value)}. Allowed values: [{allowed_str}]"
            )

    @staticmethod
    def validate_range(
        name: str,
        value: Union[int, float],
        minimum: Optional[Union[int, float]] = None,
        maximum: Optional[Union[int, float]] = None,
    ) -> None:
        """
        Validate that a numeric value is within the specified range.

        Args:
            name: Parameter name
            value: Parameter value
            minimum: Minimum allowed value (inclusive)
            maximum: Maximum allowed value (inclusive)

        Raises:
            ValueError: If the value is outside the allowed range
        """
        if minimum is not None and value < minimum:
            raise ValueError(
                f"Invalid value for '{name}'. {value} is less than minimum of {minimum}"
            )

        if maximum is not None and value > maximum:
            raise ValueError(
                f"Invalid value for '{name}'. {value} is greater than maximum of {maximum}"
            )

    @staticmethod
    def validate_length(
        name: str,
        value: Union[str, List, Dict],
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
    ) -> None:
        """
        Validate that a string or collection has a length within the specified range.

        Args:
            name: Parameter name
            value: Parameter value
            min_length: Minimum allowed length (inclusive)
            max_length: Maximum allowed length (inclusive)

        Raises:
            ValueError: If the length is outside the allowed range
        """
        if value is None:
            return

        length = len(value)

        if min_length is not None and length < min_length:
            raise ValueError(
                f"Invalid length for '{name}'. Got {length}, but minimum length is {min_length}"
            )

        if max_length is not None and length > max_length:
            raise ValueError(
                f"Invalid length for '{name}'. Got {length}, but maximum length is {max_length}"
            )

    @staticmethod
    def validate_pattern(name: str, value: str, pattern: str) -> None:
        """
        Validate that a string matches a regular expression pattern.

        Args:
            name: Parameter name
            value: String value to validate
            pattern: Regular expression pattern

        Raises:
            ValueError: If the string doesn't match the pattern
        """
        if value is None:
            return

        if not re.match(pattern, value):
            raise ValueError(
                f"Invalid format for '{name}'. Value '{value}' does not match the required pattern."
            )

    @staticmethod
    def validate_email(name: str, value: str) -> None:
        """
        Validate that a string is a properly formatted email address.

        Args:
            name: Parameter name
            value: String value to validate

        Raises:
            ValueError: If the string is not a valid email address
        """
        if value is None:
            return

        # Email regex pattern
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        if not re.match(pattern, value):
            raise ValueError(
                f"Invalid email address for '{name}'. '{value}' is not a valid email format."
            )

    @staticmethod
    def validate_url(name: str, value: str, require_protocol: bool = True) -> None:
        """
        Validate that a string is a properly formatted URL.

        Args:
            name: Parameter name
            value: String value to validate
            require_protocol: If True, requires http:// or https:// prefix

        Raises:
            ValueError: If the string is not a valid URL
        """
        if value is None:
            return

        # URL regex pattern
        if require_protocol:
            pattern = r"^(http|https)://[a-zA-Z0-9]+([\-\.]{1}[a-zA-Z0-9]+)*\.[a-zA-Z]{2,}(:[0-9]{1,5})?(\/.*)?$"
        else:
            pattern = r"^[a-zA-Z0-9]+([\-\.]{1}[a-zA-Z0-9]+)*\.[a-zA-Z]{2,}(:[0-9]{1,5})?(\/.*)?$"

        if not re.match(pattern, value):
            raise ValueError(
                f"Invalid URL for '{name}'. '{value}' is not a valid URL format."
            )

    @staticmethod
    def validate_date(name: str, value: str, formats: List[str] = None) -> None:
        """
        Validate that a string is a properly formatted date.

        Args:
            name: Parameter name
            value: String value to validate
            formats: List of date formats to try (default: ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"])

        Raises:
            ValueError: If the string is not a valid date in any of the accepted formats
        """
        if value is None:
            return

        if formats is None:
            formats = ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"]

        is_valid = False
        for date_format in formats:
            try:
                datetime.strptime(value, date_format)
                is_valid = True
                break
            except ValueError:
                continue

        if not is_valid:
            formats_str = ", ".join(formats)
            raise ValueError(
                f"Invalid date for '{name}'. '{value}' does not match any of the accepted formats: {formats_str}"
            )

    @staticmethod
    def validate_composite(
        name: str,
        value: Any,
        validations: List[Callable[[str, Any], None]],
    ) -> None:
        """
        Apply multiple validation functions to a single value.

        Args:
            name: Parameter name
            value: Value to validate
            validations: List of validation functions to apply

        Raises:
            ValueError: If the value fails any validation
        """
        for validation_fn in validations:
            validation_fn(name, value)
