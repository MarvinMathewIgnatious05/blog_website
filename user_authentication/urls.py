from django.urls import path
from .views import user_registration,user_login,user_logout,user_profile_view,user_profile_edit,forgot_password_username,reset_password
from blog.views import blog_list
urlpatterns=[

    path('blog', blog_list, name='home'),

    path('register/', user_registration, name="register"),
    path("", user_login, name="login"),
    path('logout/',user_logout,name='logout'),
    path('user_view/', user_profile_view, name="user_view"),
    path('user_edit/', user_profile_edit, name="user_edit"),
    path('forgot-password/', forgot_password_username, name='forgot_password'),
    path('reset-password/', reset_password, name='reset_password'),
]