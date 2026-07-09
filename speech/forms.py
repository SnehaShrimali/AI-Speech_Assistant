import os
from django import forms
from .models import SpeechRecord
from .services import validate_audio_file, SUPPORTED_AUDIO_EXTENSIONS, LANGUAGE_CODES


class AudioUploadForm(forms.Form):
    audio_file = forms.FileField(
        label='Choose Audio File',
        help_text=f'Supported: {", ".join(sorted(SUPPORTED_AUDIO_EXTENSIONS))}',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': ','.join(SUPPORTED_AUDIO_EXTENSIONS),
        })
    )
    language = forms.ChoiceField(
        choices=[('auto', 'Auto Detect')] + [(k, v) for k, v in LANGUAGE_CODES.items()],
        required=False,
        initial='auto',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def clean_audio_file(self):
        uploaded_file = self.cleaned_data['audio_file']
        try:
            validate_audio_file(uploaded_file)
        except ValueError as e:
            raise forms.ValidationError(str(e))
        return uploaded_file
