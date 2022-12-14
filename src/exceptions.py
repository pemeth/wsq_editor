"""Custom exceptions.

Author: Patrik Nemeth
Xlogin: xnemet04
School: Vysoke Uceni Technicke v Brne, Fakulta Informacnich Technologii
"""
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

class InvalidInputImageDimensions(ImageProcessingError):
    """Exception raised when the input image array is not a 2D array."""
    pass