# authentication/urls.py

from django.urls import path, re_path

# from authentication import views
from authentication.views import user

urlpatterns = [
    re_path('register/', user.register,
            name='token_obtain_pair'),
    re_path('login/', user.login,
            name='token_obtain_pair'),
    re_path('profile/', user.profile,
            name='token_obtain_pair'),
]
