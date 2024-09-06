from inspect import getdoc, cleandoc
import json
import logging
from llmclient import LLMClient
from dotenv import load_dotenv
from os import getenv
from os.path import abspath, dirname

# Groq + llama3.1 (preferred) - Consistent responses, with 0 test failures
load_dotenv()

class DocExtractor:
    """
    Tool to extract summary and arguments from function docstring.

    @TODO: Add support for additional Python docstring formats
    """

    def __init__(self) -> None:
        """
        Initialize tool and configure to use LLMClient
        """
        self._client = LLMClient(url='https://api.groq.com/openai/v1/chat/completions',
                                 model='llama-3.1-8b-instant',
                                 system_prompt=open(f'{dirname(abspath(__file__))}/prompts/doc_extractor.md').read(),
                                 model_options={ "temperature": 0.1 },
                                 addn_headers={ 'Authorization': f'Bearer {getenv("GROQ_API_KEY")}' })


    def get_func_doc(self, func:callable) -> str | None:
        """
        Get doc string from function.

        func -- Function to extract docstring from
        returns -- cleaned docstring or None, if no docstring
        """
        # get and clean function doc
        doc = getdoc(func)
        doc = cleandoc(doc) if doc is not None else doc
        logging.debug(doc)
        return doc


    def get_func_details(self, doc:str) -> dict:
        """
        Function to extract the tool details. This is based on the documented in code.

        Requirements:
        1. Following documentation format: https://peps.python.org/pep-0257/#multi-line-docstrings
        2. Argument types must be specified
        3. Return type must be specified
        4. Documentation must include;
            4.1. Function description (Format `Add a description to be used`)
            4.2. Argument description (Format `<arg name>: <description>`)
        5. Provide enough details in description to allow LLM to determine the
        right use of the tool.

        def some_function(name: str, num: int = -1) -> str:
            \"\"\"
            This is a summary of what the function does

            This is a much more detailed description with more details.
            name: User's name
            num: Some number (defaults to -1)
            \"\"\"
        
        doc -- docstring for function
        returns -- dictionary with summary & args
        """
        # fetch function details using LLM
        str_res = self._client.request(doc)
        if "```json" in str_res:
            str_res = str_res[len("```json"):]
            if "```" in str_res:
                str_res = str_res[:str_res.index("```")]
        logging.debug(str_res)

        # delete 'returns' as we only need function args
        res_dict = json.loads(str_res)
        if 'returns' in res_dict['args']:
            del res_dict['args']['returns']
        
        return res_dict



########
# Demo #
########
if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)

    def some_func(user: str = 'World'):
        """
        Prints hello to the user.

        user -- Name of the user. (default=World)
        """
        print(f'Hello {user}!')

    # Initial tool
    doc_extract = DocExtractor()

    # Test function to get docstring from function
    # """
    # Prints hello to the user.
    #
    # user -- Name of the user. (default=World)
    # """
    doc = doc_extract.get_func_doc(some_func)
    logging.info(doc)

    # Test function to convert function docstring to dictionary
    # {
    #     "summary": "Prints hello to the user.",
    #     "args": {
    #         "user": "Name of the user. (default=World)"
    #     }
    # }
    details = doc_extract.get_func_details(doc)
    logging.info(details)
