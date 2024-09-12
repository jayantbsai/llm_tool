import pytest
import re

from demo import Demo
from llmtoolutil import llm_tool_util

@pytest.mark.parametrize('prompt, regexs', [
    (
        'Who was the first president of the united states?',
        [r'George Washington']
    ),
    (
        'What will the temperature be in London, next Monday?',
        [r'\btemperature\b|\bweather\b', r'precipitation', r'wind speed', r'London', r'Monday']
    ),
    (
        'Who were the top 3 gold medal winning countries in the Tokyo olympics?',
        [r'United States', r'China', r'Japan', r'Tokyo Olympics']
    ),
    (
        'What will be the weather in San Francisco on Friday?',
        [r'\btemperature\b|\bweather\b', r'San Francisco', r'Friday']
    )
])

def test_demo_request(prompt:str, regexs:list):
    assert('get_weather_forecast' in llm_tool_util._tool_funcs)

    assistant = Demo()
    response = assistant.handle(prompt)
    
    for regx in regexs:
        assert(re.search(regx, response.lower(), re.IGNORECASE) != None)
