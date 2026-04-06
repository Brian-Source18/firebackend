import logging

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/api/emergency-reports/':
            print("\n" + "="*50)
            print(f"REQUEST: {request.method} {request.path}")
            print(f"User: {request.user}")
            print(f"Content-Type: {request.content_type}")
            print(f"POST data: {request.POST}")
            print(f"FILES: {request.FILES}")
            print("="*50 + "\n")
        
        response = self.get_response(request)
        
        if request.path == '/api/emergency-reports/' and response.status_code >= 400:
            print("\n" + "="*50)
            print(f"RESPONSE: {response.status_code}")
            print(f"Content: {response.content}")
            print("="*50 + "\n")
        
        return response
