import os
import json
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import TTSRecord
from .services import generate_speech
from translation.services import SUPPORTED_LANGUAGES
from history.services import add_history_entry


class TTSView(LoginRequiredMixin, TemplateView):
    template_name = 'tts.html'

    def post(self, request, *args, **kwargs):
        text = request.POST.get('text', '').strip()
        language = request.POST.get('language', '')

        if not text:
            messages.error(request, 'Please enter text to convert to speech.')
            return render(request, self.template_name, {
                'languages': SUPPORTED_LANGUAGES,
                'text': text,
                'selected_lang': language,
            })

        if not language:
            messages.error(request, 'Please select a language.')
            return render(request, self.template_name, {
                'languages': SUPPORTED_LANGUAGES,
                'text': text,
                'selected_lang': language,
            })

        try:
            relative_path, _ = generate_speech(text, language)

            TTSRecord.objects.create(
                user=request.user,
                text=text,
                audio_file=relative_path,
                language=language,
            )

            add_history_entry(
                user=request.user,
                history_type='tts',
                source_text=text,
                target_language=language,
            )

            messages.success(request, 'Speech generated successfully!')
            return render(request, self.template_name, {
                'languages': SUPPORTED_LANGUAGES,
                'text': text,
                'audio_url': f'/media/{relative_path}',
                'selected_lang': language,
            })

        except Exception as e:
            messages.error(request, f'TTS generation error: {str(e)}')
            return render(request, self.template_name, {
                'languages': SUPPORTED_LANGUAGES,
                'text': text,
                'selected_lang': language,
            })

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['languages'] = SUPPORTED_LANGUAGES
        context['text'] = self.request.GET.get('text', '')
        context['selected_lang'] = self.request.GET.get('lang', '')
        context['audio_url'] = kwargs.get('audio_url', '')
        return context


class TTSAPIView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        text = data.get('text', '').strip()
        language = data.get('language', 'en')
        slow = data.get('slow', False)

        if not text:
            return JsonResponse({'error': 'No text provided'}, status=400)
        if language not in SUPPORTED_LANGUAGES:
            return JsonResponse({'error': 'Unsupported language'}, status=400)

        try:
            relative_path, _ = generate_speech(text, language, slow=slow)

            TTSRecord.objects.create(
                user=request.user,
                text=text,
                audio_file=relative_path,
                language=language,
            )

            add_history_entry(
                user=request.user,
                history_type='tts',
                source_text=text,
                target_language=language,
            )

            return JsonResponse({
                'success': True,
                'audio_url': f'/media/{relative_path}',
                'filename': os.path.basename(relative_path),
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
