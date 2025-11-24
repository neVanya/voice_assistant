import os
import subprocess
import psutil
import platform
from skills.base_skill import BaseSkill


class ApplicationSkill(BaseSkill):
    """Расширенный навык управления приложениями"""

    def __init__(self):
        super().__init__("Приложения")
        self.app_mappings = self._init_app_mappings()

    def _init_app_mappings(self):
        """Инициализация сопоставления приложений"""
        system = platform.system()

        if system == "Windows":
            return {
                # Офисные приложения
                "блокнот": ("notepad", "Блокнот"),
                "word": ("winword", "Microsoft Word"),
                "excel": ("excel", "Microsoft Excel"),
                "powerpoint": ("powerpnt", "Microsoft PowerPoint"),
                "калькулятор": ("calc", "Калькулятор"),

                # Браузеры
                "браузер": ("chrome", "Google Chrome"),
                "chrome": ("chrome", "Google Chrome"),
                "edge": ("msedge", "Microsoft Edge"),
                "firefox": ("firefox", "Mozilla Firefox"),
                "opera": ("opera", "Opera Browser"),

                # Системные утилиты
                "проводник": ("explorer", "Проводник"),
                "диспетчер задач": ("taskmgr", "Диспетчер задач"),
                "командная строка": ("cmd", "Командная строка"),
                "powershell": ("powershell", "Windows PowerShell"),
                "панель управления": ("control", "Панель управления"),
                "реестр": ("regedit", "Редактор реестра"),

                # Мультимедиа
                "медиаплеер": ("wmplayer", "Windows Media Player"),
                "кино и тв": ("movies", "Приложение Кино и ТВ"),
                "камера": ("camera", "Камера"),
                "диктофон": ("soundrecorder", "Диктофон"),

                # Графические редакторы
                "paint": ("mspaint", "Paint"),
                "фотографии": ("photos", "Приложение Фотографии"),

                # Сообщения и почта
                "почта": ("outlook", "Почта"),
                "календарь": ("outlookcal", "Календарь"),
                "теams": ("teams", "Microsoft Teams"),
                "skype": ("skype", "Skype"),
                "discord": ("discord", "Discord"),

                # Разработка
                "visual studio": ("devenv", "Visual Studio"),
                "vscode": ("code", "Visual Studio Code"),
                "pycharm": ("pycharm", "PyCharm"),
                "notepad++": ("notepad++", "Notepad++"),

                # Другое
                "zoom": ("zoom", "Zoom"),
                "steam": ("steam", "Steam"),
                "торрент": ("utorrent", "uTorrent")
            }
        else:  # Linux/Mac
            return {
                "браузер": ("google-chrome", "Браузер"),
                "калькулятор": ("gnome-calculator", "Калькулятор"),
                "текстовый редактор": ("gedit", "Текстовый редактор"),
                "терминал": ("gnome-terminal", "Терминал"),
            }

    def get_keywords(self):
        return [
            "открой", "запусти", "включи", "открыть", "запустить",
            "блокнот", "калькулятор", "браузер", "проводник", "word", "excel",
            "powerpoint", "paint", "диспетчер задач", "командная строка",
            "почта", "календарь", "skype", "discord", "steam", "zoom",
            "vscode", "pycharm", "notepad++", "visual studio"
        ]

    def execute(self, command: str, memory):
        command_lower = command.lower()

        # Поиск приложения по ключевым словам
        for app_name, (app_command, app_display) in self.app_mappings.items():
            if app_name in command_lower:
                try:
                    # Пробуем разные способы запуска
                    success = self._launch_application(app_command, app_name)
                    if success:
                        return f"✅ Открываю {app_display}"
                    else:
                        return f"❌ Не удалось открыть {app_display}. Приложение не установлено или недоступно."
                except Exception as e:
                    return f"❌ Ошибка при открытии {app_display}"

        # Если приложение не найдено, предлагаем варианты
        return self._suggest_applications(command_lower)

    def _launch_application(self, app_command: str, app_name: str) -> bool:
        """Запускает приложение разными способами"""
        try:
            # Способ 1: Через os.system
            result = os.system(f'start "" "{app_command}"' if platform.system() == "Windows" else app_command)
            if result == 0:
                return True
        except:
            pass

        try:
            # Способ 2: Через subprocess
            subprocess.Popen(app_command, shell=True)
            return True
        except:
            pass

        try:
            # Способ 3: Поиск в PATH
            subprocess.Popen([app_command], shell=True)
            return True
        except:
            pass

        return False

    def _suggest_applications(self, command: str) -> str:
        """Предлагает приложения на основе похожих команд"""
        suggestions = {
            "офис": ["word", "excel", "powerpoint"],
            "игр": ["steam"],
            "сообщен": ["skype", "discord", "teams"],
            "разработ": ["vscode", "pycharm", "visual studio"],
            "музык": ["медиаплеер"],
            "видео": ["кино и тв"],
            "фото": ["paint", "фотографии"],
            "систем": ["диспетчер задач", "панель управления", "реестр"]
        }

        for category, apps in suggestions.items():
            if category in command:
                app_list = ", ".join([self.app_mappings[app][1] for app in apps if app in self.app_mappings])
                return f"Возможно, вы хотите открыть: {app_list}"

        # Показываем популярные приложения
        popular_apps = ["Блокнот", "Калькулятор", "Браузер", "Проводник", "Word", "Excel"]
        return f"Какое приложение открыть? Популярные: {', '.join(popular_apps)}"


