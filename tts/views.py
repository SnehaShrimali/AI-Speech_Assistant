from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.contrib import messages
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
