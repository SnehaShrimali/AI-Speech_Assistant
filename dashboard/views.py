from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from speech.models import SpeechRecord
from translation.models import TranslationRecord
from tts.models import TTSRecord
from history.models import HistoryRecord


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['total_speech'] = SpeechRecord.objects.filter(user=user).count()
        context['total_translations'] = TranslationRecord.objects.filter(user=user).count()
        context['total_tts'] = TTSRecord.objects.filter(user=user).count()
        context['recent_history'] = HistoryRecord.objects.filter(user=user)[:10]

        return context
