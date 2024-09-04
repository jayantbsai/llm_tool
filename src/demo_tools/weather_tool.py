import requests
from datetime import datetime
import logging

from urllib.parse import urlencode
from llmtoolutil import llm_tool_util

weather_url = 'https://api.open-meteo.com/v1/forecast'

@llm_tool_util.llm_tool
def get_weather_forecast(lat:float,
                         lon:float,
                         forecast_date:datetime = datetime.today().strftime('%Y-%m-%d')
                         ) -> dict:
    '''
    Returns the weather and temperature forecast for a specified date

    lat: Latitude for the location. ex: 37.7749
    lon: Longitude for the location. ex: -122.4194
    forecast_date: Date to forecast weather in YYYY-MM-DD format. ex: 2007-01-09 (defaults to current date)
    '''
    params = {
        'latitude': lat,
        'longitude': lon,
        'temperature_unit': 'fahrenheit',
        'hourly': 'temperature_2m',
        'start_date': forecast_date,
        'end_date': forecast_date,
    }

    response = requests.get(f'{weather_url}?{urlencode(params)}')
    res_json = response.json()
    logging.debug(res_json)
    hourly = res_json['hourly']['temperature_2m']

    return {
        'forecast': {
            'date': forecast_date,
            'min_temp': min(hourly),
            'max_temp': max(hourly),
        }
    }