import logging
import json

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
    llm_response = client.request(...)

    if llm_tool_util.can_handle_tool(llm_response) == True:
        tool_response = llm_tool_util.handle_tool(llm_response)
        llm_response = client.request(tool_response)
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
        LLM and invoke them based on the LLM response.

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


    def can_handle_tool_response(self, llm_response:str) -> bool:
        """
        See @handle_tool_response. Returns bool if tool can be invoked.

        @TODO: Add tests
        """
        try:
            tool_json = json.loads(llm_response)
            if 'name' in tool_json and 'parameters' in tool_json:
                tool_name = tool_json['name']
                if tool_name in self._tool_funcs:
                    return True
        except ValueError as ve:
            return False
        else:
            return False


    def handle_tool_response(self, llm_response:str) -> dict | None:
        """
        If applicable, this function invokes the registered tool and returns
        the response from the tool.

        llm_response -- Response returned by LLM, which could include tool
        invocation

        returns dictionary response from calling tool, else None. None is
        returned in the following cases:
        1. `llm_response` was a string and not JSON
        2. The JSON was not for tool invocation
        3. There was an exception parsing the JSON
        4. No tool with the `name` is available
        5. There was an exception invoking the tool

        @TODO: Add tests
        """
        try:
            tool_json = json.loads(llm_response)
            if 'name' in tool_json and 'parameters' in tool_json:
                tool_name = tool_json['name']
                if tool_name in self._tool_funcs:
                    return self._tool_funcs[tool_name](**tool_json['parameters'])
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
