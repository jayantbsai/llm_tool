import logging
import json
from datetime import datetime

from inspect import Parameter, getfullargspec, signature
from docextractor import DocExtractor


class _LLMToolUtil:
    """
    DO NOT USE this class directly. It is recommended to use the singleton that
    is created at the end of the code file.

    Usage in code:
    * Use the `llm_tool_util.llm_tool` decorator to identify to be exposed in prompt
    * Add docstring for python function
    ```
    from llmtoolutil import llm_tool_util

    @llm_tool_util.llm_tool
    def func_to_expose_to_llm(some_param:string) -> dict:
        ...
    ```

    Include JSON in prompt to make LLM aware of available tools
    ```
    prompt = f'...\n{llm_tool_util.generate_tool_markup()}'
    ```

    Usage in app/assistant response handling
    ```
    model_response = client.request(...)

    if llm_tool_util.is_tool_call(model_response) and llm_tool_util.can_handle_tool_call(model_response):
        tool_response = llm_tool_util.handle_tool_call(model_response)
        model_response = client.request(tool_response)
    ```
    """

    def __init__(self) -> None:
        """
        DO NOT USE. Use the `llm_tool_util` instance.
        """
        self._doc_extraction = DocExtractor()
        self._tool_funcs = {}
        self._tool_docs = {}


    def llm_tool(self, func:callable) -> callable:
        """
        Decorator for tools that should be exposed and made avaialble to the
        LLM. Unlike classic decorators, this does NOT wrap the original
        function. It is used to collect the functions that are exposed to the
        model and invoke them based on the LLM response.

        func: Function to be made available
        """
        name = func.__name__
        spec = getfullargspec(func)
        doc = self._doc_extraction.get_func_doc(func)

        warnings = []

        # raise warning if return is not specified
        if 'return' not in spec.annotations:
            warnings.append('Missing return type. All llm tool functions should return a value, to be subsequently used by the llm.\n')

        # raise warning if types are not specified for each argument
        if len(spec.args) != len(spec.annotations) + (-1 if 'return' in spec.annotations else 0):
            missing_types = [arg for arg in spec.args if arg not in spec.annotations]
            warnings.append(f'Missing argument type{"s" if len(missing_types) > 1 else ""} for: `{", ".join(missing_types)}`\n')

        # raise warning if no doc
        if doc is None or len(doc.strip()) == 0:
            warnings.append('Missing documentation.\n')
        else:
            # raise warning if docs missing for function or params
            doc_json = self._doc_extraction.get_func_details(doc)
            summary = doc_json.get("summary")
            args = doc_json.get("args")

            if summary is None or len(summary.strip()) == 0:
                warnings.append(f'Missing or invalid function summary.\n')
            elif summary not in doc:
                warnings.append(f'Function summary does not match input: `{summary}`\n')

            missing_params = [arg for arg in spec.args if arg not in args]
            if len(missing_params) > 0:
                warnings.append(f'Missing argument summary{"s" if len(missing_params) > 1 else ""} for: `{", ".join(missing_params)}`\n')

        # if no warnings, add function to collection
        if len(warnings) == 0:
            self._tool_funcs[name] = func
            self._tool_docs[name] = doc_json

            logging.info(f'✅ Function `{name}` passes all checks.\n')
        else:
            logging.critical(f'❌ Function `{name}` not added. It may not work as expected when included in prompt.\n * {" * ".join(warnings)}')

        return func
    

    def _clear_tools(self):
        """
        Clear all current tools. Used primarily for testing.
        """
        self._tool_funcs = {}
        self._tool_docs = {}


    def _map_type_to_name(self, t:type) -> str:
        """
        Return general type names, not Python specific class names

        t -- Type
        returns -- String name for type
        """
        # based on type, return a reader friendly type
        match t.__name__:
            case 'str':
                return 'string'
            case 'int':
                return 'integer'
            case 'dict':
                return 'dictionary'
            case 'list':
                return 'array'
            case 'bool':
                return 'boolean'
            case 'enum':
                return 'enumeration'

        return t.__name__


    def _convert_type(self, value:any, to:type) -> any:
        """
        Attempts to convert value to specified type.

        value - Object to be converted
        to - New type for Object
        """
        try:
            match to.__name__:
                case 'int':
                    return int(value)
                case 'float':
                    return float(value)
                case 'bool':
                    return bool(value)
                case 'datetime.datetime':
                    return datetime.strptime(value, '%Y-%m-%d')
        except Exception as e:
            logging.debug('Unable to convert type ({e})')

        return value


    def generate_tool_markup(self) -> list:
        """
        Using the list of tools, marked as `llm_tool`, this method generates
        markup that can be used within LLAMA 3.1 prompt for the LLM to use as a
        tool to retrieve information, if required.

        Usage in prompt
        ```
        prompt = f'...\n{llm_tool_util.generate_tool_markup()}'
        ```

        returns -- List of tools that can be used by LLM

        @TODO: Add support for tool markup for OpenAI
        """
        docs = self._tool_docs
        markup = []
        
        for (name, doc) in docs.items():
            func = self._tool_funcs[name]

            desc = doc.get("summary")
            args = doc.get('args')
            
            spec = getfullargspec(func)
            annos = spec.annotations
            sigs = signature(func)

            parameters = None

            if len(args) > 0:
                parameters = {
                    'type': 'object',
                    'properties': {
                        key: {
                            'type': self._map_type_to_name(annos[key]),
                            'description': args[key]
                            }
                        for key in args },
                    'required': [k for (k,v) in sigs.parameters.items() if v.default == Parameter.empty],
                }

            tool = {
                'type': 'function',
                'function': {
                    'name': name,
                    'description': desc,
                    'parameters': parameters,                
                },
            }

            markup.append(tool)

        return markup


    def is_tool_call(self, llm_response:str) -> bool:
        """
        Checks whether the response is in JSON format and is a tool call.
        Returns bool if tool response. This method is different from
        @can_handle_tool_call, it does not check whether there is a custom
        tool registered to be called.
        """
        try:
            tool_json = json.loads(llm_response)
            return 'name' in tool_json and 'parameters' in tool_json
        except ValueError as ve:
            return False


    def can_handle_tool_call(self, llm_response:str) -> bool:
        """
        See @handle_tool_call. Returns bool if tool can be invoked.
        """
        try:
            tool_json = json.loads(llm_response)
            if 'name' in tool_json and 'parameters' in tool_json:
                return tool_json['name'] in self._tool_funcs
        except ValueError as ve:
            return False
        else:
            return False


    def handle_tool_call(self, llm_response:str) -> dict | None:
        """
        If tool is available, invokes it and returns the response from the
        tool.

        llm_response - Response returned by model, which could include tool
        call.

        returns dictionary response from calling tool, else None. None is
        returned in the following cases:
        1. `llm_response` was a string and not JSON
        2. The JSON was not for custom tool call
        3. There was an exception parsing the JSON
        4. No tool with the `name` is available
        5. There was an exception invoking the tool

        @TODO: Add tests
        """
        try:
            tool_json = json.loads(llm_response)
            if 'name' in tool_json and 'parameters' in tool_json:
                tool_name = tool_json['name']

                # ensure argument is of correct type
                func = self._tool_funcs[tool_name]
                annos = getfullargspec(func).annotations

                params:dict = tool_json['parameters']
                for key, value in params.items():
                    params[key] = self._convert_type(value, annos[key])

                # invoke custom tool
                if tool_name in self._tool_funcs:
                    return func(**params)
        except ValueError as ve:
            logging.debug(ve)
            return None
        else:
            return None


"""
Singleton instance of _LLMToolUtil that must be used.
"""
llm_tool_util = _LLMToolUtil()



########
# Demo #
########
if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)

    @llm_tool_util.llm_tool
    def valid_func(user: str) -> str:
        """
        Simple function to say hello to user

        user -- Name of user
        returns -- String saying hello
        """
        return f'Hello {user}!'

    @llm_tool_util.llm_tool
    def invalid_func(user: str) -> str:
        return f'Hello {user}!'

    logging.info(llm_tool_util.generate_tool_markup())
