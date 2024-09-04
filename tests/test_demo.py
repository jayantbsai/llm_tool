import pytest

from demo import Demo
from llmtoolutil import llm_tool_util

@pytest.mark.parametrize('prompt, expected_list_of_words', [
    (
        'Who was the first president of the united states?',
        ['George Washington']
    ),
    (
        'What will the temperature be in London, next Monday?',
        ['temperature', 'London', 'Monday']
    ),
    (
        'Who were the top 3 gold medal winning countries in the Tokyo olympics?',
        ['United States', 'China', 'Japan', 'Tokyo Olympics']
    ),
    (
        'What will be the weather in San Francisco on Friday?',
        ['weather', 'San Francisco', 'Friday']
    )
])

def test_demo_request(prompt:str, expected_list_of_words:list):
    assert('get_weather_forecast' in llm_tool_util._tool_funcs)

    assistant = Demo()
    response = assistant.request(prompt)
    for word in expected_list_of_words:
        assert(word.lower() in response.lower())
