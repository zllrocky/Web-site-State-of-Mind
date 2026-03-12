from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('about/', views.about, name='about'), # Страница "О Юле"
    path('archive/', views.all_posts, name='all_posts'), # Все статьи
]