class ProcessSkill(BaseSkill):
    """Навык управления процессами"""

    def __init__(self):
        super().__init__("Процессы")

    def get_keywords(self):
        return [
            "закрой приложение", "заверши процесс", "закрой программу",
            "какие приложения открыты", "список процессов", "диспетчер задач",
            "закрой все приложения", "останови программу"
        ]

    def execute(self, command: str, memory):
        command_lower = command.lower()

        if any(word in command_lower for word in ["какие приложения", "список процессов", "диспетчер задач"]):
            return self._list_processes()

        elif any(word in command_lower for word in ["закрой приложение", "заверши процесс", "закрой программу"]):
            return self._close_application(command)

        elif "закрой все приложения" in command_lower:
            return self._close_all_user_apps()

        return "Скажите 'закрой [название программы]' или 'покажи запущенные приложения'"

    def _list_processes(self) -> str:
        """Показывает список запущенных процессов"""
        try:
            user_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
                try:
                    if proc.info['memory_info']:  # Фильтруем системные процессы
                        user_processes.append(proc)
                except:
                    continue

            # Берем топ-10 процессов по использованию памяти
            user_processes.sort(key=lambda x: x.info['memory_info'].rss if x.info['memory_info'] else 0, reverse=True)

            response = "📊 Запущенные приложения (топ-10):\n\n"
            for proc in user_processes[:10]:
                mem_mb = proc.info['memory_info'].rss / 1024 / 1024 if proc.info['memory_info'] else 0
                response += f"• {proc.info['name']} (PID: {proc.info['pid']}) - {mem_mb:.1f} MB\n"

            print(response)
            return "Вывел список процессов в консоль"

        except Exception as e:
            return f"Ошибка получения списка процессов: {e}"

    def _close_application(self, command: str) -> str:
        """Закрывает указанное приложение"""
        try:
            # Извлекаем название приложения из команды
            words = command.lower().split()
            close_keywords = ["закрой", "заверши", "останови"]
            app_name = next((word for word in words if word not in close_keywords), None)

            if not app_name:
                return "Укажите название приложения для закрытия"

            # Ищем процесс
            for proc in psutil.process_iter(['pid', 'name']):
                if app_name.lower() in proc.info['name'].lower():
                    proc.terminate()
                    return f"✅ Закрыл приложение: {proc.info['name']}"

            return f"❌ Не нашел запущенное приложение: {app_name}"

        except Exception as e:
            return f"❌ Ошибка при закрытии приложения: {e}"

    def _close_all_user_apps(self) -> str:
        """Закрывает все пользовательские приложения"""
        try:
            closed_count = 0
            system_processes = ['svchost.exe', 'explorer.exe', 'winlogon.exe', 'csrss.exe']

            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if (proc.info['name'].endswith('.exe') and
                            proc.info['name'].lower() not in system_processes and
                            proc.info['name'].lower() not in ['python.exe', 'cmd.exe']):
                        proc.terminate()
                        closed_count += 1
                except:
                    continue

            return f"✅ Закрыл {closed_count} пользовательских приложений"

        except Exception as e:
            return f"❌ Ошибка при закрытии приложений: {e}"


class SystemInfoSkill(BaseSkill):
    """Навык получения системной информации"""

    def __init__(self):
        super().__init__("Системная информация")

    def get_keywords(self):
        return [
            "системная информация", "характеристики пк", "информация о системе",
            "сколько памяти", "загрузка процессора", "состояние батареи",
            "свободное место", "версия windows", "информация о дисках"
        ]

    def execute(self, command: str, memory):
        command_lower = command.lower()

        if any(word in command_lower for word in ["системная информация", "характеристики пк"]):
            return self._get_system_info()

        elif "сколько памяти" in command_lower or "загрузка процессора" in command_lower:
            return self._get_performance_info()

        elif "состояние батареи" in command_lower:
            return self._get_battery_info()

        elif "свободное место" in command_lower or "информация о дисках" in command_lower:
            return self._get_disk_info()

        elif "версия windows" in command_lower:
            return self._get_windows_version()

        return "Какую системную информацию показать?"

    def _get_system_info(self) -> str:
        """Получает общую системную информацию"""
        try:
            info = f"""
💻 СИСТЕМНАЯ ИНФОРМАЦИЯ:

🖥️ Система: {platform.system()} {platform.release()}
⚙️ Процессор: {platform.processor()}
💾 Память: {psutil.virtual_memory().total / 1024 / 1024 / 1024:.1f} GB
📀 Диски: {len(psutil.disk_partitions())} разделов
"""
            print(info)
            return "Вывел системную информацию в консоль"

        except Exception as e:
            return f"Ошибка получения системной информации: {e}"

    def _get_performance_info(self) -> str:
        """Получает информацию о производительности"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()

            response = f"""
