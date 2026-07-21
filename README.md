# AI Speech Assistant

An intelligent speech recognition, translation, and text-to-speech web application built with Django.

## Features

- **Speech Recognition**: Record audio via microphone or upload audio files (WAV, MP3, M4A, OGG, FLAC)
- **Translation**: Translate text to 20+ languages including English, Hindi, Gujarati, French, German, Japanese, etc.
- **Text to Speech**: Convert translated text to natural-sounding speech with play, pause, replay, and download
- **History**: Track all activities with search, filter, and delete capabilities
- **User Authentication**: Register, login, profile management, password change/reset
- **Dashboard**: Overview of usage statistics and recent history

## Tech Stack

- Python 3.13+
- Django 6.0+
- PostgreSQL
- Bootstrap 5
- OpenAI Whisper
- SpeechRecognition
- Google Translate (deep-translator)
- gTTS
- pyttsx3
- pydub

## Installation

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd ai_speech
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. **Create PostgreSQL database**
   ```bash
   createdb ai_speech_db
   ```

6. **Run migrations**
   ```bash
   python manage.py migrate
   ```

7. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```

## Project Structure

```
ai_speech/
├── accounts/           # User authentication & profiles
├── ai_speech/          # Project settings & configuration
├── core/               # Core views (home, etc.)
├── dashboard/          # User dashboard
├── history/            # Activity history
├── speech/             # Speech recognition
├── translation/        # Text translation
├── tts/                # Text to speech
├── media/              # User uploaded/generated files
├── static/             # Static assets (CSS, JS, images)
├── templates/          # HTML templates
├── .env                # Environment variables
└── requirements.txt    # Python dependencies
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `/` | Home page |
| `/accounts/` | Authentication (register, login, profile) |
| `/dashboard/` | User dashboard |
| `/speech/` | Speech recognition |
| `/translate/` | Text translation |
| `/tts/` | Text to speech |
| `/history/` | Activity history |
| `/admin/` | Django admin panel |

## License

MIT
