# LLM Tool
Library to extract and convert Python function details into a tool that is
callable by LLMs.


### General Notes
* The library code is bare-metal and minimizes use of libraries:
    * Uses `requests` for making network requests
    * Uses `pytest` for tests.
* It is based on [Llama 3.1 JSON tool calling](https://llama.meta.com/docs/model-cards-and-prompt-formats/llama3_1/#json-based-tool-calling) documentation
* This code is a proof-of-concept:
    * It has NOT been tested extensively across different LLMs
    * Prompts have not been optimized to ensure model errors/hallucination
* The code uses Llama 3.1 8b & 70b family of models.
    * [8b](https://console.groq.com/docs/models#llama-31-8b-preview): Python docstring extraction
    * [70b](https://console.groq.com/docs/models#llama-31-70b-preview): Tool calling and assistant response


## Setup
After cloning repo, run following command to setup a virtual environment and 
install python dependencies:
```
% cd llm_tool
llm_tool % python -m venv .venv
llm_tool % source .venv/bin/activate
(.venv) llm_tool % pip install -r requirements.txt
```


### Groq (Recommended)
Navigate to [Groq](https://console.groq.com/docs/quickstart) and generate new
API key.

Create a new file `src/.env` file and add generated API key.
```
GROQ_API_KEY=<groq api key>
```


### Run Assistant

Run assistant to ask questions and check weather forecast. _(model output can vary, but should be similar)_
```
(.venv) llm_tool % cd src
(.venv) src % python assistant.py
Enter message (⏎ or ^C to exit): Who was the first president of the united states?
George Washington was the first president of the United States.
Enter message (⏎ or ^C to exit): Who was the first ever female prime minister?
Sirimavo Bandaranaike of Ceylon (now Sri Lanka) was the first female prime minister in the world, serving from 1960 to 1965 and then again from 1970 to 1977, and from 1994 to 2000.
Enter message (⏎ or ^C to exit): What will the temperature be in London, next Monday?
On Monday, September 16, in London, the temperature will be between 58.8°F and 67.8°F, with no precipitation, and wind speeds ranging from 3.3 to 7.0 miles per hour.
```


### Adding Your Function
You can add your own function easily and make it available to the LLM to call:
1. Copy/create python file with your function in `src/tools` directory.
2. In `my_code_file.py`, add `from llmtoolutil import llm_tool_util`
3. **Annotate** the function arguments & return types. (Ex [function signature](src/tools/weather_tool.py#L11))
4. **Document** function description and each argument. (Ex [docs](src/tools/weather_tool.py#L12C5-L20C11))
5. **Decorate** function with `@llm_tool_util.llm_tool`. (Ex [decorator](src/tools/weather_tool.py#L10))

Run assistant.py to test:
```
(.venv) src % python assistant.py
Enter message (⏎ or ^C to exit): <Ask a question to invoke your tool>
<Model response based on your function response should be displayed here>
```

**Issues:**
* If your tool is not invoked, [uncomment code](src/assistant.py#L11) and re-run.
* Ensure tool is included in prompt:
```
<tools>
[list of tools in json format]
</tools>
```
* Ensure the function documentation is valid. If successfully loaded, you should see:
```
INFO:root:✅ Function `my_function` passes all checks.
```
* Else, an appropriate error is printed. For example:
```
CRITICAL:root:❌ Function `get_weather_forecast` not added. It may not work as expected when included in prompt.
 * Missing argument summary for: `lon`
```


### Running Code

In addition to `assistant.py`, the `docextractor.py` and `llmtoolutil.py` can also
be run from the command line.

Running `docextractor.py` prints docstring and dictionary returned by model
```
(.venv) src % python docextractor.py
INFO:root:Prints hello to the user.

user -- Name of the user. (default=World)
INFO:root:{'summary': 'Prints hello to the user.', 'args': {'user': 'Name of the user. (default=World)'}}
```

Running `llmtoolutil.py` adds `valid_func` as tool exposed to model, but not `invalid_func`.
```
(.venv) src % python llmtoolutil.py
INFO:root:✅ Function `valid_func` passes all checks.

CRITICAL:root:❌ Function `invalid_func` not added. It may not work as expected when included in prompt.
 * Missing documentation.

INFO:root:[{'type': 'function', 'function': {'name': 'valid_func', 'description': 'Simple function to say hello to user', 'parameters': {'type': 'object', 'properties': {'user': {'type': 'string', 'description': 'Name of user'}}, 'required': ['user']}}}]
```


### Running Tests

The repo includes pytests for the different code files:
```
(.venv) llm_tool % pytest

================================== test session starts ===================================
platform darwin -- Python 3.11.6, pytest-8.3.2, pluggy-1.5.0
rootdir: /llm_tool
collected 59 items

tests/tools/test_weather_tool.py .....                                              [  8%]
tests/test_assistant.py ....                                                        [ 15%]
tests/test_docextractor.py ................F...                                     [ 49%]
tests/test_llmtoolutil.py ...............FFF............                            [100%]

====================================== FAILURES ==========================================
... output ommitted ...
```


## References:
* [Llama 3.1 JSON tool calling](https://llama.meta.com/docs/model-cards-and-prompt-formats/llama3_1/#json-based-tool-calling)
* [OpenAI Function calling](https://platform.openai.com/docs/assistants/tools/function-calling)
* [Open-Mateo Weather Forecast API](https://open-meteo.com/en/docs)


## TODOs:
* Add tests for `llmtoolgen.handle_tool_call`
* Update `doc_extractor` & `assistant` prompts to reduce errors
    * `two_args_yes_type_no_return` extraction summary periodically returns `""`
    * `dates` are sometimes not in `YYYY-MM-DD` format
    * General knowledge questions should use training data and not non-existent tools
* Handle cases where Groq inference fails/exceeds rate limits
* Fix issue when `pytest` on full test suite leads to higher test failure rate
* Add support for multiple tool calls in single model response
* Support functions to provide prompt additions for system/user messages
* Format hints as part of tool response
* Add retry logic for failures
* Add support for [Llama 3.1 custom tool calling](https://llama.meta.com/docs/model-cards-and-prompt-formats/llama3_1/#user-defined-custom-tool-calling)
* Add support for [OpenAI/GPT function calling](https://platform.openai.com/docs/assistants/tools/function-calling)
