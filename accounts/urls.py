from unicodedata import name
from django.urls import path
from . import views

urlpatterns = [
    path('userlogin', views.user_login, name='userlogin'),
    path('register', views.register, name="userregistration"),
    path("userlogout", views.Handlelogout, name="userlogout"),

    path('follow/', views.follow_user),
    path('unfollow/', views.unfollow_user),
    path('edit_profile', views.edit_profile, name='edit_profile')
]
