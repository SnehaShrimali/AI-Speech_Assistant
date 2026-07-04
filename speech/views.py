import os
import json
import uuid
from django.conf import settings
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import SpeechRecord
from .services import process_audio, validate_audio_file
from history.services import add_history_entry


class SpeechView(LoginRequiredMixin, TemplateView):
    template_name = 'speech.html'

    def post(self, request, *args, **kwargs):
        if 'audio_file' in request.FILES:
            return self.handle_audio_upload(request)
        return self.get(request, *args, **kwargs)

    def handle_audio_upload(self, request):
        audio_file = request.FILES['audio_file']

        try:
            validate_audio_file(audio_file)
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('speech:speech')

        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)

        ext = os.path.splitext(audio_file.name)[1]
        filename = f"{uuid.uuid4().hex}{ext}"
        filepath = os.path.join(upload_dir, filename)

        with open(filepath, 'wb+') as f:
            for chunk in audio_file.chunks():
                f.write(chunk)

        try:
            recognized_text = process_audio(filepath)

            if not recognized_text:
                messages.warning(request, 'Could not recognize speech in the audio.')
                return redirect('speech:speech')

            record = SpeechRecord.objects.create(
                user=request.user,
                audio_file=f'uploads/{filename}',
                recognized_text=recognized_text,
            )

            add_history_entry(
                user=request.user,
                history_type='speech',
                source_text=recognized_text,
            )

            messages.success(request, 'Speech recognized successfully!')
            return render(request, self.template_name, {
                'recognized_text': recognized_text,
            })

        except Exception as e:
            messages.error(request, f'Error processing audio: {str(e)}')
            return redirect('speech:speech')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recognized_text'] = kwargs.get('recognized_text', '')
        return context


class ProcessRecordingView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        if 'audio_blob' not in request.FILES:
            return JsonResponse({'success': False, 'error': 'No audio file provided'}, status=400)

        audio_blob = request.FILES['audio_blob']

        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)

        filename = f"recording_{uuid.uuid4().hex}.webm"
        filepath = os.path.join(upload_dir, filename)

        with open(filepath, 'wb+') as f:
            for chunk in audio_blob.chunks():
                f.write(chunk)

        try:
            recognized_text = process_audio(filepath)

            if not recognized_text:
                return JsonResponse({'success': False, 'error': 'Could not recognize speech'})

            SpeechRecord.objects.create(
                user=request.user,
                audio_file=f'uploads/{filename}',
                recognized_text=recognized_text,
            )

            add_history_entry(
                user=request.user,
                history_type='speech',
                source_text=recognized_text,
            )

            return JsonResponse({'success': True, 'text': recognized_text})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
