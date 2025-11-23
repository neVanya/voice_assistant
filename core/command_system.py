import logging
from skills import get_all_skills
from utils.news_service import news_service
from core.game_engine import game_engine

logger = logging.getLogger('VoiceAssistant')


class CommandSystem:
    """Система управления командами ассистента"""

    def __init__(self, memory):
        self.memory = memory
        self.skills = get_all_skills()
        self._setup_special_commands()
        logger.info(f"Загружено {len(self.skills)} навыков")


    def process_command(self, text: str) -> str:
        """Обрабатывает команду и возвращает ответ (БЕЗ озвучивания)"""
        text_lower = text.lower()

        # 🔄 ПЕРВЫЙ ПРИОРИТЕТ - игровые команды
        game_response = self._process_game_commands(text_lower)
        if game_response is not None:
            return game_response

        # 1. Проверяем специальные команды
        special_response = self._process_special_commands(text_lower)
        if special_response:
            return special_response

        # 2. Ищем подходящий навык
        for skill in self.skills:
            if skill.match(text_lower):
                logger.info(f"Навык найден: {skill.name}")
                try:
                    response = skill.execute(text_lower, self.memory)
                    return response
                except Exception as e:
                    logger.error(f"Ошибка выполнения навыка {skill.name}: {e}")
                    return "Произошла ошибка при выполнении команды"

        # 3. Команда не найдена
        return "Извините, я не понял команду. Скажите 'помощь' для списка команд."

    def _process_game_commands(self, text: str) -> str:
        """Обрабатывает игровые команды"""
        # Если игра активна - все команды идут в игру
        if game_engine.game_active:
            response, game_continues = game_engine.process_game_input(text)
            return response

        # Команды начала игр
        if any(word in text for word in ['крестики нолики', 'начать игру', 'играть в крестики']):
            return game_engine.start_tic_tac_toe()

        # Команды статуса игр
        if any(word in text for word in ['статус игры', 'ход игры', 'поле', 'доска']):
            return game_engine.get_game_status()

        return None

    def _process_special_commands(self, text: str) -> str:
        """Обрабатывает специальные команды"""
        for command_type, config in self.special_commands.items():
            if any(keyword in text for keyword in config["keywords"]):
                return config["handler"](text)
        return None

    def _handle_help(self, text: str) -> str:
        """Обрабатывает команду помощи"""
        help_text = "Вот что я умею:\n\n"

        # Добавляем специальные команды
        help_text += "🔸 ОСНОВНЫЕ КОМАНДЫ:\n"
        help_text += "• помощь, команды - этот список\n"
        help_text += "• привет - поздороваться\n"
        help_text += "• моё имя [имя] - запомнить имя\n"
        help_text += "• новости - последние новости\n"
        help_text += "• стоп - завершить работу\n\n"

        # Добавляем навыки
        help_text += "🔸 НАВЫКИ:\n"
        for skill in self.skills:
            help_text += f"• {skill.get_description()}\n"

        print(f"\n{'=' * 50}")
        print(help_text)
        print(f"{'=' * 50}\n")

        return "Я вывел список команд в консоль. Чем еще могу помочь?"

    def _handle_exit(self, text: str) -> str:
        """Обрабатывает команду выхода"""
        return "STOP"

    def _handle_greeting(self, text: str) -> str:
        """Обрабатывает приветствие"""
        if self.memory.user_name:
            return f"Привет, {self.memory.user_name}! Рад тебя слышать!"
        return "Привет! Я ваш голосовой ассистент. Чем могу помочь?"

    def _handle_name(self, text: str) -> str:
        """Обрабатывает команду имени"""
        if 'зовут' in text:
            name = text.split('зовут')[-1].strip()
        elif 'имя' in text:
            name = text.split('имя')[-1].strip()
        else:
            return "Скажите 'моё имя [ваше имя]'"

        return self.memory.remember_name(name)

    def _handle_news(self, text: str) -> str:
        """Обрабатывает запрос новостей"""
        categories = {
            "технологии": "technology",
            "политика": "politics",
            "экономика": "economics",
            "город": "ivanovo",
            "все": "general"
        }

        # Определяем категорию из текста
        category = "general"
        for cat_ru, cat_en in categories.items():
            if cat_ru in text:
                category = cat_en
                break

        return news_service.read_news_headlines(category, 3)

    def _setup_special_commands(self):
        """Настройка специальных команд"""
        self.special_commands = {
            "help": {
                "keywords": ["помощь", "команды", "что ты умеешь"],
                "handler": self._handle_help
            },
            "exit": {
                "keywords": ["стоп", "выход", "пока", "заверши работу"],
                "handler": self._handle_exit
            },
            "greeting": {
                "keywords": ["привет", "здравствуй", "добрый день", "хай"],
                "handler": self._handle_greeting
            },
            "name": {
                "keywords": ["моё имя", "зовут", "запомни имя"],
                "handler": self._handle_name
            },
            "news": {
                "keywords": ["новости", "что нового", "свежие новости", "последние новости"],
                "handler": self._handle_news
            }
        }

