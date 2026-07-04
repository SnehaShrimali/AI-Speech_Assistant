from django.urls import path
from . import views

app_name = 'speech'

urlpatterns = [
    path('', views.SpeechView.as_view(), name='speech'),
    path('process-recording/', views.ProcessRecordingView.as_view(), name='process_recording'),
]
