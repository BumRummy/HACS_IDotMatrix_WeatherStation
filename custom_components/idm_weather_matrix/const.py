DOMAIN = "idm_weather_matrix"

CONF_ADDRESS = "address"
CONF_WEATHER_ENTITY = "weather_entity"
CONF_PACK_PATH = "pack_path"
CONF_SIZE = "size"
CONF_TIME_FORMAT = "time_format"
CONF_TEMP_UNIT = "temp_unit"
CONF_REFRESH_SECONDS = "refresh_seconds"

DEFAULT_SIZE = 64
DEFAULT_PACK_PATH = "__bundled_giraffe__"
DEFAULT_TIME_FORMAT = "%-I:%M"
DEFAULT_REFRESH_SECONDS = 60

SERVICE_UUID = "000000fa-0000-1000-8000-00805f9b34fb"
WRITE_UUID = "0000fa02-0000-1000-8000-00805f9b34fb"
NOTIFY_UUID = "0000fa03-0000-1000-8000-00805f9b34fb"

DEFAULT_LAYOUT = {
    "clock": {"x": 11, "y": 0, "w": 42, "h": 11, "align": "center"},
    "temperature": {"x": 0, "y": 53, "w": 26, "h": 11, "align": "left"},
    "condition": {"x": 27, "y": 53, "w": 37, "h": 11, "align": "right"},
}

CONDITION_ALIASES = {
    "clear-night": "clear_night",
    "cloudy": "cloudy",
    "fog": "fog",
    "hail": "snow",
    "lightning": "thunderstorm",
    "lightning-rainy": "thunderstorm",
    "partlycloudy": "partly_cloudy",
    "pouring": "rain",
    "rainy": "rain",
    "snowy": "snow",
    "snowy-rainy": "snow",
    "sunny": "sunny",
    "windy": "windy",
    "windy-variant": "windy",
    "exceptional": "default",
    "extreme_heat": "extreme_heat",
    "freezing": "freezing",
}
