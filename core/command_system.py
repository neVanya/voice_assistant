import logging
from skills import get_all_skills
from utils.news_service import news_service
from core.game_engine import game_engine
from core.smart_parser import smart_parser
from typing import Dict, Any

logger = logging.getLogger('VoiceAssistant')


class CommandSystem:
    """Система управления командами ассистента с умным парсингом"""

    def __init__(self, memory):
        self.memory = memory
        self.skills = get_all_skills()
        self._setup_special_commands()


        logger.info(f"Загружено {len(self.skills)} навыков")

    def process_command(self, text: str) -> str:
        """Обрабатывает команду и возвращает ответ"""
        text_lower = text.lower()

        # 🔄 ПЕРВЫЙ ПРИОРИТЕТ - игровые команды
        game_response = self._process_game_commands(text_lower)
        if game_response is not None:
            return game_response

        # 1. Проверяем специальные команды
        special_response = self._process_special_commands(text_lower)
        if special_response:
            return special_response


        # 2. 🔥 НОВОЕ: Используем умный парсинг для поиска навыков
        smart_match = self._smart_find_skill(text_lower)
        if smart_match:
            logger.info(f"Умный поиск навыка: {smart_match['skill'].name}")
            try:
                response = smart_match['skill'].execute(text_lower, self.memory)
                return response
            except Exception as e:
                logger.error(f"Ошибка выполнения навыка: {e}")
                return "Произошла ошибка при выполнении команды"

        # 3. 🔥 НОВОЕ: Используем умный парсер для анализа команды
        parsed_command = smart_parser.parse_command(text, {
            "user_name": self.memory.user_name
        })

        if parsed_command["intent"] != "непонятно":
            return self._handle_parsed_intent(parsed_command, text)

        # 4. Старый метод: ищем подходящий навык (для обратной совместимости)
        for skill in self.skills:
            if skill.match(text_lower):
                logger.info(f"Навык найден (старый метод): {skill.name}")
                try:
                    response = skill.execute(text_lower, self.memory)
                    return response
                except Exception as e:
                    logger.error(f"Ошибка выполнения навыка {skill.name}: {e}")
                    return "Произошла ошибка при выполнении команды"

        # 5. Команда не найдена
        return parsed_command["response"]

        # Добавляем специальные команды для управления плагинами

    def _handle_plugins(self, text: str) -> str:
        """Обрабатывает команды управления плагинами"""
        text_lower = text.lower()

        if "список плагинов" in text_lower:
            plugins_info = plugin_system.list_plugins()
            response = "📦 Загруженные плагины:\n\n"

            for plugin in plugins_info:
                status = "✅" if plugin["enabled"] else "❌"
                response += f"{status} {plugin['name']} v{plugin['version']}\n"
                response += f"   Команды: {', '.join(plugin['commands'][:3])}\n\n"

            print(response)
            return "Вывел список плагинов в консоль"

        elif "перезагрузить плагины" in text_lower:
            # Перезагрузка плагинов
            plugin_system.load_plugins()
            return "Плагины перезагружены!"

        return None

    def _smart_find_skill(self, text: str) -> Dict:
        """Умный поиск подходящего навыка"""
        for skill in self.skills:
            # Для каждого навыка проверяем его ключевые слова более гибко
            for keyword in skill.get_keywords():
                if keyword in text:
                    return {
                        "skill": skill,
                        "matched_keyword": keyword,
                        "confidence": 0.9
                    }
        return None

    def _handle_parsed_intent(self, parsed_command: Dict, original_text: str) -> str:
        """Обрабатывает намерения от умного парсера"""
        intent = parsed_command["intent"]

        logger.info(f"Обработка умного намерения: {intent}")

        if intent == "поиск":
            query = parsed_command.get("query", "")
            if query:
                from skills.web_skills import SearchSkill
                return SearchSkill().execute(f"найди {query}", self.memory)
            else:
                return "Что именно вы хотите найти?"

        elif intent == "погода":
            from skills.fun_skills import WeatherSkill
            return WeatherSkill().execute(original_text, self.memory)

        elif intent == "время":
            from skills.time_skills import TimeSkill
            return TimeSkill().execute(original_text, self.memory)

        elif intent == "игра":
            from core.game_engine import game_engine
            return game_engine.start_tic_tac_toe()

        elif intent == "система":
            from skills.system_skills import ApplicationSkill
            return ApplicationSkill().execute(original_text, self.memory)

        elif intent == "скриншот":
            from skills.system_skills import ScreenshotSkill
            return ScreenshotSkill().execute(original_text, self.memory)

        elif intent == "буфер":
            from skills.system_skills import ClipboardSkill
            return ClipboardSkill().execute(original_text, self.memory)

        elif intent == "новости":
            from utils.news_service import news_service
            return news_service.read_news_headlines()

        elif intent == "шутка":
            from skills.fun_skills import JokeSkill
            return JokeSkill().execute(original_text, self.memory)

        elif intent == "youtube":
            query = parsed_command.get("query", "")
            if query:
                from skills.web_skills import YouTubeSkill
                return YouTubeSkill().execute(f"ютуб {query}", self.memory)
            else:
                return "Что вы хотите найти на YouTube?"

        else:
            return parsed_command["response"]

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

        help_text += "\n🔸 УМНЫЙ ПОИСК:\n"
        help_text += "• Говорите естественно - я пойму!\n"
        help_text += "• 'Какая погода в Москве?'\n"
        help_text += "• 'Найди информацию про Python'\n"
        help_text += "• 'Сколько времени?'\n"
        help_text += "• 'Расскажи что-нибудь интересное'\n"
        help_text += "• 'Открой калькулятор'\n"

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
            },
        }