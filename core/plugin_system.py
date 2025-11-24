import os
import importlib
import logging
from typing import Dict, List
from core.plugin_base import BasePlugin

logger = logging.getLogger('VoiceAssistant')


class PluginSystem:
    """Система управления плагинами"""

    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = plugins_dir
        self.plugins: Dict[str, BasePlugin] = {}
        self._ensure_plugins_dir()

    def _ensure_plugins_dir(self):
        """Создает директорию для плагинов если её нет"""
        if not os.path.exists(self.plugins_dir):
            os.makedirs(self.plugins_dir)
            # Создаем __init__.py для импорта
            with open(os.path.join(self.plugins_dir, "__init__.py"), "w") as f:
                f.write("# Пакет плагинов\n")

    def load_plugins(self):
        """Загружает все плагины из директории"""
        logger.info("Загрузка плагинов...")

        # Ищем файлы плагинов
        for filename in os.listdir(self.plugins_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                plugin_name = filename[:-3]  # Убираем .py
                self.load_plugin(plugin_name)

        logger.info(f"Загружено {len(self.plugins)} плагинов")

    def load_plugin(self, plugin_name: str) -> bool:
        """Загружает конкретный плагин"""
        try:
            # Динамически импортируем модуль плагина
            module = importlib.import_module(f"plugins.{plugin_name}")

            # Ищем класс плагина (должен называться как файл с заглавной буквы)
            plugin_class_name = plugin_name.title().replace("_", "")
            plugin_class = getattr(module, plugin_class_name, None)

            if plugin_class and issubclass(plugin_class, BasePlugin):
                # Создаем экземпляр плагина
                plugin_instance = plugin_class()
                self.plugins[plugin_name] = plugin_instance
                plugin_instance.on_enable()

                logger.info(f"✅ Плагин загружен: {plugin_name}")
                return True
            else:
                logger.warning(f"❌ Не найден класс плагина в {plugin_name}")
                return False

        except Exception as e:
            logger.error(f"❌ Ошибка загрузки плагина {plugin_name}: {e}")
            return False

    def unload_plugin(self, plugin_name: str) -> bool:
        """Выгружает плагин"""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].on_disable()
            del self.plugins[plugin_name]
            logger.info(f"Плагин выгружен: {plugin_name}")
            return True
        return False

    def execute_command(self, command: str, memory, **kwargs) -> str:
        """Выполняет команду через подходящий плагин"""
        command_lower = command.lower()

        for plugin_name, plugin in self.plugins.items():
            if plugin.enabled:
                for plugin_command in plugin.get_commands():
                    if plugin_command in command_lower:
                        try:
                            logger.info(f"Плагин {plugin_name} обрабатывает команду: {command}")
                            return plugin.execute(command, memory, **kwargs)
                        except Exception as e:
                            logger.error(f"Ошибка в плагине {plugin_name}: {e}")
                            return f"Ошибка в плагине {plugin_name}"

        return None  # Если ни один плагин не подошел

    def get_plugin_info(self, plugin_name: str) -> dict:
        """Возвращает информацию о плагине"""
        if plugin_name in self.plugins:
            return self.plugins[plugin_name].get_info()
        return None

    def list_plugins(self) -> List[dict]:
        """Возвращает список всех плагинов"""
        return [plugin.get_info() for plugin in self.plugins.values()]

    def enable_plugin(self, plugin_name: str) -> bool:
        """Включает плагин"""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = True
            self.plugins[plugin_name].on_enable()
            return True
        return False

    def disable_plugin(self, plugin_name: str) -> bool:
        """Выключает плагин"""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = False
            self.plugins[plugin_name].on_disable()
            return True
        return False


# Глобальный экземпляр
plugin_system = PluginSystem()