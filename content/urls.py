from unicodedata import name
from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('explore', views.explore, name="explore"),
    path('tag/<str:tag>', views.get_tag, name="get_tag"),
    path('post/<int:id>', views.viewPost, name='view_post'),
    re_path(r'search', views.search, name='search'),
    path('addPost', views.addPost, name="add_post"),
    path('add_comment', views.add_comment, name='add_comment'),
    path('like_post/', views.postlike, name='like_post'),
    path('toggle_bookmark/', views.toggle_bookmark, name='toggle_bookmark'),
    path('<str:uname>', views.profile, name="profile_page"),
    path('<str:uname>/view/analytics', views.view_analytics, name="view_analytics"),
    path('<str:uname>/view/bookmarks', views.view_bookmarks, name="view_bookmarks"),
]
