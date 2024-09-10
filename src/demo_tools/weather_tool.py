import requests
from datetime import datetime
import logging

from urllib.parse import urlencode
from llmtoolutil import llm_tool_util

weather_url = 'https://api.open-meteo.com/v1/forecast'

@llm_tool_util.llm_tool
def get_weather_forecast(lat:float, lon:float, date:datetime) -> dict:
    '''
    Returns the weather and temperature forecast for a specified date

    lat: Latitude for the location. ex: 37.7749
    lon: Longitude for the location. ex: -122.4194
    date: Date to forecast weather in YYYY-MM-DD format. ex: 2024-07-29

    returns: dictionary with date, min/max temperature, min/max precipitation, and min/max winds
    '''
    params = {
        'latitude': lat,
        'longitude': lon,
        'start_date': date,
        'end_date': date,
        'hourly': 'temperature_2m,precipitation,wind_speed_10m',
        'temperature_unit': 'fahrenheit',
        'precipitation_unit': 'inch',
        'wind_speed_unit': 'mph',
    }

    response = requests.get(f'{weather_url}?{urlencode(params)}')
    res_json = response.json()
    logging.debug(res_json)
    hourly = res_json['hourly']
    units = res_json['hourly_units']

    return {
        'format_hint': 'Format response with temperature, precipitation, & wind speed in a single sentence.',
        'forecast': {
            'date': date,
            'temperature': f"{min(hourly['temperature_2m'])} - {max(hourly['temperature_2m'])} {units['temperature_2m']}",
            'precipitation': f"{min(hourly['precipitation'])} - {max(hourly['precipitation'])} {units['precipitation']}",
            'wind_speed': f"{min(hourly['wind_speed_10m'])} - {max(hourly['wind_speed_10m'])} {units['wind_speed_10m']}",
        }
    }
