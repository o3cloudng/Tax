from account.models import User
from django.db.models import Q

class CheckProfileMiddleware:
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # is_complete = User.objects.filter(Q(company_name="Olumide AI Engineering")).exists()
        is_complete = User.objects.filter(Q(company_name="") \
            | Q(phone_number="") | Q(rc_number="") | Q(country="")\
                | Q(address="") | Q(company_logo__icontains="default.png")).exists()
        request.is_complete = is_complete
        response = self.get_response(request)
        return response
