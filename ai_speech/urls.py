from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', core_views.home, name='home'),
    path('live/', core_views.LiveTranslateView.as_view(), name='live_translate'),
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('speech/', include('speech.urls')),
    path('translate/', include('translation.urls')),
    path('tts/', include('tts.urls')),
    path('history/', include('history.urls')),
    path('download/txt/', core_views.DownloadTXTView.as_view(), name='download_txt'),
    path('download/pdf/', core_views.DownloadPDFView.as_view(), name='download_pdf'),
    path('download/srt/', core_views.DownloadSRTView.as_view(), name='download_srt'),
    path('download/json/', core_views.DownloadJSONView.as_view(), name='download_json'),
    path('download/docx/', core_views.DownloadDOCXView.as_view(), name='download_docx'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
