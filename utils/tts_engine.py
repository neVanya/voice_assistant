import os

import pyttsx3

from config.settings import Settings


class TTSEngine:
    """Универсальный движок синтеза речи с выбором голоса"""

    def __init__(self, engine_type="pyttsx3"):
        self.engine_type = engine_type
        self.current_voice = Settings.VOICE_PITCH_SHIFT

    def speak(self, text: str):
        """Озвучивает текст выбранным методом"""
        if self.engine_type == "pyttsx3":
            self._speak_pyttsx3(text)
        elif self.engine_type == "sapi5":
            self._speak_sapi5(text)
        elif self.engine_type == "google":
            self._speak_google(text)
        # Добавьте другие методы...

    def _speak_pyttsx3(self, text: str):
        """Ваш текущий код с pitch shifting"""
        # ... ваш существующий код ...
        pass

    def _speak_sapi5(self, text: str):
        """Windows SAPI5 голоса"""
        import pythoncom
        import win32com.client

        pythoncom.CoInitialize()
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        speaker.Speak(text)
        pythoncom.CoUninitialize()

    def _speak_google(self, text: str):
        """Google TTS"""
        from gtts import gTTS
        import pygame
        import tempfile

        tts = gTTS(text=text, lang='ru', slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            tts.save(tmp_file.name)
            pygame.mixer.init()
            pygame.mixer.music.load(tmp_file.name)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)

    def list_voices(self):
        """Показывает доступные голоса"""
        if self.engine_type == "pyttsx3":
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            for i, voice in enumerate(voices):
                print(f"{i}: {voice.name} - {voice.id}")