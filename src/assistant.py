import json
import logging
import re
from datetime import datetime

from dotenv import load_dotenv
from os import getenv
from os.path import abspath, dirname

# Uncomment following line to see debug logs
# logging.getLogger().setLevel(logging.DEBUG)

from llmclient import LLMClient
from llmtoolutil import llm_tool_util

from tools import *

### Initialize
load_dotenv()

no_func_regex = r'^no.(function|tool).*.available'


class Assistant:
    def __init__(self) -> None:
        """
        Initialize Assistant.
        """
        system_prompt = open(f'{dirname(abspath(__file__))}/prompts/assistant.md').read()
        system_message = system_prompt.format(date=datetime.today().strftime('%Y-%m-%d'),
                                              tools=json.dumps(llm_tool_util.generate_tool_markup()))
        logging.debug(system_message)

        # initialize llm client. Use `llama-3.1-70b-versatile` model
        self._client = LLMClient(url='https://api.groq.com/openai/v1/chat/completions',
                                 model='llama-3.1-70b-versatile',
                                 system_message=system_message,
                                 model_options={ "temperature": 0.1 },
                                 addn_headers={ 'Authorization': f'Bearer {getenv("GROQ_API_KEY")}' })


    def handle(self, user_message:str) -> str:
        """
        Once `LLMClient` returns a response:
        - Check if `llm_tool_util.can_handle_tool_call` can handle response
        - If so, call `llm_tool_util.handle_tool_call`. The function 
        invokes the tool and returns the tool's response, else returns None
        - If a tool response is returned, call the LLM with the result as JSON
        - A new, response at this point will be returned, based on the tool
        response
        """

        response = self._client.request(user_message)
        logging.debug(f"response = {response}")

        # if model responds that there is 'no function/tool to answer' OR calls a
        # non-existent tool, force it use training data
        if (re.search(no_func_regex, response, re.IGNORECASE) != None
            or (llm_tool_util.is_tool_call(response)
                and not llm_tool_util.can_handle_tool_call(response))):
            response = self._client.request('Use your training data to respond.')

        # check llm_tool_util, for tools that can handle response
        while llm_tool_util.can_handle_tool_call(response) == True:
            tool_response = llm_tool_util.handle_tool_call(response)
            logging.debug(f"tool_response = {tool_response}")
            response = self._client.request(json.dumps(tool_response))
            logging.debug(f"response = {response}")

        return response



#################
# Run Assistant #
#################
if __name__ == "__main__":
    assistant = Assistant()

    while True:
        try:
            msg = input("Enter message (⏎ or ^C to exit): ")
            if len(msg.strip()) == 0:
                break

            print(assistant.handle(msg))
        except KeyboardInterrupt as ki:
            break
        except Exception as e:
            print(f'Exception: {e}')
