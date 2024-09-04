import requests
import json
import logging

class LLMClient():
    """
    Simple LLM API wrapper client to invoke and return LLM response.

    This client is bare-bones and does not use any libraries, it simply invokes
    the LLM thru' the API endpoint.

    @TODO: Add ability to control whether to send history of messages
    """


    def __init__(self,
                 url:str,
                 model:str,
                 system_prompt:str,
                 model_options:dict = {},
                 addn_headers:dict = {}) -> None:
        """
        Initialize LLMClient

        url -- API endpoint
        model -- LLM to use for inference
        system_prompt -- System prompt for initializing messages
        model_options -- Configuration options for model. ex: { 'temperature': 0.1 } (default {})
        addn_headers -- Additional HTTP headers. ex: { 'Authorization': 'Bearer <GROQ_API_KEY>' } } (default {})
        """
        self.url = url
        self.model = model
        self.history = [{ 'role': 'system', 'content': system_prompt }]
        self.options = model_options
        self.additional_headers = addn_headers


    def request(self, prompt: str) -> str:
        """
        Request LLM API endpoint and return assistant response content as
        string.

        This request handler will extract the assistant's response, add it to
        the messages history and return to caller. If the LLM returns multiple
        choices, it will use first choice.

        set `logging.getLogger().setLevel(logging.DEBUG)` to see debug logs

        prompt -- User prompt to send to LLM.
        """
        self.history.append({ 'role': 'user', 'content': prompt })

        headers = {
            "Content-Type": "application/json",
        }
        headers.update(self.additional_headers)

        data = {
            "model": self.model,
            "messages": self.history,
            "stream": False,
        }
        data.update(self.options)

        response = requests.post(self.url, headers=headers, json=data)

        try:
            res_json = response.json()
            logging.debug(json.dumps(res_json))

            # If multiple choices returned, return first
            content = res_json['choices'][0]["message"]["content"] if 'choices' in res_json else res_json["message"]["content"]
            self.history.append({'role': 'assistant', 'content': content})

            return content
        except Exception as e:
            logging.critical(e)
            return response.text
