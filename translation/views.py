from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.contrib import messages
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import TranslationRecord
from .services import translate_text, SUPPORTED_LANGUAGES
from history.services import add_history_entry


class TranslateView(LoginRequiredMixin, TemplateView):
    template_name = 'translate.html'

    def post(self, request, *args, **kwargs):
        source_text = request.POST.get('source_text', '').strip()
        target_language = request.POST.get('target_language', '')

        if not source_text:
            messages.error(request, 'Please enter text to translate.')
            return render(request, self.template_name, {
                'languages': SUPPORTED_LANGUAGES,
                'source_text': source_text,
                'target_lang': target_language,
            })

        if not target_language:
            messages.error(request, 'Please select a target language.')
            return render(request, self.template_name, {
                'languages': SUPPORTED_LANGUAGES,
                'source_text': source_text,
                'target_lang': target_language,
            })

        try:
            translated_text = translate_text(source_text, target_language)

            TranslationRecord.objects.create(
                user=request.user,
                source_text=source_text,
                translated_text=translated_text,
                target_language=target_language,
            )

            add_history_entry(
                user=request.user,
                history_type='translation',
                source_text=source_text,
                translated_text=translated_text,
                target_language=target_language,
            )

            messages.success(request, 'Text translated successfully!')
            return render(request, self.template_name, {
                'languages': SUPPORTED_LANGUAGES,
                'source_text': source_text,
                'translated_text': translated_text,
                'target_lang': target_language,
            })

        except Exception as e:
            messages.error(request, f'Translation error: {str(e)}')
            return render(request, self.template_name, {
                'languages': SUPPORTED_LANGUAGES,
                'source_text': source_text,
                'target_lang': target_language,
            })

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['languages'] = SUPPORTED_LANGUAGES
        context['source_text'] = self.request.GET.get('text', '')
        context['translated_text'] = kwargs.get('translated_text', '')
        context['target_lang'] = kwargs.get('target_lang', '')
        return context


class TranslateAPIView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        import json
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        text = data.get('text', '').strip()
        target_lang = data.get('target_lang', 'en')

        if not text:
            return JsonResponse({'error': 'No text provided'}, status=400)
        if target_lang not in SUPPORTED_LANGUAGES:
            return JsonResponse({'error': 'Unsupported language'}, status=400)

        try:
            translated = translate_text(text, target_lang)
            return JsonResponse({
                'success': True,
                'translated': translated,
                'original': text,
                'target_lang': target_lang,
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
