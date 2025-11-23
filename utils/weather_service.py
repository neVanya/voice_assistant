import requests
from config.settings import Settings
import logging

logger = logging.getLogger('VoiceAssistant')

# Координаты городов из вашего кода
CITY_COORDINATES = {
    "Ivanovo": {"lat": 56.9942, "lon": 40.9858},
    "Moscow": {"lat": 55.7558, "lon": 37.6173},
    "Saint Petersburg": {"lat": 59.9343, "lon": 30.3351},
    "Yaroslavl": {"lat": 57.6261, "lon": 39.8845},
    "Vladimir": {"lat": 56.1290, "lon": 40.4066},
    "Kostroma": {"lat": 57.7665, "lon": 40.9269},
    "Nizhny Novgorod": {"lat": 56.3269, "lon": 44.0059},
    "Kazan": {"lat": 55.7887, "lon": 49.1221},
    "Yekaterinburg": {"lat": 56.8389, "lon": 60.6057},
    "Krasnodar": {"lat": 45.0355, "lon": 38.9753},
    "Sochi": {"lat": 43.5855, "lon": 39.7231},
    "Tver": {"lat": 56.8584, "lon": 35.9000},
    "Novosibirsk": {"lat": 55.0084, "lon": 82.9357}
}

# Сопоставление русских названий с английскими
CITY_MAPPING = {
    'москв': 'Moscow',
    'питер': 'Saint Petersburg',
    'спб': 'Saint Petersburg',
    'санкт-петербург': 'Saint Petersburg',
    'новгород': 'Nizhny Novgorod',
    'ярослав': 'Yaroslavl',
    'костр': 'Kostroma',
    'владимир': 'Vladimir',
    'иванов': 'Ivanovo',
    'казан': 'Kazan',
    'екатеринбург': 'Yekaterinburg',
    'краснодар': 'Krasnodar',
    'сочи': 'Sochi',
    'твер': 'Tver',
    'новосибирск': 'Novosibirsk',
}


class WeatherService:
    """Сервис для получения погоды через OpenWeatherMap"""

    def __init__(self):
        self.api_key = Settings.WEATHER_API_KEY
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"

    def get_city_from_text(self, text: str) -> str:
        """Определяет город из текста команды"""
        text_lower = text.lower()

        for city_ru, city_en in CITY_MAPPING.items():
            if city_ru in text_lower:
                return city_en

        # Если город не найден, используем Иваново по умолчанию
        return "Ivanovo"

    def get_weather(self, city: str = "Ivanovo") -> str:
        """Получает текущую погоду для города"""
        try:
            if city not in CITY_COORDINATES:
                return f"Город {city} не настроен в системе"

            coords = CITY_COORDINATES[city]

            params = {
                'lat': coords["lat"],
                'lon': coords["lon"],
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'ru'
            }

            logger.info(f"Запрос погоды для {city}: {coords['lat']}, {coords['lon']}")

            response = requests.get(self.base_url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                logger.info(f"Данные погоды получены: {data['weather'][0]['description']}")
                return self._format_weather_response(data, city)
            elif response.status_code == 401:
                logger.error("Неверный API ключ OpenWeatherMap")
                return "Проблема с подключением к погодному сервису. Проверьте API ключ."
            else:
                logger.error(f"Ошибка API погоды: {response.status_code}")
                return f"Ошибка получения погоды: {response.status_code}"

        except requests.exceptions.Timeout:
            logger.error("Таймаут запроса погоды")
            return "Не удалось получить погоду: превышено время ожидания"
        except requests.exceptions.ConnectionError:
            logger.error("Ошибка подключения к погодному сервису")
            return "Нет подключения к интернету для получения погоды"
        except Exception as e:
            logger.error(f"Общая ошибка получения погоды: {e}")
            return f"Ошибка при получении погоды: {e}"

    def _format_weather_response(self, data: dict, city: str) -> str:
        """Форматирует данные о погоде в читаемый текст"""
        try:
            temperature = round(data['main']['temp'])
            feels_like = round(data['main']['feels_like'])
            humidity = data['main']['humidity']
            pressure = data['main']['pressure']
            description = data['weather'][0]['description']
            wind_speed = data['wind']['speed']

            # Emoji для погоды
            weather_emoji = self._get_weather_emoji(data['weather'][0]['main'])

            # Форматируем ответ для голосового воспроизведения
            response = f"{weather_emoji} Погода в {city}: "
            response += f"{description}. "
            response += f"Температура {temperature}°C, "
            response += f"ощущается как {feels_like}°C. "
            response += f"Влажность {humidity}%. "
            response += f"Ветер {wind_speed} м/с."

            # Добавляем рекомендации
            recommendation = self._get_weather_recommendation(temperature, description)
            if recommendation:
                response += f" {recommendation}"

            return response

        except Exception as e:
            return f"Ошибка обработки данных погоды: {e}"

    def _get_weather_emoji(self, weather_main: str) -> str:
        """Возвращает emoji в зависимости от типа погоды"""
        emoji_map = {
            'Clear': '☀️',
            'Clouds': '☁️',
            'Rain': '🌧️',
            'Drizzle': '🌦️',
            'Thunderstorm': '⛈️',
            'Snow': '❄️',
            'Mist': '🌫️',
            'Smoke': '💨',
            'Haze': '🌫️',
            'Dust': '💨',
            'Fog': '🌫️',
            'Sand': '💨',
            'Ash': '💨',
            'Squall': '💨',
            'Tornado': '🌪️'
        }
        return emoji_map.get(weather_main, '🌤️')

    def _get_weather_recommendation(self, temperature: int, description: str) -> str:
        """Возвращает рекомендации по погоде"""
        recommendations = []

        if temperature < -10:
            recommendations.append("Очень холодно! Оденьтесь теплее.")
        elif temperature < 0:
            recommendations.append("Холодно! Наденьте куртку.")
        elif temperature < 10:
            recommendations.append("Прохладно, возьмите кофту.")
        elif temperature > 25:
            recommendations.append("Жарко! Отличная погода для мороженого.")
        elif temperature > 30:
            recommendations.append("Очень жарко! Пейте больше воды.")

        if 'rain' in description.lower():
            recommendations.append("Возьмите зонт!")
        elif 'snow' in description.lower():
            recommendations.append("Осторожно, скользко!")
        elif 'clear' in description.lower() and temperature > 15:
            recommendations.append("Отличная погода для прогулки!")

        return " ".join(recommendations) if recommendations else ""


# Глобальный экземпляр сервиса погоды
weather_service = WeatherService()