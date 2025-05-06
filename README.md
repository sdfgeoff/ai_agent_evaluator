# Ai Agent Evaluator

This project is a general purpose AI agent evaluator. It aims to compare LLM's agentic abilities using human comparison rather than mathematical numbers. This means:
 - You can evalutate it on abstract tasks like "make me a website for steve's mowing serviec"
 - It's very hard to benchmaxx
 - You can evalute based on your metrics of what makes a good model

The basic idea is quite simple. There is a folder of test cases.
Each test case is a folder, with a config.json file. The config.json file looks like:
```json
{
    "image": <a docker image to run in>,
    "blurb": <human readable text about what the test is trying to make the model do>,
    "prompt": <whatever your prompt is>,
    "thumbnail": <a command to generate a thumbnail of the output>
}
```

Then in config.py, there is a list of providers and models, eg:
```python
providers=[
    TestParameters(
        name: "local",
        base_url: "http://localhost",
        token: <your token>,
        models: [
            "qwen3-30b-a3b",
            "llama3.2-8b",
        ]
    )
]
```

Then for every model in every provider it will create a folder in output of the form:
```
<provider>/<model>/<test>
```
And inside that folder, run the model with the supplied test.

Some metadata about the run is then placed in a `_results` folder, This includes:
 - `log.txt` - a complete transcript of what the model did, tool calls, results etc.
 - `stats.json`, a json file that contains stats such as the time taken.
 - `thumbnail.jpg`, an image of the result.


When running each agent it will provide the following tools:
```
bash
create_file
read_file
write_file
get_url
```
The rest is up to the model.


# Further Ideas:
 - Allow test cases to specify additional MCP's 