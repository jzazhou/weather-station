"""
Configuration template.

Copy this file to config.py and fill in your own values:

    cp config.example.py config.py

config.py is listed in .gitignore so your API key never gets committed.
This template is committed so anyone cloning the repo (including you, on a
fresh SD card) knows exactly which settings the code expects.
"""

# ---------------------------------------------------------------------
# OpenWeatherMap
# ---------------------------------------------------------------------

# Free-tier API key from https://openweathermap.org/api
# A brand-new key can take up to a couple of hours to activate — a 401
# response right after signing up usually means "not live yet", not "wrong".
OWM_API_KEY = "your_api_key_here"

# Location for outdoor readings.
CITY_NAME = "Ithaca"
COUNTRY_CODE = "US"

# "metric" gives degrees Celsius and metres per second.
# "imperial" would give Fahrenheit and miles per hour — note that ui.py
# hardcodes the "°C" and "m/s" labels, so switching this means editing
# those strings too.
UNITS = "metric"

# ---------------------------------------------------------------------
# Polling intervals, in seconds
# ---------------------------------------------------------------------

# How often the BME688 is read. Local I2C, so this is cheap.
SENSOR_INTERVAL = 10

# How often the weather API is called. Keep this at 600 or above: the free
# tier allows 60 calls/minute, and outdoor conditions do not change faster
# than every 10 minutes anyway.
API_INTERVAL = 600
