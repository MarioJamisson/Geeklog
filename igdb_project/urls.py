from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('games.urls')),         # <- precisa existir
    path('accounts/', include('allauth.urls')),
  # <- necessário pro login com Google
]
