# Test functions


# No docstring.
# Will fail due to no doc
def no_doc():
    print('Hello World!')


# Empty doc string
# Will fail due to empty doc
def empty_doc():
    """
    """
    print('Hello World!')


# No args, but function returns string
# Will pass given it returns a string
def hello_doc() -> str:
    """
    This function returns Hello World!
    """
    return 'Hello World!'


# One arg with no type
# Will fail as no type for arg and no return type
def one_arg_no_type_no_return(param):
    """
    This function takes in a param and prints it

    param -- Some parameter that will be printed
    """
    ...


# One arg with type & int type
# Will fail bcoz no function description, only arg description
def one_arg_no_doc_desc(param:str) -> int:
    """
    param -- Some parameter that will be printed
    """
    return -1


# One arg with type, but no return type
# Will fail due to missing return type
def one_arg_type_no_return(param:int):
    """
    This function takes in an int param and returns a string

    param -- Some parameter that will be returned as a string
    """
    return "Hello World!"


# One arg with no type
# Will fail due to missing arg type
def one_arg_no_type_yes_return(param) -> int:
    """
    This function takes in a param and ignores it.

    param -- Some parameter that will be ignored
    """
    return -1


# Two args with types, but no return type
# Will fail due to missing return type
# @TODO: Fix test, as it fails
def two_args_yes_type_no_return(anInt:int, aList:list):
    """
    Annotated args with no return specified.

    anInt -- Param is an integer
    aList -- Param is a list
    """
    ...


# Three args with types, 1 default, return type, & docstring
# Will pass
def three_args_yes_type_yes_return(some_string:str,
                                   some_other_string:str,
                                   glue:int=1) -> int:
    """
    Take two strings, join them with 1 multiplied by glue and return its length.

    some_string -- Some string
    some_other_string -- Some other string
    glue -- Added '0' as separators (default 1)
    returns length of new string
    """
    return len(f'{some_string}{(1*glue)}{some_other_string}')


# Test different arg types & docstring
# Will pass due to valid doc + types
def just_test_types(a: int,
                    b: str,
                    c: dict,
                    d: list,
                    e: bool,
                    f: tuple,
                    g: range,
                    h: set,
                    i: float) -> str:
    """
    Provides a test method to test types

    a -- an integer (int)
    b -- a string (str)
    c -- a dictionary (dict)
    d -- an array (list)
    e -- a boolean (bool)
    f -- a tuple
    g -- a range
    h -- a set
    i -- a float
    """
    return '💥'


# Function with arg & return types and docstring
# Will pass
def connect_to_next_port(minimum:int) -> int:
    """Connects to the next available port.

    Args:
      minimum: A port value greater or equal to 1024

    Returns:
      The new minimum port.

    Raises:
      ConnectionError: If no available port is found.
    """
    return 1
