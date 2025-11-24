import speech_recognition as sr
import pyttsx3
import librosa
import sounddevice as sd
import soundfile as sf
import os
import tempfile
import threading
import time
import hashlib
import logging
from config.settings import Settings

logger = logging.getLogger('VoiceAssistant')


class VoiceEngine:
    """Оптимизированный голосовой движок с кешированием"""

    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = None
        self.audio_cache = {}  # Кеш аудио файлов
        self.max_cache_size = 50  # Максимальный размер кеша
        self._init_tts()
        self._init_stt()

    def _init_tts(self):
        """Инициализация синтеза речи"""
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', Settings.VOICE_RATE)
            self.tts_engine.setProperty('volume', Settings.VOICE_VOLUME)

            # Поиск русского голоса
            voices = self.tts_engine.getProperty('voices')
            for voice in voices:
                if 'russian' in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break

            logger.info("TTS система инициализирована")
        except Exception as e:
            logger.error(f"Ошибка инициализации TTS: {e}")
            self.tts_engine = None

    def _init_stt(self):
        """Инициализация распознавания речи"""
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            logger.info("STT система инициализирована")
        except Exception as e:
            logger.error(f"Ошибка инициализации STT: {e}")

    def _get_audio_hash(self, text: str, pitch_shift: int) -> str:
        """Создает хеш для кеширования аудио"""
        return hashlib.md5(f"{text}_{pitch_shift}".encode()).hexdigest()

    def speak(self, text: str):
        """Озвучивает текст с оптимизацией"""
        if not self.tts_engine:
            print(f"🔊 {text}")
            return

        try:
            logger.info(f"Озвучка: {text}")

            # Для коротких ответов используем быстрый метод
            if len(text) < 100:  # Короткие фразы
                self._fast_speak(text)
            else:  # Длинные фразы - используем кеширование
                self._cached_speak(text)

        except Exception as e:
            logger.error(f"Ошибка озвучки: {e}")
            self._fallback_speak(text)

    def _fast_speak(self, text: str):
        """Быстрая озвучка для коротких фраз"""
        try:
            # Создаем аудио в памяти без сохранения в файл
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_filename = temp_file.name

            # Генерируем аудио
            engine = pyttsx3.init()
            engine.setProperty('rate', 200)
            engine.setProperty('volume', 1.0)
            engine.save_to_file(text, temp_filename)
            engine.runAndWait()

            # Быстрая обработка pitch
            y, sr = librosa.load(temp_filename, sr=None)
            y_shifted = librosa.effects.pitch_shift(y, sr=sr, n_steps=Settings.VOICE_PITCH_SHIFT)

            # Воспроизведение в отдельном потоке
            def play_audio():
                try:
                    sd.play(y_shifted, sr)
                    sd.wait()
                finally:
                    if os.path.exists(temp_filename):
                        os.remove(temp_filename)

            threading.Thread(target=play_audio, daemon=True).start()

        except Exception as e:
            logger.error(f"Ошибка быстрой озвучки: {e}")
            self._fallback_speak(text)

    def _cached_speak(self, text: str):
        """Озвучка с кешированием для длинных фраз"""
        audio_hash = self._get_audio_hash(text, Settings.VOICE_PITCH_SHIFT)

        if audio_hash in self.audio_cache:
            # Используем кешированное аудио
            logger.debug("Используется кешированное аудио")
            y_shifted, sr = self.audio_cache[audio_hash]
            threading.Thread(target=sd.play, args=(y_shifted, sr), daemon=True).start()
        else:
            # Генерируем новое аудио
            self._generate_and_cache_audio(text, audio_hash)

    def _generate_and_cache_audio(self, text: str, audio_hash: str):
        """Генерирует и кеширует аудио"""
        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_filename = temp_file.name

            # Генерируем аудио
            engine = pyttsx3.init()
            engine.setProperty('rate', 260)
            engine.setProperty('volume', 1.0)
            engine.save_to_file(text, temp_filename)
            engine.runAndWait()

            # Обрабатываем pitch
            y, sr = librosa.load(temp_filename, sr=None)
            y_shifted = librosa.effects.pitch_shift(y, sr=sr, n_steps=Settings.VOICE_PITCH_SHIFT)

            # Кешируем
            if len(self.audio_cache) >= self.max_cache_size:
                # Удаляем самый старый элемент
                self.audio_cache.pop(next(iter(self.audio_cache)))

            self.audio_cache[audio_hash] = (y_shifted, sr)

            # Воспроизводим
            threading.Thread(target=sd.play, args=(y_shifted, sr), daemon=True).start()

            # Очищаем временный файл
            if os.path.exists(temp_filename):
                os.remove(temp_filename)

        except Exception as e:
            logger.error(f"Ошибка генерации аудио: {e}")
            self._fallback_speak(text)

    def _fallback_speak(self, text: str):
        """Резервный метод озвучки"""
        print(f"🔊 {text}")
        # Пытаемся использовать быстрый TTS без pitch shifting
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except:
            pass

    def listen(self) -> str:
        """Слушает и распознает речь с оптимизацией"""
        try:
            if hasattr(self, '_game_engine') and self._game_engine.game_active:
                print("🎮 Ваш ход...")
            else:
                print("🎤 Слушаю...")

            # Уменьшаем время ожидания для более быстрого ответа
            with self.microphone as source:
                audio = self.recognizer.listen(
                    source,
                    timeout=7,
                    phrase_time_limit=4
                )

            text = self.recognizer.recognize_google(audio, language='ru-RU')
            logger.info(f"Распознано: {text}")
            return text.lower()

        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except Exception as e:
            logger.error(f"Ошибка распознавания: {e}")
            return ""

    def stop(self):
        """Останавливает голосовой движок"""
        if self.tts_engine:
            self.tts_engine.stop()
        try:
            sd.stop()
        except:
            pass