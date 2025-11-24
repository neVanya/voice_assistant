import re
from core.plugin_base import BasePlugin


class CalculatorPlugin(BasePlugin):
    """Плагин калькулятора"""

    def __init__(self):
        super().__init__("Калькулятор", "1.0")

    def get_commands(self) -> list:
        return [
            "посчитай",
            "сколько будет",
            "вычисли",
            "реши пример"
        ]

    def execute(self, command: str, memory, **kwargs) -> str:
        command_lower = command.lower()

        if "сколько будет" in command_lower:
            expression = command_lower.split("сколько будет")[-1].strip()
        elif "посчитай" in command_lower:
            expression = command_lower.split("посчитай")[-1].strip()
        else:
            expression = command_lower

        try:
            # Безопасное вычисление
            expression = self._sanitize_expression(expression)
            result = eval(expression)
            return f"Результат: {expression} = {result}"
        except:
            return "Не могу вычислить это выражение"

    def _sanitize_expression(self, expression: str) -> str:
        """Очищает выражение для безопасного вычисления"""
        # Разрешаем только цифры, основные операторы и пробелы
        safe_chars = r'[0-9+\-*/(). ]'
        cleaned = ''.join(re.findall(safe_chars, expression))
        return cleaned