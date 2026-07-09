import os
import json
import uuid
import warnings
from pathlib import Path

from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

from .models import SpeechRecord
from .services import process_audio, validate_audio_file, get_audio_duration


@method_decorator(ensure_csrf_cookie, name='dispatch')
class SpeechView(LoginRequiredMixin, TemplateView):
    template_name = 'speech.html'

    def post(self, request, *args, **kwargs):
        if 'audio_file' not in request.FILES:
            return JsonResponse({'success': False, 'error': 'No audio file provided'}, status=400)

        audio_file = request.FILES['audio_file']
        selected_lang = request.POST.get('language', 'auto')

        try:
            validate_audio_file(audio_file)
        except ValueError as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', str(request.user.id))
        os.makedirs(upload_dir, exist_ok=True)

        ext = os.path.splitext(audio_file.name)[1].lower()
        safe_name = f"{uuid.uuid4().hex}{ext}"
        filepath = os.path.join(upload_dir, safe_name)

        with open(filepath, 'wb') as f:
            for chunk in audio_file.chunks():
                f.write(chunk)

        try:
            recognized_text, detected_lang = process_audio(filepath)
            duration = get_audio_duration(filepath)

            record = SpeechRecord.objects.create(
                user=request.user,
                audio_file=f'uploads/{request.user.id}/{safe_name}',
                recognized_text=recognized_text,
                detected_language=detected_lang or '',
                duration=duration,
                file_size=os.path.getsize(filepath),
            )

            from history.services import add_history_entry
            add_history_entry(
                user=request.user,
                history_type='speech',
                source_text=recognized_text,
                target_language=detected_lang or '',
            )

            return JsonResponse({
                'success': True,
                'text': recognized_text,
                'language': detected_lang or '',
                'duration': round(duration, 1),
                'word_count': len(recognized_text.split()),
                'char_count': len(recognized_text),
            })

        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recognized_text'] = kwargs.get('recognized_text', '')
        context['languages'] = {
            'auto': 'Auto Detect',
            'en': 'English',
            'hi': 'Hindi',
            'gu': 'Gujarati',
        }
        context['max_recording_duration'] = getattr(settings, 'MAX_RECORDING_DURATION', 300)
        return context


class ProcessRecordingView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        if 'audio_blob' not in request.FILES:
            return JsonResponse({'success': False, 'error': 'No audio data received'}, status=400)

        audio_blob = request.FILES['audio_blob']
        selected_lang = request.POST.get('language', 'auto')

        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', str(request.user.id))
        os.makedirs(upload_dir, exist_ok=True)

        ext_map = {
            'audio/webm': '.webm',
            'audio/ogg': '.ogg',
            'audio/wav': '.wav',
            'audio/mp4': '.mp4',
        }
        ext = ext_map.get(audio_blob.content_type, '.webm')
        safe_name = f"rec_{uuid.uuid4().hex}{ext}"
        filepath = os.path.join(upload_dir, safe_name)

        with open(filepath, 'wb') as f:
            for chunk in audio_blob.chunks():
                f.write(chunk)

        if os.path.getsize(filepath) == 0:
            os.remove(filepath)
            return JsonResponse({'success': False, 'error': 'Empty recording'}, status=400)

        try:
            recognized_text, detected_lang = process_audio(filepath)
            duration = get_audio_duration(filepath)

            record = SpeechRecord.objects.create(
                user=request.user,
                audio_file=f'uploads/{request.user.id}/{safe_name}',
                recognized_text=recognized_text,
                detected_language=detected_lang or '',
                duration=duration,
                file_size=os.path.getsize(filepath),
            )

            from history.services import add_history_entry
            add_history_entry(
                user=request.user,
                history_type='speech',
                source_text=recognized_text,
            )

            return JsonResponse({
                'success': True,
                'text': recognized_text,
                'language': detected_lang or '',
                'duration': round(duration, 1),
                'word_count': len(recognized_text.split()),
                'char_count': len(recognized_text),
            })

        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
