from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('games.urls')),
    path('account/', include('allauth.urls')),  # allauth cuida de login, senha etc.
]
