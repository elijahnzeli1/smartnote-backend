"""
Core middleware for the Smart Notes application.
"""
import logging
import time
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all incoming requests and their processing time.
    """
    
    def process_request(self, request):
        """
        Called on each request before Django decides which view to execute.
        """
        request.start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """
        Called on each response.
        """
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            logger.info(
                f"{request.method} {request.path} - "
                f"Status: {response.status_code} - "
                f"Duration: {duration:.2f}s"
            )
        return response
    
    def process_exception(self, request, exception):
        """
        Called when a view raises an exception.
        """
        logger.error(
            f"Exception for {request.method} {request.path}: {str(exception)}",
            exc_info=True
        )
        return None
