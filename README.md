# Ai Agent Evaluator

This project is a general purpose AI agent evaluator. It aims to compare LLM's agentic abilities using human comparison rather than mathematical numbers. This means:
 - You can evalutate it on abstract tasks like "make me a website for steve's mowing serviec"
 - It's very hard to benchmaxx
 - You can evalute based on your metrics of what makes a good model

The results of this repo being run on some common models is available at https://sdfgeoff.github.io/ai_agent_evaluator/


To run this repo:
```
./run.sh
```
Will do what you want. It will call cargo build with the right parameters, and use uv to fetch/run the python stuff.

 # How it Works:

The basic idea is quite simple. There is a folder of test cases.
Each test case is a folder, with a config.json file. The config.json file looks like:
```json
{
	"name": "Hello World HTML",
    "docker_image": "ghcr.io/astral-sh/uv:python3.13-bookworm",
    "blurb": "Can the model create a simple html webpage",
    "initial_prompt": [
		{
			"content":"Create a single index.html file containing a hello world. Include styling in a dark theme with bold and striking color choice.",
			"role": "user"
		}
	],
	"allowed_tools": [
		"bash",
		"create_file"
	]
}
```

Then in config.py, there is a list of providers and models, eg:
```python
providers=[
    ModelProvider(
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
And using the specified docker image, mount that folder and run the model with the supplied prompt.

After the run is complete, a summary of the run is placed in
```
<provider>/<model>/<test>/stats.json
```
This includes the entire message stack, tool calls etc.

From there a static site generator generates an index HTML.

# Repo Structure and Developer Notes 

The repo consists of three parts:
 - The scaffold. This is the code that figures out what tests to run, and launches docker container containing them.
 - The agent. This is code that is copied/runs inside the docker container when running a test. It contains the agentic loop, tools the LLM has access to etc.
 - The site generator. This generates a human viewable site that sums up the results.

## simple-agent
To allow tests to be run in just about any docker container, the agent is written in rust and compiled to a single staticly linked binary (even using musl rather than glibc!). This means that there is no need for the docker container to have python, npm or anything. It just needs to be a reasonably standard linux container.

