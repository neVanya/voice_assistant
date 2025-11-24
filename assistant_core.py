import warnings

warnings.filterwarnings("ignore")  # Отключаем предупреждения

import logging
import speech_recognition as sr
from core.voice_engine import VoiceEngine
from core.memory_manager import MemoryManager
from core.command_system import CommandSystem
from core.game_engine import game_engine  # ⬅️ ДОБАВИЛИ ДЛЯ ДОСТУПА К ИГРЕ
from config.settings import Settings

# ⚠️ ИЗМЕНЕННАЯ НАСТРОЙКА ЛОГИРОВАНИЯ - БЕЗ КОНСОЛИ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('assistant.log', encoding='utf-8'),
        # ⬇️ УБРАЛИ StreamHandler - логи не выводятся в консоль
    ]
)

logger = logging.getLogger('VoiceAssistant')


class VoiceAssistant:
    """Главный класс голосового ассистента"""

    def __init__(self):
        self.voice_engine = VoiceEngine()  # ⬅️ Простая инициализация без параметров
        self.memory = MemoryManager()
        self.command_system = CommandSystem(self.memory)

        # Связываем TTS движок с памятью
        self.memory.tts_engine = self.voice_engine

        # Связываем игровой движок
        self.voice_engine._game_engine = game_engine

        logger.info("Голосовой ассистент инициализирован")

    def run(self):
        """Основной цикл работы ассистента"""
        logger.info("Запуск ассистента")

        # Приветственное сообщение с озвучкой
        welcome_text = "Голосовой ассистент запущен! Скажите 'помощь' для списка команд."
        #print(f"🤖 {welcome_text}")
        self.voice_engine.speak(welcome_text)

        try:
            while True:
                # Слушаем команду - вывод "Слушаю..." теперь в voice_engine.listen()
                command = self.voice_engine.listen()

                if not command:
                    continue

                print(f"👤 Вы: {command}")

                # Обрабатываем команду
                response = self.command_system.process_command(command)

                # Проверяем специальные команды
                if response == "STOP":
                    self._shutdown()
                    break

                # Выводим и озвучиваем ответ (ТОЛЬКО ЗДЕСЬ)
                if response and response != "STOP":
                    #print(f"🤖 Ассистент: {response}")

                    # Озвучиваем только если это не команда помощи
                    if not response.startswith("Я вывел список"):
                        self.voice_engine.speak(response)

        except KeyboardInterrupt:
            self._shutdown()
        except Exception as e:
            logger.error(f"Критическая ошибка: {e}")
            self.voice_engine.speak("Произошла ошибка. Перезапустите ассистента.")

    def _show_welcome_help(self):
        """Показывает приветственную справку"""
        help_text = """
🎯 ОСНОВНЫЕ КОМАНДЫ:

⏰ Время и дата:
  • "который час" - узнать время
  • "какая дата" - узнать дату

💻 Система:
  • "открой блокнот" - запустить приложение
  • "сделай скриншот" - снимок экрана
  • "прочитай буфер" - буфер обмена

🌐 Интернет:
  • "найди кошек" - поиск в Google
  • "ютуб музыка" - поиск на YouTube

🌤️ Погода:
  • "погода" - погода в Иваново
  • "погода в москве" - погода в других городах
  • "прогноз погоды" - прогноз

📰 Новости:
  • "новости" - последние новости
  • "новости технологии" - технические новости

🎮 Игры:
  • "крестики нолики" - начать игру
  • "номер 5" - ход в игре
  • "статус игры" - посмотреть поле
  • "выход" - выйти из игры

🎭 Развлечения:
  • "расскажи шутку" - случайная шутка

❓ Помощь:
  • "помощь" - полный список команд
  • "привет" - поздороваться
  • "стоп" - завершить работу

💡 Просто говорите команды - я их услышу!
        """

        print("\n" + "=" * 50)
        print(help_text)
        print("=" * 50 + "\n")

    def _shutdown(self):
        """Корректное завершение работы"""
        logger.info("Завершение работы ассистента")
        goodbye_text = "До свидания! Буду рад помочь снова!"
        #print(f"👋 {goodbye_text}")
        self.voice_engine.speak(goodbye_text)
        self.voice_engine.stop()

    def run_once(self):
        """Запуск для однократной обработки команды"""
        # Вывод "Слушаю..." теперь в voice_engine.listen()
        command = self.voice_engine.listen()

        if command:
            response = self.command_system.process_command(command)
            if response and response != "STOP":
                #print(f"🤖 {response}")
                # Озвучиваем и для однократного режима
                if not response.startswith("Я вывел список"):
                    self.voice_engine.speak(response)
            return response
        return ""