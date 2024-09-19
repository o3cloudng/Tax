
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
# from django.conf.urls.defaults import *
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
admin.autodiscover()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('clients/', include("account.urls")),
    path('tax/', include("tax.urls")),
    path('payments/', include("payments.urls")),
    path('agency/', include("agency.urls")),
    # path('adminarea/', include("admin.urls")),
]

if settings.DEBUG:  
        urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)  
        # + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()