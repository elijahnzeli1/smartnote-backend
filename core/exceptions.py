"""
Custom exceptions for the Smart Notes application.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


class AIServiceException(Exception):
    """
    Exception raised when the AI service (Gemini) fails.
    """
    def __init__(self, message="AI service is currently unavailable", details=None):
        self.message = message
        self.details = details
        super().__init__(self.message)


class ValidationException(Exception):
    """
    Exception raised for business logic validation errors.
    """
    def __init__(self, message="Validation error", details=None):
        self.message = message
        self.details = details
        super().__init__(self.message)


def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF.
    Handles custom exceptions and provides consistent error responses.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # Handle custom exceptions
    if isinstance(exc, AIServiceException):
        logger.error(f"AI Service Exception: {exc.message}", exc_info=True)
        return Response(
            {
                'error': 'AI Service Error',
                'message': exc.message,
                'details': exc.details
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    if isinstance(exc, ValidationException):
        logger.warning(f"Validation Exception: {exc.message}")
        return Response(
            {
                'error': 'Validation Error',
                'message': exc.message,
                'details': exc.details
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # If response is None, it's an unhandled exception
    if response is None:
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        return Response(
            {
                'error': 'Internal Server Error',
                'message': 'An unexpected error occurred. Please try again later.'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Add custom error formatting for DRF exceptions
    if hasattr(response, 'data'):
        response.data = {
            'error': response.data.get('detail', 'Error'),
            'message': str(response.data)
        }
    
    return response
