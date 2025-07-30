"""Custom exceptions for ComfyReality AR nodes."""


class ARError(Exception):
    """Base exception for all ComfyReality AR operations."""

    pass


class ARValidationError(ARError):
    """Raised when input validation fails."""

    def __init__(self, message: str, parameter: str | None = None):
        """Initialize validation error.

        Args:
            message: Error description
            parameter: Name of the parameter that failed validation
        """
        super().__init__(message)
        self.parameter = parameter


class ARProcessingError(ARError):
    """Raised when AR processing operations fail."""

    pass


class ARFormatError(ARError):
    """Raised when data format conversion fails."""

    pass


class ARExportError(ARError):
    """Raised when export operations fail."""

    pass


class ARGeometryError(ARError):
    """Raised when geometry operations fail."""

    pass


class ARMaterialError(ARError):
    """Raised when material operations fail."""

    pass


class AROptimizationError(ARError):
    """Raised when optimization operations fail."""

    pass
