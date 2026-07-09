from django.urls import path
from . import views

app_name = 'translation'

urlpatterns = [
    path('', views.TranslateView.as_view(), name='translate'),
    path('api/', views.TranslateAPIView.as_view(), name='translate_api'),
]
