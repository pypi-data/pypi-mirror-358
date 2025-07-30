class ApiError(Exception):
    """Base API error class"""

    def __init__(self, message, code=None, status=None):
        super().__init__(message)
        self.code = code
        self.status = status

    @classmethod
    def from_error(cls, error):
        """
        Convert from various error types to ApiError
        """
        if isinstance(error, cls):
            return error

        # Extract error details
        message = str(error)
        code = None
        status = None

        if hasattr(error, "status"):
            status = error.status
        if hasattr(error, "code"):
            code = error.code
        if hasattr(error, "status_code"):
            status = error.status_code

        # Handle HTTP status codes
        if "404" in message:
            status = 404
            code = 404
        elif "500" in message:
            status = 500
            code = 500

        return cls(message, code=code, status=status)
