from django.urls import path
from Net640.apps.user_profile import views

urlpatterns = [
    path(r'signup/', views.signup_view, name="signup"),
    path(r'login/', views.login_view, name="login"),
    path(r'profile/', views.profile_view, name="profile"),
    path(r'logout/', views.logout_view, name="logout"),
]
