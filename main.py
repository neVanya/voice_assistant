#!/usr/bin/env python3
"""
Главный запускающий файл голосового ассистента
"""
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

from assistant_core import VoiceAssistant
import logging

logger = logging.getLogger('VoiceAssistant')


def main():
    """Основная функция запуска"""
    print("🚀 Запуск улучшенного голосового ассистента...")

    try:
        assistant = VoiceAssistant()
        assistant.run()

    except KeyboardInterrupt:
        logger.info("Работа ассистента завершена пользователем")
    except Exception as e:
        logger.error(f"Ошибка запуска ассистента: {e}")
        print(f"❌ Критическая ошибка: {e}")


if __name__ == "__main__":
    main()