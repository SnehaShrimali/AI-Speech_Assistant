from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.contrib import messages
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import TranslationRecord
from .services import translate_text, SUPPORTED_LANGUAGES, detect_language_with_confidence
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
            detected = detect_language_with_confidence(source_text)
            source_lang = detected['language']

            translated_text = translate_text(source_text, target_language, source_language=source_lang)

            TranslationRecord.objects.create(
                user=request.user,
                source_text=source_text,
                translated_text=translated_text,
                source_language=source_lang,
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
                'detected_lang': detected['language'],
                'detected_lang_name': detected['language_name'],
                'detected_confidence': detected['confidence'],
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
        context['detected_lang'] = kwargs.get('detected_lang', '')
        context['detected_lang_name'] = kwargs.get('detected_lang_name', '')
        context['detected_confidence'] = kwargs.get('detected_confidence', 0)
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
        source_lang = data.get('source_lang', 'auto')

        if not text:
            return JsonResponse({'error': 'No text provided'}, status=400)
        if target_lang not in SUPPORTED_LANGUAGES:
            return JsonResponse({'error': 'Unsupported language'}, status=400)

        try:
            detected = detect_language_with_confidence(text)
            detected_code = detected['language']
            actual_source = source_lang if source_lang != 'auto' else detected_code

            translated = translate_text(text, target_lang, source_language=actual_source)

            return JsonResponse({
                'success': True,
                'translated': translated,
                'original': text,
                'target_lang': target_lang,
                'source_lang': source_lang,
                'detected_lang': detected['language'],
                'detected_lang_name': detected['language_name'],
                'detected_confidence': detected['confidence'],
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class LanguageDetectAPIView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        import json
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        text = data.get('text', '').strip()
        if not text:
            return JsonResponse({'error': 'No text provided'}, status=400)

        try:
            detected = detect_language_with_confidence(text)
            return JsonResponse({
                'success': True,
                'detected_lang': detected['language'],
                'detected_lang_name': detected['language_name'],
                'confidence': detected['confidence'],
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)