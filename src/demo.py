import json
import logging
from datetime import datetime

from dotenv import load_dotenv
from os import getenv
from os.path import abspath, dirname

from llmclient import LLMClient
from llmtoolutil import llm_tool_util

from demo_tools import *

### Initialize
load_dotenv()


class Demo:
    def __init__(self) -> None:
        """
        Initialize Demo App.
        """
        system_prompt = open(f'{dirname(abspath(__file__))}/prompts/demo.md').read()
        prompt = system_prompt.format(date=datetime.today().strftime('%Y-%m-%d'),
                                      tools=json.dumps(llm_tool_util.generate_tool_markup()))
        logging.debug(prompt)

        # Initialize llm client. Use `llama-3.1-70b-versatile` model
        self._client = LLMClient(url='https://api.groq.com/openai/v1/chat/completions',
                                 model='llama-3.1-70b-versatile',
                                 system_prompt=prompt,
                                 model_options={ "temperature": 0.1 },
                                 addn_headers={ 'Authorization': f'Bearer {getenv("GROQ_API_KEY")}' })


    def request(self, prompt:str) -> str:
        """
        Once `LLMClient` returns a response:
        - Check if `llm_tool_util.can_handle_tool_response` can handle response
        - If so, invoke `llm_tool_util.handle_tool_response`. The function 
        invokes the tool and returns the tool's response, else returns None
        - If a tool response is returned, invoke the LLM with the result as
        JSON
        - A new, response at this point will be returned, based on the tool
        response
        """

        response = self._client.request(prompt)
        logging.debug(f"response = {response}")

        # If LLM responds that there is no tool/function to answer, force it
        # use training data
        if response.startswith('No function available') or response.startswith('No function call available') or response.startswith('No tool available'):
            response = self._client.request('Use your training data to respond.')

        # Check llm_tool_util, for tools that can handle response
        while llm_tool_util.can_handle_tool_response(response) == True:
            tool_response = llm_tool_util.handle_tool_response(response)
            logging.debug(f"tool_response = {tool_response}")
            response = self._client.request(json.dumps(tool_response))
            logging.debug(f"response = {response}")

        return response



########
# DEMO #
########
if __name__ == "__main__":
    assistant = Demo()

    while True:
        try:
            msg = input("Enter prompt (⏎ or ^C to exit): ")
            if len(msg.strip()) == 0:
                break

            print(assistant.request(msg))
        except KeyboardInterrupt as ki:
            break
        except Exception as e:
            print(f'Exception: {e}')
