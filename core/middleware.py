from django.contrib.auth import logout
from django.utils.deprecation import MiddlewareMixin
import datetime


class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['Content-Security-Policy'] = "default-src 'self'; img-src 'self' https://res.cloudinary.com; script-src 'self'; style-src 'self';"
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Cache-Control'] = 'no-store, no-cache'
        return response
    


class AutoLogoutMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.user.is_authenticated:
            return

        last_activity = request.session.get('last_activity')
        if last_activity:
            now = datetime.datetime.now()
            delta = now - datetime.datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if delta.seconds > 1800:
                logout(request)
        request.session['last_activity'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')