from django.urls import path, re_path
from Net640.apps.user_profile import views

urlpatterns = [
    path(r'signup/', views.signup_view, name="signup"),
    path(r'login/', views.login_view, name="login"),
    path(r'profile/', views.profile_view, name="profile"),
    path(r'logout/', views.logout_view, name="logout"),
    re_path(r'^confirm_email_id(?P<user_id>([\d]*))/(?P<confirmation_code>([\d\w]*))$',
            views.signup_confirm, name="signup_confirm"),
    path(r'password_reset_request/', views.password_reset_request, name="password_reset_request"),
    re_path(r'^password_reset_id(?P<user_id>([\d]*))/(?P<confirmation_code>([\d\w]*))$',
            views.password_reset, name="password_reset"),
]