📊 ПРОИЗВОДИТЕЛЬНОСТЬ:

🔄 Загрузка CPU: {cpu_percent}%
💾 Использовано памяти: {memory.percent}% ({memory.used / 1024 / 1024 / 1024:.1f} GB / {memory.total / 1024 / 1024 / 1024:.1f} GB)
"""
            return response

        except Exception as e:
            return f"Ошибка получения информации о производительности: {e}"

    def _get_battery_info(self) -> str:
        """Получает информацию о батарее"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                status = "⚡ Заряжается" if battery.power_plugged else "🔋 От батареи"
                return f"{status}\nУровень заряда: {battery.percent}%\nОсталось времени: {battery.secsleft // 3600} ч {(battery.secsleft % 3600) // 60} м"
            else:
                return "🔌 Батарея не обнаружена (возможно, ПК подключен к сети)"

        except Exception as e:
            return f"Ошибка получения информации о батарее: {e}"

    def _get_disk_info(self) -> str:
        """Получает информацию о дисках"""
        try:
            response = "📀 ИНФОРМАЦИЯ О ДИСКАХ:\n\n"
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    free_gb = usage.free / 1024 / 1024 / 1024
                    total_gb = usage.total / 1024 / 1024 / 1024
                    percent_used = usage.percent

                    response += f"• {partition.device} ({partition.fstype})\n"
                    response += f"  Свободно: {free_gb:.1f} GB / {total_gb:.1f} GB ({100 - percent_used:.1f}% свободно)\n\n"
                except:
                    continue

            print(response)
            return "Вывел информацию о дисках в консоль"

        except Exception as e:
            return f"Ошибка получения информации о дисках: {e}"

    def _get_windows_version(self) -> str:
        """Получает версию Windows"""
        try:
            return f"🪟 Версия Windows: {platform.system()} {platform.release()} {platform.version()}"
        except:
            return "Не удалось определить версию системы"


class ScreenshotSkill(BaseSkill):
    """Улучшенный навык создания скриншотов"""

    def __init__(self):
        super().__init__("Скриншот")

    def get_keywords(self):
        return [
            "сделай скриншот", "сними скрин", "скриншот", "фото экрана",
            "снимок экрана", "заскринь"
        ]

    def execute(self, command: str, memory):
        try:
            import pyautogui
            from datetime import datetime

            # Создаем папку для скриншотов если её нет
            screenshots_dir = "screenshots"
            os.makedirs(screenshots_dir, exist_ok=True)

            # Генерируем имя файла с timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = os.path.join(screenshots_dir, f"screenshot_{timestamp}.png")

            # Делаем скриншот
            screenshot = pyautogui.screenshot()
            screenshot.save(screenshot_path)

            response = f"✅ Сделал скриншот экрана и сохранил как: {screenshot_path}"
            return response

        except ImportError:
            return "❌ Для создания скриншотов установите модуль: pip install pyautogui pillow"
        except Exception as e:
            return f"❌ Не удалось сделать скриншот: {e}"


class ClipboardSkill(BaseSkill):
    """Улучшенный навык работы с буфером обмена"""

    def __init__(self):
        super().__init__("Буфер обмена")

    def get_keywords(self):
        return [
            "буфер обмена", "что в буфере", "прочитай буфер", "скопируй в буфер",
            "очисти буфер", "история буфера", "вставь из буфера"
        ]

    def execute(self, command: str, memory):
        try:
            import pyperclip

            command_lower = command.lower()

            if any(word in command_lower for word in ["прочитай", "что в"]):
                text = pyperclip.paste()
                if text:
                    if len(text) > 200:
                        response = f"📋 В буфере обмена длинный текст:\n{text[:200]}..."
                    else:
                        response = f"📋 В буфере обмена: {text}"
                else:
                    response = "📋 Буфер обмена пуст"

            elif any(word in command_lower for word in ["скопируй", "запиши"]):
                text_to_copy = command_lower.replace("скопируй", "").replace("запиши в буфер", "").strip()
                if text_to_copy:
                    pyperclip.copy(text_to_copy)
                    response = f"✅ Скопировал в буфер обмена: {text_to_copy}"
                else:
                    response = "❌ Не указано, что копировать"

            elif "очисти буфер" in command_lower:
                pyperclip.copy("")
                response = "✅ Буфер обмена очищен"

            elif "история буфера" in command_lower:
                response = "ℹ️ История буфера недоступна в базовой версии"

            else:
                response = "📋 Команды: 'прочитай буфер', 'скопируй [текст]', 'очисти буфер'"

            return response

        except ImportError:
            return "❌ Для работы с буфером обмена установите модуль: pip install pyperclip"