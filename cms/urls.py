from django.urls import path
from . import views

app_name = 'cms'
urlpatterns = [
    path('api/article', views.ArticleView.as_view(), name='article'),
    path('api/category', views.CategoryView.as_view(), name='category'),
    path('login', views.LoginView.as_view(), name='login'),
    path('', views.IndexView.as_view(), name='index'),
    path('debug', views.debug, name='debug'),
]

