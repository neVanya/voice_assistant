from skills.base_skill import BaseSkill
from core.game_engine import game_engine


class GameSkill(BaseSkill):
    """Навык для управления играми"""

    def __init__(self):
        super().__init__("Игры")

    def get_keywords(self):
        return [
            "крестики нолики", "начать игру", "играть в крестики", "хочу играть",
            "статус игры", "ход игры", "поле", "доска", "какое поле"
        ]

    def execute(self, command: str, memory):
        command_lower = command.lower()

        # Команды начала игры
        if any(word in command_lower for word in ['крестики нолики', 'начать игру', 'играть в крестики']):
            return game_engine.start_tic_tac_toe()

        # Команды статуса игры
        if any(word in command_lower for word in ['статус игры', 'ход игры', 'поле', 'доска']):
            return game_engine.get_game_status()

        return "Скажите 'крестики нолики' чтобы начать игру."