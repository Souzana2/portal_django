from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views, logout as auth_logout
from django.shortcuts import redirect

def logout_view(request):
    """Logout via GET — compatível com Django 5+ (LogoutView só aceita POST)."""
    auth_logout(request)
    return redirect('login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', logout_view, name='logout'),
    path('', include('core.urls')),
    path('entidades/', include('entidades.urls')),
    path('formacao/', include('formacao.urls')),
    path('modelos/', include('modelos_previsao.urls')),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
