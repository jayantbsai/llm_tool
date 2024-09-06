import pytest
import datetime
from demo_tools.weather_tool import get_weather_forecast

@pytest.mark.parametrize('args, expected_date', [
    (
        (37.7749, -122.4194, 1), # SF
        (datetime.datetime.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    ),
    (
        (51.5072, -0.1278, None), # London
        datetime.datetime.today().strftime('%Y-%m-%d')
    ),
    (
        (48.86, 2.3599997, 10), # Paris
        (datetime.datetime.today() + datetime.timedelta(days=10)).strftime('%Y-%m-%d')
    ),
    (
        (28.6139, 77.2090, -1), # New Delhi
        (datetime.datetime.today() + datetime.timedelta(days=-1)).strftime('%Y-%m-%d')
    ),
    (
        (-33.8651, 151.2099, 0), # Sydney
        (datetime.datetime.today() + datetime.timedelta(days=0)).strftime('%Y-%m-%d')
    )
])

def test_weather_forecast(args, expected_date):
    delta = args[2]
    if delta == None:
        delta = 0
    forecast_date = datetime.datetime.today() + datetime.timedelta(delta)

    res = get_weather_forecast(args[0], args[1], forecast_date.strftime('%Y-%m-%d'))
    assert('forecast' in res)
    forecast = res.get('forecast')
    assert('date' in forecast and 'min_temp' in forecast and 'max_temp' in forecast)
    assert(forecast.get('date') == expected_date)