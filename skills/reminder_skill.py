import datetime
import threading
import time
import re
import winsound
import os
from skills.base_skill import BaseSkill


class ReminderSkill(BaseSkill):
    """Плагин напоминаний со звуковыми уведомлениями"""

    def __init__(self):
        super().__init__("Напоминания")
        self.reminders = []
        self.active_timers = []
        self.is_running = True

        # Запускаем фоновый поток
        self.worker_thread = threading.Thread(target=self._check_reminders, daemon=True)
        self.worker_thread.start()

    def get_keywords(self):
        return [
            "напомни",
            "напоминание",
            "напомни через",
            "установи напоминание",
            "список напоминаний",
            "удали напоминание",
            "таймер"
        ]

    def _play_notification_sound(self, duration: int = 4):
        """Воспроизводит звуковое уведомление"""
        try:
            # Создаем красивую мелодию с помощью бипов
            # Мелодия: восходящая последовательность тонов
            frequencies = [523, 587, 659, 698, 784, 880, 988, 1047]  # C5 to C6
            beep_duration = min(500, (duration * 1000) // len(frequencies))

            for freq in frequencies:
                winsound.Beep(freq, beep_duration)
                time.sleep(0.05)  # небольшая пауза между тонами

        except Exception as e:
            self.logger.warning(f"Не удалось воспроизвести звук: {e}")
            # Альтернатива: системный звук
            try:
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            except:
                pass

    def _play_alert_melody(self):
        """Воспроизводит более сложную мелодию оповещения"""
        try:
            # Мелодия оповещения (чередование высоких и низких тонов)
            melody = [
                (784, 300),  # G5
                (523, 200),  # C5
                (1047, 400),  # C6
                (659, 300),  # E5
                (880, 500),  # A5
            ]

            for freq, duration in melody:
                winsound.Beep(freq, duration)
                time.sleep(0.1)

        except Exception as e:
            self.logger.warning(f"Не удалось воспроизвести мелодию: {e}")
            self._play_notification_sound(3)

    def _visual_alert(self, action: str):
        """Создает визуальное оповещение в консоли"""
        alert_text = f"""
{'🚨' * 16}
🚨                            🚨
🚨        ТАЙМЕР СРАБОТАЛ     🚨
🚨                            🚨
🚨    {action:<20}    
🚨                            🚨
🚨    {datetime.datetime.now().strftime('%H:%M:%S')}                🚨
🚨                            🚨
{'🚨' * 16}
        """
        print("\n" + alert_text + "\n")

    def execute(self, command: str, memory):
        command_lower = command.lower()

        if any(word in command_lower for word in ["напомни через", "таймер на"]):
            return self._set_timer_reminder(command, memory)
        elif "напомни" in command_lower:
            return self._set_simple_reminder(command, memory)
        elif "список напоминаний" in command_lower:
            return self._list_reminders()
        elif "удали напоминание" in command_lower:
            return self._delete_reminder(command)

        return "Скажите 'напомни через [время] [действие]'"

    def _parse_time_unit(self, command: str) -> tuple:
        """Парсит время и единицу измерения из команды"""
        command_lower = command.lower()

        # Паттерны для поиска времени
        patterns = [
            # Секунды
            (r'(\d+)\s*секунд[уы]?', 'seconds'),
            (r'(\d+)\s*сек', 'seconds'),
            (r'(\d+)\s*s', 'seconds'),

            # Минуты
            (r'(\d+)\s*минут[уы]?', 'minutes'),
            (r'(\d+)\s*мин', 'minutes'),
            (r'(\d+)\s*m', 'minutes'),

            # Часы
            (r'(\d+)\s*час[аов]?', 'hours'),
            (r'(\d+)\s*ч', 'hours'),
            (r'(\d+)\s*h', 'hours'),

            # Комбинированные форматы
            (r'(\d+):(\d+):(\d+)', 'hms'),  # часы:минуты:секунды
            (r'(\d+):(\d+)', 'hm'),  # часы:минуты
        ]

        for pattern, unit in patterns:
            match = re.search(pattern, command_lower)
            if match:
                if unit == 'hms':
                    hours, minutes, seconds = map(int, match.groups())
                    total_seconds = hours * 3600 + minutes * 60 + seconds
                    return total_seconds, f"{hours}ч {minutes}м {seconds}с"
                elif unit == 'hm':
                    hours, minutes = map(int, match.groups())
                    total_seconds = hours * 3600 + minutes * 60
                    return total_seconds, f"{hours}ч {minutes}м"
                else:
                    time_value = int(match.group(1))
                    if unit == 'seconds':
                        return time_value, f"{time_value} секунд"
                    elif unit == 'minutes':
                        return time_value * 60, f"{time_value} минут"
                    elif unit == 'hours':
                        return time_value * 3600, f"{time_value} часов"

        # Если не нашли паттерн, пробуем извлечь число и определить единицу по контексту
        numbers = re.findall(r'\d+', command_lower)
        if numbers:
            time_value = int(numbers[0])

            # Определяем единицу по контексту
            if any(word in command_lower for word in ['секунд', 'сек', 's']):
                return time_value, f"{time_value} секунд"
            elif any(word in command_lower for word in ['час', 'ч', 'h']):
                return time_value * 3600, f"{time_value} часов"
            else:  # по умолчанию минуты
                return time_value * 60, f"{time_value} минут"

        return None, None

    def _extract_action(self, command: str) -> str:
        """Извлекает действие из команды"""
        # Убираем ключевые слова времени
        time_keywords = ['через', 'таймер', 'на', 'секунд', 'минут', 'час', 'сек', 'мин', 'ч']
        words = command.split()

        # Находим где заканчивается описание времени
        action_start = 0
        for i, word in enumerate(words):
            if word.isdigit() or any(kw in word.lower() for kw in time_keywords):
                action_start = i + 1
            else:
                # Если нашли не-временное слово после временных - это начало действия
                if action_start > 0 and i >= action_start:
                    break

        action_words = words[action_start:]
        action = " ".join(action_words).strip()

        # Если действие пустое, используем стандартное
        if not action:
            action = "время вышло!"

        return action

    def _set_timer_reminder(self, command: str, memory) -> str:
        """Устанавливает напоминание по таймеру"""
        try:
            # Парсим время из команды
            total_seconds, time_display = self._parse_time_unit(command)

            if total_seconds is None:
                return "Не понял время. Скажите например: 'напомни через 30 секунд', 'таймер на 5 минут' или 'напомни через 2 часа'"

            # Извлекаем действие
            action = self._extract_action(command)

            # Создаем напоминание
            reminder_time = datetime.datetime.now() + datetime.timedelta(seconds=total_seconds)
            reminder_id = len(self.reminders) + 1

            reminder = {
                "id": reminder_id,
                "time": reminder_time,
                "action": action,
                "created": datetime.datetime.now(),
                "memory": memory,
                "total_seconds": total_seconds
            }

            self.reminders.append(reminder)

            # Создаем таймер
            timer = threading.Timer(
                total_seconds,
                self._trigger_reminder,
                [reminder_id, action]
            )
            timer.daemon = True
            timer.start()
            self.active_timers.append(timer)

            time_str = reminder_time.strftime("%H:%M:%S")
            return f"✅ Таймер установлен на {time_display}! Напомню в {time_str}: {action}"

        except Exception as e:
            self.logger.error(f"Ошибка установки напоминания: {e}")
            return "Ошибка при установке таймера"

    def _set_simple_reminder(self, command: str, memory) -> str:
        """Устанавливает простое напоминание (без таймера)"""
        action = command.replace("напомни", "").strip()
        if action:
            reminder_id = len(self.reminders) + 1
            reminder = {
                "id": reminder_id,
                "time": datetime.datetime.now(),
                "action": action,
                "created": datetime.datetime.now(),
                "memory": memory
            }
            self.reminders.append(reminder)
            return f"Запомнил: {action}"
        return "Что именно напомнить?"

    def _trigger_reminder(self, reminder_id: int, action: str):
        """Срабатывание напоминания"""
        try:
            # Находим напоминание
            reminder = next((r for r in self.reminders if r["id"] == reminder_id), None)
            if reminder and reminder.get("memory"):
                memory = reminder["memory"]

                # 1. ВИЗУАЛЬНОЕ ОПОВЕЩЕНИЕ
                self._visual_alert(action)

                # 2. ЗВУКОВОЕ ОПОВЕЩЕНИЕ (в отдельном потоке чтобы не блокировать)
                sound_thread = threading.Thread(target=self._play_alert_melody, daemon=True)
                sound_thread.start()

                # 3. ГОЛОСОВОЕ ОПОВЕЩЕНИЕ
                reminder_text = f"Внимание! Таймер сработал: {action}"

                if hasattr(memory, 'tts_engine') and memory.tts_engine:
                    # Ждем немного перед озвучкой чтобы звук начался первым
                    threading.Timer(0.5, lambda: memory.tts_engine.speak(reminder_text)).start()

                # Удаляем сработавшее напоминание
                self.reminders = [r for r in self.reminders if r["id"] != reminder_id]

        except Exception as e:
            self.logger.error(f"Ошибка при срабатывании напоминания: {e}")

    def _check_reminders(self):
        """Фоновая проверка напоминаний"""
        while self.is_running:
            try:
                now = datetime.datetime.now()

                # Проверяем просроченные напоминания (на всякий случай)
                for reminder in self.reminders[:]:
                    if now > reminder["time"] and "timer" not in reminder:
                        self._trigger_reminder(reminder["id"], reminder["action"])

                time.sleep(10)

            except Exception as e:
                self.logger.error(f"Ошибка в фоновой проверке напоминаний: {e}")
                time.sleep(30)

    def _list_reminders(self) -> str:
        """Показывает список активных напоминаний"""
        if not self.reminders:
            return "У вас нет активных напоминаний"

        response = "📋 Активные таймеры:\n\n"
        now = datetime.datetime.now()

        for reminder in self.reminders:
            time_left = reminder["time"] - now
            if time_left.total_seconds() > 0:
                # Форматируем оставшееся время
                if time_left.total_seconds() < 60:
                    time_str = f"{int(time_left.total_seconds())}с"
                elif time_left.total_seconds() < 3600:
                    minutes = int(time_left.total_seconds() // 60)
                    seconds = int(time_left.total_seconds() % 60)
                    time_str = f"{minutes}м {seconds}с"
                else:
                    hours = int(time_left.total_seconds() // 3600)
                    minutes = int((time_left.total_seconds() % 3600) // 60)
                    time_str = f"{hours}ч {minutes}м"

                response += f"• Через {time_str}: {reminder['action']}\n"

        print(response)
        return "Вывел список таймеров в консоль"

    def _delete_reminder(self, command: str) -> str:
        """Удаляет напоминание"""
        try:
            words = command.split()
            if "все" in words:
                for timer in self.active_timers:
                    timer.cancel()
                self.active_timers.clear()
                self.reminders.clear()
                return "Все таймеры удалены"

            search_term = " ".join(words[words.index("напоминание") + 1:])

            removed_count = 0
            for reminder in self.reminders[:]:
                if search_term.lower() in reminder["action"].lower():
                    # Находим и останавливаем соответствующий таймер
                    for timer in self.active_timers[:]:
                        if timer.is_alive():
                            timer.cancel()
                            self.active_timers.remove(timer)

                    self.reminders.remove(reminder)
                    removed_count += 1

            if removed_count > 0:
                return f"Удалено {removed_count} таймеров"
            else:
                return "Не нашел таких таймеров"

        except Exception as e:
            return "Скажите 'удали напоминание [текст]' или 'удали все напоминания'"

    def on_disable(self):
        """Вызывается при выключении плагина"""
        self.is_running = False
        for timer in self.active_timers:
            timer.cancel()
        self.active_timers.clear()
        super().on_disable()