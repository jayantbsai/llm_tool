# LLM Tool
Tool to extract and convert the Python docstring into a tool that can be 
invoked by a LLM.

### General Notes
* The goal of the code is to be bare-metal and minimize the use of libraries.
* This tool is based on [Llama 3.1 JSON tool calling](https://llama.meta.com/docs/model-cards-and-prompt-formats/llama3_1/#json-based-tool-calling) documentation
* This code is a POC
    * It has NOT been tested extensively across different LLMs
    * Prompts have not been optimized to ensure LLM errors/hallucination
* The code uses Llama 3.1 8b & 70b family of models.
    * [8b](https://console.groq.com/docs/models#llama-31-8b-preview): Python docstring extraction
    * [70b](https://console.groq.com/docs/models#llama-31-70b-preview): Tool invocation and simple assistant response


## Setup
After cloning repo, run following command to setup a virtual environment and 
install python dependencies:
```
$> cd llm_tool
$> python -m venv .venv
$> source .venv/bin/activate
$> pip install -r requirements.txt
```

### Groq (Recommended)
Navigate to [Groq](https://console.groq.com/docs/quickstart) and generate new
API key.

Create a new file `src/.env` file and add generated API key.
```
GROQ_API_KEY=<groq api key>
```

### Run Demo

Run demo app to ask questions and check weather forecast. _(LLM output can vary, but should be similar)_
```
$> cd src
$> python demo.py
Enter prompt (⏎ or ^C to exit): Who was the first president of the united states?
George Washington was the first president of the United States.
Enter prompt (⏎ or ^C to exit): Who was the first ever female prime minister?
Sirimavo Bandaranaike of Ceylon (now Sri Lanka) was the first female prime minister in the world, serving from 1960 to 1965 and then again from 1970 to 1977, and from 1994 to 2000.
Enter prompt (⏎ or ^C to exit): What will the temperature be in London, next Monday?
The temperature in London next Monday will be between 61.6°F and 74.9°F.
```


### Running Code

In addition to `demo.py`, the `docextractor.py` and `llmtoolutil.py` can also
be run from the command line.

Running `docextractor.py` prints docstring and dictionary returned by llm
```
$> python docextractor.py
INFO:root:Prints hello to the user.

user -- Name of the user. (default=World)
INFO:root:{'summary': 'Prints hello to the user.', 'args': {'user': 'Name of the user. (default=World)'}}
```

Running `llmtoolutil.py` adds `valid_func` as tool exposed to llm, but not `invalid_func`.
```
$> python llmtoolutil.py
INFO:root:✅ Function `valid_func` passes all checks.

CRITICAL:root:❌ Function `invalid_func` not added. It may not work as expected when included in prompt.
 * Missing documentation.

INFO:root:[{'type': 'function', 'function': {'name': 'valid_func', 'description': 'Simple function to say hello to user', 'parameters': {'type': 'object', 'properties': {'user': {'type': 'string', 'description': 'Name of user'}}, 'required': ['user']}}}]
```


### Running Tests

The repo includes pytests for the different code files:
```
$> cd tests
$> pytest

======================================= test session starts =======================================
platform darwin -- Python 3.11.6, pytest-8.3.2, pluggy-1.5.0
rootdir: /llm_tool
collected 47 items

tests/demo_tools/test_weather_tool.py .....                                                  [ 10%]
tests/test_demo.py ....                                                                      [ 19%]
tests/test_docextractor.py ................F...                                              [ 61%]
tests/test_llmtoolutil.py ..................                                                 [100%]

=========================================== FAILURES ==============================================
________________ test_get_func_details[two_args_yes_type_no_return-expected_dict5] ________________

... output ommitted

    def test_get_func_details(func, expected_dict):
        doc_extract = DocExtractor()
        doc = doc_extract.get_func_doc(func)
>       assert(doc_extract.get_func_details(doc) == expected_dict)
E       AssertionError: assert {'args': {'aL...'summary': ''} == {'args': {'aL...n specified.'}
E         
E         Omitting 1 identical items, use -vv to show
E         Differing items:
E         {'summary': ''} != {'summary': 'Annotated args with no return specified.'}
E         Use -v to get more diff

tests/test_docextractor.py:191: AssertionError
===================================== short test summary info =====================================
FAILED tests/test_docextractor.py::test_get_func_details[two_args_yes_type_no_return-expected_dict5] - AssertionError: assert {'args': {'aL...'summary': ''} == {'args': {'aL...n specified.'}
================================== 1 failed, 46 passed in 48.73s ==================================

```


## References:
* [Llama 3.1 JSON tool calling](https://llama.meta.com/docs/model-cards-and-prompt-formats/llama3_1/#json-based-tool-calling)
* [OpenAI Function calling](https://platform.openai.com/docs/assistants/tools/function-calling)
* [Open-Mateo Weather Forecast API](https://open-meteo.com/en/docs)


## TODOs:
* Add tests for `llmtoolgen.can_handle_tool_response` & `llmtoolgen.handle_tool_response`
* Update `doc_extractor` & `demo` prompts to reduce errors
    * `two_args_yes_type_no_return` extraction summary periodically returns `""`
    * `dates` are not in `YYYY-MM-DD` format
    * General knowledge questions should use training data and not non-existent tools
* Handle cases where Groq inference fails/exceeds rate limits
* Fix issue when `pytest` on full test suite leads to higher test failure rate
* Add support for [Llama 3.1 custom tool calling](https://llama.meta.com/docs/model-cards-and-prompt-formats/llama3_1/#user-defined-custom-tool-calling)
* Add support for [OpenAI/GPT function calling](https://platform.openai.com/docs/assistants/tools/function-calling)
