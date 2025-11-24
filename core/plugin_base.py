from abc import ABC, abstractmethod
import logging

logger = logging.getLogger('VoiceAssistant')


class BasePlugin(ABC):
    """Базовый класс для всех плагинов"""

    def __init__(self, name: str, version: str = "1.0"):
        self.name = name
        self.version = version
        self.enabled = True
        self.logger = logger

    @abstractmethod
    def get_commands(self) -> list:
        """Возвращает список команд, которые обрабатывает плагин"""
        pass

    @abstractmethod
    def execute(self, command: str, memory, **kwargs) -> str:
        """Выполняет команду"""
        pass

    def on_enable(self):
        """Вызывается при включении плагина"""
        self.logger.info(f"Плагин {self.name} v{self.version} включен")

    def on_disable(self):
        """Вызывается при выключении плагина"""
        self.logger.info(f"Плагин {self.name} v{self.version} выключен")

    def get_info(self) -> dict:
        """Возвращает информацию о плагине"""
        return {
            "name": self.name,
            "version": self.version,
            "enabled": self.enabled,
            "commands": self.get_commands()
        }