class ImageProcessingError(Exception):
    """Base exception class for image processing."""
    def __init__(self, message):
        """Parameters
        ----------
        message : str
            Message to be displayed."""
        self.message = message


class InvalidDataType(ImageProcessingError):
    """Invalid data type exception raised when a function has been passed a parameter with an invalid datatype."""
    pass