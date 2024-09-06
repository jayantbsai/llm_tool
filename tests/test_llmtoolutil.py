import pytest
from fixture_functions import *
from llmtoolutil import llm_tool_util
from demo_tools.weather_tool import get_weather_forecast

import logging
import io


### Test func -> llm_tool handling #

@pytest.mark.parametrize('func, expected_logs', [
    (
        hello_doc,
        """✅ Function `hello_doc` passes all checks."""
    ),
    (
        one_arg_no_type_no_return,
        """❌ Function `one_arg_no_type_no_return` not added. It may not work as expected when included in prompt.
 * Missing return type. All llm tool functions should return a value, to be subsequently used by the llm.
 * Missing argument type for: `param`"""
    ),
    (
        one_arg_no_doc_desc,
        """❌ Function `one_arg_no_doc_desc` not added. It may not work as expected when included in prompt.
 * Missing or invalid function summary."""
    ),
    (
        one_arg_type_no_return,
        """❌ Function `one_arg_type_no_return` not added. It may not work as expected when included in prompt.
 * Missing return type. All llm tool functions should return a value, to be subsequently used by the llm."""
    ),
    (
        one_arg_no_type_yes_return,
        """❌ Function `one_arg_no_type_yes_return` not added. It may not work as expected when included in prompt.
 * Missing argument type for: `param`"""
    ),
    (
        two_args_yes_type_no_return,
        """❌ Function `two_args_yes_type_no_return` not added. It may not work as expected when included in prompt.
 * Missing return type. All llm tool functions should return a value, to be subsequently used by the llm."""
    ),
    (
        three_args_yes_type_yes_return,
        """✅ Function `three_args_yes_type_yes_return` passes all checks."""
    ),
    (
        just_test_types,
        """✅ Function `just_test_types` passes all checks."""
    ),
    (
        connect_to_next_port,
        """✅ Function `connect_to_next_port` passes all checks."""
    )
])

def test_llm_tool_addition(func, expected_logs):
    stream = io.StringIO()
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(stream)
    logger.addHandler(handler)
    
    llm_tool_util.llm_tool(func)

    assert(stream.getvalue().strip() == expected_logs)

    logger.removeHandler(handler)
    llm_tool_util._clear_tools()


### Test func -> tool markup ###

@pytest.mark.parametrize('func, expected_list', [
        (
            hello_doc,
            [
                {
                    "type": "function",
                    "function": {
                        "name": "hello_doc",
                        "description": "This function returns Hello World!",
                        "parameters": None,
                    }
                }
            ]
        ),
        (
            one_arg_no_type_no_return,
            []
        ),
        (
            one_arg_no_doc_desc,
            []
        ),
        (
            one_arg_type_no_return,
            []
        ),
        (
            one_arg_no_type_yes_return,
            []
        ),
        (
            two_args_yes_type_no_return,
            []
        ),
        (
            three_args_yes_type_yes_return,
            [
                {
                    "type": "function",
                    "function": {
                        "name": "three_args_yes_type_yes_return",
                        "description": "Take two strings, join them with 1 multiplied by glue and return its length.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "some_string": {
                                    "type": "string",
                                    "description": "Some string"
                                },
                                "some_other_string": {
                                    "type": "string",
                                    "description": "Some other string"
                                },
                                "glue": {
                                    "type": "integer",
                                    "description": "Added '0' as separators (default 1)"
                                }
                            },
                            "required": [
                                "some_string",
                                "some_other_string"
                            ]
                        }
                    }
                }
            ]
        ),
        (
            just_test_types,
            [
                {
                    "type": "function",
                    "function": {
                        "name": "just_test_types",
                        "description": "Provides a test method to test types",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "a": {
                                    "type": "integer",
                                    "description": "an integer (int)"
                                },
                                "b": {
                                    "type": "string",
                                    "description": "a string (str)"
                                },
                                "c": {
                                    "type": "dictionary",
                                    "description": "a dictionary (dict)"
                                },
                                "d": {
                                    "type": "array",
                                    "description": "an array (list)"
                                },
                                "e": {
                                    "type": "boolean",
                                    "description": "a boolean (bool)"
                                },
                                "f": {
                                    "type": "tuple",
                                    "description": "a tuple"
                                },
                                "g": {
                                    "type": "range",
                                    "description": "a range"
                                },
                                "h": {
                                    "type": "set",
                                    "description": "a set"
                                },
                                "i": {
                                    "type": "float",
                                    "description": "a float"
                                }
                            },
                            "required": [
                                "a",
                                "b",
                                "c",
                                "d",
                                "e",
                                "f",
                                "g",
                                "h",
                                "i"
                            ]
                        }
                    }
                }
            ]
        ),
        (
            connect_to_next_port,
            [
                {
                    "type": "function",
                    "function": {
                        "name": "connect_to_next_port",
                        "description": "Connects to the next available port.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "minimum": {
                                    "type": "integer",
                                    "description": "A port value greater or equal to 1024"
                                }
                            },
                            "required": [
                                "minimum"
                            ]
                        }
                    }
                }
            ]
        )
    ])

def test_get_func_details(func, expected_list):
    llm_tool_util.llm_tool(func)
    assert(llm_tool_util.generate_tool_markup() == expected_list)

    llm_tool_util._clear_tools()



### Test llm_tool.is_tool_call ###

@pytest.mark.parametrize('model_response, expected', [
    (
        '{ "name": "get_top_gold_medal_winning_countries", "parameters": { "year": "2020", "city": "tokyo" } }',
        True
    ),
    (
        '{ "name": "get_top_gold_medal_winning_countries" }',
        False
    ),
    (
        '{ "parameters": { "year": "2020", "city": "tokyo" } }',
        False
    ),
    (
        '{ "name": "get_weather_forecast", "parameters": { "lat": "37.7749", "lon": "-122.4194", "forecast_date": "2024-09-06" } }',
        True
    ),
    (
        'The first president of the United States was George Washington.',
        False
    )
])

def test_is_tool_call(model_response:str, expected:str):
    assert(llm_tool_util.is_tool_call(model_response) == expected)


### Test llm_tool_response.can_handle_model_response

@pytest.mark.parametrize('tools, model_response, expected', [
    (
        [],
        '{ "name": "get_top_gold_medal_winning_countries", "parameters": { "year": "2020", "city": "tokyo" } }',
        False
    ),
    (
        [],
        '{ "name": "get_top_gold_medal_winning_countries" }',
        False
    ),
    (
        [],
        '{ "parameters": { "year": "2020", "city": "tokyo" } }',
        False
    ),
    (
        [connect_to_next_port],
        '{ "name": "connect_to_next_port", "parameters": { "minimum": "8080" } }',
        True
    ),
    (
        [connect_to_next_port],
        '{ "name": "get_top_gold_medal_winning_countries", "parameters": { "year": "2020", "city": "tokyo" } }',
        False
    ),
    (
        [get_weather_forecast, connect_to_next_port],
        '{ "name": "get_weather_forecast", "parameters": { "lat": "37.7749", "lon": "-122.4194", "forecast_date": "2024-09-06" } }',
        True
    ),
    (
        [get_weather_forecast],
        'The first president of the United States was George Washington.',
        False
    )
])

def test_can_handle_tool_call(tools, model_response, expected):
    for tool in tools:
        llm_tool_util.llm_tool(tool)

    assert(llm_tool_util.can_handle_tool_call(model_response) == expected)

    llm_tool_util._clear_tools()



