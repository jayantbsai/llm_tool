import pytest
from docextractor import DocExtractor
from fixture_functions import *


### Test function -> docstring ###

@pytest.mark.parametrize('func, expected_doc', [
        (
            no_doc,
            None
        ),
        (
            empty_doc,
            ""
        ),
        (
            hello_doc,
            "This function returns Hello World!"
        ),
        (
            one_arg_no_type_no_return,
            """This function takes in a param and prints it

param -- Some parameter that will be printed"""
        ),
        (
            one_arg_no_doc_desc,
            """param -- Some parameter that will be printed"""
        ),
        (
            one_arg_type_no_return,
            """This function takes in an int param and returns a string

param -- Some parameter that will be returned as a string"""
        ),
        (
            one_arg_no_type_yes_return,
            """This function takes in a param and ignores it.

param -- Some parameter that will be ignored"""
        ),
        (
            two_args_yes_type_no_return,
            """Annotated args with no return specified.

anInt -- Param is an integer
aList -- Param is a list"""
        ),
        (
            three_args_yes_type_yes_return,
            """Take two strings, join them with 1 multiplied by glue and return its length.

some_string -- Some string
some_other_string -- Some other string
glue -- Added '0' as separators (default 1)
returns length of new string"""
        ),
        (
            just_test_types,
            """Provides a test method to test types

a -- an integer (int)
b -- a string (str)
c -- a dictionary (dict)
d -- an array (list)
e -- a boolean (bool)
f -- a tuple
g -- a range
h -- a set
i -- a float"""
        ),
        (
            connect_to_next_port,
            """Connects to the next available port.

Args:
  minimum: A port value greater or equal to 1024

Returns:
  The new minimum port.

Raises:
  ConnectionError: If no available port is found."""
        )
    ])

def test_get_func_doc(func, expected_doc):
    doc_extract = DocExtractor()
    assert(doc_extract.get_func_doc(func)) == expected_doc


### Test docstring -> dict ###

@pytest.mark.parametrize('func, expected_dict', [
        (
            hello_doc,
            {
                "summary": "This function returns Hello World!",
                "args": {}
            }
        ),
        (
            one_arg_no_type_no_return,
            {
                "summary": "This function takes in a param and prints it",
                "args": {
                    "param": "Some parameter that will be printed"
                }
            }
        ),
        (
            one_arg_no_doc_desc,
            {
                "summary": "",
                "args": {
                    "param": "Some parameter that will be printed"
                }
            }
        ),
        (
            one_arg_type_no_return,
            {
                "summary": "This function takes in an int param and returns a string",
                "args": {
                    "param": "Some parameter that will be returned as a string"
                }
            }
        ),
        (
            one_arg_no_type_yes_return,
            {
                "summary": "This function takes in a param and ignores it.",
                "args": {
                    "param": "Some parameter that will be ignored"
                }
            }
        ),
        (
            two_args_yes_type_no_return,
            {
                "summary": "Annotated args with no return specified.",
                "args": {
                    "anInt": "Param is an integer",
                    "aList": "Param is a list"
                }
            }
        ),
        (
            three_args_yes_type_yes_return,
            {
                "summary": "Take two strings, join them with 1 multiplied by glue and return its length.",
                "args": {
                    "some_string": "Some string",
                    "some_other_string": "Some other string",
                    "glue": "Added '0' as separators (default 1)"
                }
            }
        ),
        (
            just_test_types,
            {
                "summary": "Provides a test method to test types",
                "args": {
                    "a": "an integer (int)",
                    "b": "a string (str)",
                    "c": "a dictionary (dict)",
                    "d": "an array (list)",
                    "e": "a boolean (bool)",
                    "f": "a tuple",
                    "g": "a range",
                    "h": "a set",
                    "i": "a float"
                }
            }
        ),
        (
            connect_to_next_port,
            {
                "summary": "Connects to the next available port.",
                "args": {
                    "minimum": "A port value greater or equal to 1024"
                }
            }
        )
    ])

def test_get_func_doc_details(func, expected_dict):
    doc_extract = DocExtractor()
    doc = doc_extract.get_func_doc(func)
    assert(doc_extract.get_func_details(doc) == expected_dict)

