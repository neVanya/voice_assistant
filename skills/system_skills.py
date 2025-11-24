import os
import subprocess
from skills.base_skill import BaseSkill


class ApplicationSkill(BaseSkill):
    """Навык открытия приложений"""

    def __init__(self):
        super().__init__("Приложения")

    def get_keywords(self):
        return [
            "открой", "запусти", "включи",
            "блокнот", "калькулятор", "браузер", "проводник"
        ]

    def execute(self, command: str, memory):
        command_lower = command.lower()

        app_mappings = {
            "блокнот": ("notepad", "Блокнот"),
            "калькулятор": ("calc", "Калькулятор"),
            "браузер": ("chrome", "Браузер"),
            "проводник": ("explorer", "Проводник"),
            "панель управления": ("control", "Панель управления")
        }

        for app_name, (app_command, app_display) in app_mappings.items():
            if app_name in command_lower:
                try:
                    os.system(app_command)
                    response = f"Открываю {app_display}"
                    return response
                except Exception as e:
                    response = f"Не удалось открыть {app_display}"
                    return response

        return "Какое приложение открыть? Я умею открывать блокнот, калькулятор, браузер и проводник."


class ScreenshotSkill(BaseSkill):
    """Навык создания скриншотов"""

    def __init__(self):
        super().__init__("Скриншот")

    def get_keywords(self):
        return ["сделай скриншот", "сними скрин", "скриншот", "фото экрана"]

    def execute(self, command: str, memory):
        try:
            import pyautogui
            screenshot = pyautogui.screenshot()
            screenshot_path = "data/screenshot.png"
            screenshot.save(screenshot_path)
            response = f"Сделал скриншот экрана и сохранил его как {screenshot_path}"
            return response
        except Exception as e:
            response = "Не удалось сделать скриншот. Установите модуль Pillow"
            return response


class ClipboardSkill(BaseSkill):
    """Навык работы с буфером обмена"""

    def __init__(self):
        super().__init__("Буфер обмена")

    def get_keywords(self):
        return ["буфер обмена", "что в буфере", "прочитай буфер", "скопируй в буфер"]

    def execute(self, command: str, memory):
        try:
            import pyperclip

            command_lower = command.lower()

            if any(word in command_lower for word in ["прочитай", "что в"]):
                text = pyperclip.paste()
                if text:
                    # Ограничиваем длину для озвучки
                    if len(text) > 100:
                        response = f"В буфере обмена длинный текст. Начинается так: {text[:100]}..."
                    else:
                        response = f"В буфере обмена: {text}"
                else:
                    response = "Буфер обмена пуст"

            elif any(word in command_lower for word in ["скопируй", "запиши"]):
                # Упрощенная логика извлечения текста
                words = command_lower.split()
                if len(words) > 1:
                    text_to_copy = " ".join(words[3:])
                    pyperclip.copy(text_to_copy)
                    response = f"Скопировал в буфер обмена: {text_to_copy}"
                else:
                    response = "Не указано, что копировать"
            else:
                response = "Скажите 'прочитай буфер' или 'скопируй [текст]'"

            return self.speak_response(response, memory.tts_engine)

        except ImportError:
            response = "Для работы с буфером обмена установите модуль pyperclip"
            return response