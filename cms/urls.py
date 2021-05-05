from django.urls import path, include
from . import views

app_name = 'cms'
urlpatterns = [
  path('api/', include('cms.api_urls', namespace='api')),
  path('login', views.LoginView.as_view(), name='login'),
  path('', views.CmsView.index, name='index'),
  path('debug', views.debug, name='debug'),
  path('a/<slug:name>', views.CmsView.article, name='article'),
  path('c/<slug:name>', views.CmsView.category, name='category'),
]
