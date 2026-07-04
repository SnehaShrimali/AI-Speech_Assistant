from django.db import models
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages
from .models import HistoryRecord


class HistoryView(LoginRequiredMixin, ListView):
    model = HistoryRecord
    template_name = 'history.html'
    context_object_name = 'history_items'
    paginate_by = 20

    def get_queryset(self):
        queryset = HistoryRecord.objects.filter(user=self.request.user)

        query = self.request.GET.get('q', '')
        filter_type = self.request.GET.get('type', '')

        if query:
            queryset = queryset.filter(
                models.Q(source_text__icontains=query) |
                models.Q(translated_text__icontains=query)
            )

        if filter_type:
            queryset = queryset.filter(type=filter_type)

        return queryset

    def post(self, request, *args, **kwargs):
        delete_id = request.POST.get('delete_id')
        if delete_id:
            try:
                record = HistoryRecord.objects.get(id=delete_id, user=request.user)
                if record.audio_file:
                    import os
                    if os.path.exists(record.audio_file.path):
                        os.remove(record.audio_file.path)
                record.delete()
                messages.success(request, 'Record deleted successfully.')
            except HistoryRecord.DoesNotExist:
                messages.error(request, 'Record not found.')
        return redirect('history:history')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['filter_type'] = self.request.GET.get('type', '')
        return context


