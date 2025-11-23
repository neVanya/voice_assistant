import datetime
from skills.base_skill import BaseSkill


class TimeSkill(BaseSkill):
    """Навык определения времени"""

    def __init__(self):
        super().__init__("Время")

    def get_keywords(self):
        return ["время", "час", "времени", "который час", "сколько времени"]

    def execute(self, command: str, memory):
        now = datetime.datetime.now()
        time_str = now.strftime("%H:%M")
        response = f"Сейчас {time_str}. Хорошего дня!"
        return response  # Просто возвращаем текст


class DateSkill(BaseSkill):
    """Навык определения даты"""

    def __init__(self):
        super().__init__("Дата")

    def get_keywords(self):
        return ["дата", "число", "день", "какое число", "какая дата", "сегодня число"]

    def execute(self, command: str, memory):
        now = datetime.datetime.now()

        months = [
            "января", "февраля", "марта", "апреля", "мая", "июня",
            "июля", "августа", "сентября", "октября", "ноября", "декабря"
        ]

        days = [
            "понедельник", "вторник", "среда", "четверг",
            "пятница", "суббота", "воскресенье"
        ]

        date_str = f"{now.day} {months[now.month - 1]} {now.year} года"
        day_str = days[now.weekday()]

        response = f"Сегодня {day_str}, {date_str}"
        return response  # Просто возвращаем текст