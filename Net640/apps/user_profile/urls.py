from django.urls import path, re_path
from Net640.apps.user_profile import views, classy_views

app_name = 'user_profile'
urlpatterns = [
    path(r'signup/', views.signup_view, name="signup"),
    path(r'login/', views.login_view, name="login"),
    path(r'profile/', views.profile_view, name="profile"),
    path(r'logout/', views.logout_view, name="logout"),
    path(r'account_activation_sent/', views.signup_confirm_sent, name='account_activation_sent'),
    re_path(r'^confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            views.signup_confirm, name='signup_confirm'),
    path(r'reset_password/', classy_views.Net640PasswordResetView.as_view(), name="reset_password"),
    path(r'reset/done/', classy_views.Net640PasswordResetDoneView.as_view(), name='password_reset_done'),
    path(r'reset/complete/', classy_views.Net640PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    re_path(r'reset_password/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
            classy_views.Net640PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
