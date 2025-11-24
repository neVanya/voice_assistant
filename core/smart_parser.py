import logging
import re
from typing import Dict, Any, List, Tuple

logger = logging.getLogger('VoiceAssistant')


class SmartCommandParser:
    """Умный парсер команд с пониманием контекста"""

    def __init__(self):
        self.command_patterns = self._init_command_patterns()
        self.conversation_context = []

    def _init_command_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Инициализация шаблонов команд"""

        return {
            "поиск": {
                "keywords": ["найди", "поищи", "найти", "ищи", "что такое", "кто такой",
                             "расскажи про", "информация о", "что значит", "определение"],
                "confidence": 0.9,
                "extract_query": True,
                "response": "Ищу информацию: {query}"
            },
            "погода": {
                "keywords": ["погод", "температур", "градус", "холодно", "жарко", "дождь",
                             "снег", "солнечн", "облачн", "прогноз погоды"],
                "confidence": 0.95,
                "extract_city": True,
                "response": "Узнаю погоду для {city}"
            },
            "время": {
                "keywords": ["врем", "час", "который час", "сколько времени", "дата",
                             "число", "сегодня число", "текущее время"],
                "confidence": 0.98,
                "response": "Скажу текущее время и дату!"
            },
            "игра": {
                "keywords": ["игра", "крестик", "нолик", "сыграем", "поиграем",
                             "начать игру", "хочу играть", "давай поиграем"],
                "confidence": 0.9,
                "response": "Начинаю игру в крестики-нолики!"
            },
            "система": {
                "keywords": ["открой", "запусти", "включи", "блокнот", "калькулятор",
                             "браузер", "проводник", "панель управления"],
                "confidence": 0.85,
                "response": "Выполняю системную команду!"
            },
            "скриншот": {
                "keywords": ["сделай скриншот", "сними скрин", "скриншот", "фото экрана"],
                "confidence": 0.95,
                "response": "Делаю скриншот экрана!"
            },
            "буфер": {
                "keywords": ["буфер обмена", "что в буфере", "прочитай буфер", "скопируй в буфер"],
                "confidence": 0.88,
                "response": "Работаю с буфером обмена!"
            },
            "новости": {
                "keywords": ["новост", "что нового", "события", "последние новости",
                             "что в мире", "свежие новости"],
                "confidence": 0.9,
                "response": "Рассказываю последние новости!"
            },
            "шутка": {
                "keywords": ["шутка", "пошути", "рассмеши", "расскажи шутку", "анекдот"],
                "confidence": 0.92,
                "response": "Рассказываю шутку!"
            },
            "youtube": {
                "keywords": ["ютуб", "youtube", "видео", "найди на ютуб", "поищи видео"],
                "confidence": 0.87,
                "extract_query": True,
                "response": "Ищу на YouTube: {query}"
            }
        }

    def parse_command(self, command: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Анализирует команду и возвращает структурированный результат
        """
        command_lower = command.lower()

        # Ищем подходящий паттерн команды
        best_match = None
        highest_confidence = 0

        for intent, pattern in self.command_patterns.items():
            confidence = self._calculate_confidence(command_lower, pattern)

            if confidence > highest_confidence and confidence > 0.5:
                highest_confidence = confidence
                best_match = {
                    "intent": intent,
                    "confidence": confidence,
                    "pattern": pattern,
                    "original_command": command
                }

        if best_match:
            # Извлекаем дополнительные параметры
            best_match = self._extract_parameters(best_match, command_lower)
            logger.info(f"Умный парсинг: {best_match['intent']} (уверенность: {best_match['confidence']:.2f})")
            return best_match

        # Если команда не распознана
        return {
            "intent": "непонятно",
            "confidence": 0.3,
            "response": self._generate_unknown_response(command),
            "original_command": command
        }

    def _calculate_confidence(self, command: str, pattern: Dict[str, Any]) -> float:
        """Вычисляет уверенность в совпадении команды"""
        base_confidence = pattern["confidence"]
        keyword_matches = 0

        # Проверяем ключевые слова
        for keyword in pattern["keywords"]:
            if keyword in command:
                keyword_matches += 1

        # Чем больше ключевых слов совпало - тем выше уверенность
        if keyword_matches > 0:
            confidence_boost = min(0.3, keyword_matches * 0.1)
            return min(1.0, base_confidence + confidence_boost)

        return 0.0

    def _extract_parameters(self, match: Dict[str, Any], command: str) -> Dict[str, Any]:
        """Извлекает параметры из команды"""
        pattern = match["pattern"]

        # Извлекаем поисковый запрос
        if pattern.get("extract_query", False):
            query = self._extract_search_query(command, pattern["keywords"])
            match["query"] = query
            match["response"] = pattern["response"].format(query=query)

        # Извлекаем город для погоды
        elif pattern.get("extract_city", False):
            city = self._extract_city(command)
            match["city"] = city
            match["response"] = pattern["response"].format(city=city)

        else:
            match["response"] = pattern["response"]

        return match

    def _extract_search_query(self, command: str, keywords: List[str]) -> str:
        """Извлекает поисковый запрос из команды"""
        # Удаляем ключевые слова из команды
        clean_command = command.lower()
        for keyword in keywords:
            clean_command = clean_command.replace(keyword, "")

        # Удаляем лишние слова
        stop_words = ['в', 'интернете', 'википедии', 'про', 'о', 'на', 'за']
        words = clean_command.split()
        clean_words = [word for word in words if word not in stop_words and len(word) > 2]

        return ' '.join(clean_words).strip()

    def _extract_city(self, command: str) -> str:
        """Извлекает город из команды о погоде"""
        cities = {
            'москв': 'Москве',
            'питер': 'Санкт-Петербурге',
            'спб': 'Санкт-Петербурге',
            'санкт-петербург': 'Санкт-Петербурге',
            'ярослав': 'Ярославле',
            'костр': 'Костроме',
            'владимир': 'Владимире',
            'казан': 'Казани',
            'новгород': 'Нижнем Новгороде',
            'иванов': 'Иваново'
        }

        for city_key, city_name in cities.items():
            if city_key in command:
                return city_name

        return "Иваново"

    def _generate_unknown_response(self, command: str) -> str:
        """Генерирует ответ для непонятной команды"""
        responses = [
            f"Извините, я не понял команду '{command}'. Скажите 'помощь' для списка команд.",
            f"Не уверен что вы имели в виду под '{command}'. Попробуйте сказать команду четче.",
            f"Простите, не распознал команду. Скажите 'помощь' чтобы узнать что я умею.",
        ]

        import random
        return random.choice(responses)

    def add_context(self, user_command: str, ai_response: str, intent: str):
        """Добавляет контекст для будущего анализа"""
        self.conversation_context.append({
            "user": user_command,
            "response": ai_response,
            "intent": intent,
            "timestamp": len(self.conversation_context)
        })

        # Ограничиваем размер контекста
        if len(self.conversation_context) > 5:
            self.conversation_context.pop(0)


# Глобальный экземпляр
smart_parser = SmartCommandParser()