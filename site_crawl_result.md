# https://fast-agent.ai/

## welcome to fast-agent

* **Set up in 5 minutes**

  Install [`fast-agent-mcp`](https://pypi.org/project/fast-agent-mcp/) with [`uv`](https://docs.astral.sh/uv/) and get up and running in minutes.
* **Batteries Included**

  Out-of-the box examples of sophisticated Agents, Workflows and advanced MCP Usage.
* **Comprehensive Test Suite**

  Comprehensive test automation, accelerating delivery and assuring quality.
* **MCP Feature Support**

  First MCP Host to support Tools, Prompts, Resources, Sampling and Roots ([Reference](mcp/)).
* **MCP Native**

  MCP-first design makes multi-modal Agent application development easy.
* **Agent Developer Friendly**

  Lightweight deployment - in-built Echo and Playback LLMs allow robust agent application testing.

## Getting Started

**fast-agent** lets you create and interact with sophisticated Agents and Workflows in minutes. It's multi-modal - supporting Images and PDFs in Prompts, Resources and MCP Tool Call results.

Prebuilt agents and examples implementing the patterns in Anthropic's [building effective agents](https://www.anthropic.com/engineering/building-effective-agents) paper get you building valuable applications quickly. Seamlessly use MCP Servers with your agents, or host your agents as MCP Servers.

* `uv pip install fast-agent-mcp` - Install fast-agent.
* `fast-agent setup` - Create Agent and Configuration files.
* `uv run agent.py` - Run your first Agent.
* `fast-agent bootstrap workflow` - Create Agent workflow examples.

![](welcome_small.png)


# https://fast-agent.ai/agents/

## Attaching Files

You can include files in a conversation using Paths:

```
from mcp_agent.core.prompt import Prompt
from pathlib import Path

plans = agent.send(
    Prompt.user(
        "Summarise this PDF",
        Path("secret-plans.pdf")
    )
)
```

This works for any mime type that can be tokenized by the model.

## MCP Resources

MCP Server resources can be conveniently included in a message with:

```
description = agent.with_resource(
    "What is in this image?",
    "mcp_image_server",
    "resource://images/cat.png"
)
```

## Prompt Files

Prompt Files can include Resources:

agent_script.txt

```
---USER
Please extract the major colours from this CSS file:
---RESOURCE
index.css
```

They can either be loaded with the `load_prompt_multipart` function, or delivered via the built-in `prompt-server`.



# https://fast-agent.ai/agents/defining/




# https://fast-agent.ai/agents/prompting/

**fast-agent** provides a flexible MCP based API for sending messages to agents, with convenience methods for handling Files, Prompts and Resources.

Read more about the use of MCP types in **fast-agent** [here](../../mcp/types/).

## Sending Messages

The simplest way of sending a message to an agent is the `send` method:

```
response: str = await agent.send("how are you?")
```

Attach files by using the `Prompt.user()` method to construct the message:

```
from mcp_agent.core.prompt import Prompt
from pathlib import Path

plans: str = await agent.send(
    Prompt.user(
        "Summarise this PDF",
        Path("secret-plans.pdf")
    )
)
```

Attached files are converted to the appropriate MCP Type (e.g. ImageContent for Images, EmbeddedResource for PDF and TextResource).

> Note: use `Prompt.assistant()` to produce messages for the `assistant` role.

### MCP Prompts

Apply a Prompt from an MCP Server to the agent with:

```
response: str = await agent.apply_prompt(
    "setup_sizing",
    arguments: {"units","metric"}
)
```

You can list and get Prompts from attached MCP Servers:

```
from mcp.types import GetPromptResult, PromptMessage

prompt: GetPromptResult = await agent.get_prompt("setup_sizing")
first_message: PromptMessage = prompt[0]
```

and send the native MCP `PromptMessage` to the agent with:

```
response: str = agent.send(first_message)
```

> If the last message in the conversation is from the `assistant`, it is returned as the response.

### MCP Resources

`Prompt.user` also works with MCP Resources:

```
from mcp.types import ReadResourceResult

resource: ReadResourceResult = agent.get_resource(
    "resource://images/cat.png", "mcp_server_name" 
)
response: str = agent.send(
    Prompt.user("What is in this image?", resource)
)
```

Alternatively, use the *with_resource* convenience method:

```
response: str = agent.with_resource(
    "What is in this image?",
    "resource://images/cat.png"
    "mcp_server_name",
)
```

### Prompt Files

Long prompts can be stored in text files, and loaded with the `load_prompt` utility:

```
from mcp_agent.mcp.prompts import load_prompt
from mcp.types import PromptMessage

prompt: List[PromptMessage] = load_prompt(Path("two_cities.txt"))
result: str = await agent.send(prompt[0])
```

two_cities.txt

```
### The Period

It was the best of times, it was the worst of times, it was the age of
wisdom, it was the age of foolishness, it was the epoch of belief, it was
the epoch of incredulity, ...
```

Prompts files can contain conversations to aid in-context learning or allow you to replay conversations with the Playback LLM:

sizing_conversation.txt

```
---USER
the moon
---ASSISTANT
object: MOON
size: 3,474.8
units: KM
---USER
the earth
---ASSISTANT
object: EARTH
size: 12,742
units: KM
---USER
how big is a tiger?
---ASSISTANT
object: TIGER
size: 1.2
units: M
```

Multiple messages (conversations) can be applied with the `generate()` method:

```
from mcp_agent.mcp.prompts import load_prompt
from mcp.types import PromptMessage

prompt: List[PromptMessage] = load_prompt(Path("sizing_conversation.txt"))
result: PromptMessageMultipart = await agent.generate(prompt)
```

Conversation files can also be used to include resources:

prompt_secret_plans.txt

```
---USER
Please review the following documents:
---RESOURCE
secret_plan.pdf
---RESOURCE
repomix.xml
---ASSISTANT
Thank you for those documents, the PDF contains secret plans, and some
source code was attached to achieve those plans. Can I help further?
```

It is usually better (but not necessary) to use `load_prompt_multipart`:

```
from mcp_agent.mcp.prompts import load_prompt_multipart
from mcp_agent.mcp.PromptMessageMultipart

prompt: List[PromptMessageMultipart] = load_prompt_multipart(Path("prompt_secret_plans.txt"))
result: PromptMessageMultipart = await agent.generate(prompt)
```

File Format / MCP Serialization

If the filetype is `json`, then messages are deserialized using the MCP Prompt schema format. The `load_prompt`, `load_prompt_multipart` and `prompt-server` will load either the text or JSON format directly.
See [History Saving](about:blank/models/#history-saving) to learn how to save a conversation to a file for editing or playback.

### Using the MCP prompt-server

Prompt files can also be served using the inbuilt `prompt-server`. The `prompt-server` command is installed with `fast-agent` making it convenient to set up and use:

fastagent.config.yaml

```
mcp:
  servers:
    prompts:
      command: "prompt-server"
      args: ["prompt_secret_plans.txt"]
```

This configures an MCP Server that will serve a `prompt_secret_plans` MCP Prompt, and `secret_plan.pdf` and `repomix.xml` as MCP Resources.

If arguments are supplied in the template file, these are also handled by the `prompt-server`

prompt_with_args.txt

```
---USER
Hello {{assistant_name}}, how are you?
---ASSISTANT
Great to meet you {{user_name}} how can I be of assistance?
```


# https://fast-agent.ai/agents/running/

**fast-agent** provides flexible deployment options to meet a variety of use cases, from interactive development to production server deployments.

## Interactive Mode

Run **fast-agent** programs interactively for development, debugging, or direct user interaction.

agent.py

```
import asyncio
from mcp_agent.core.fastagent import FastAgent

fast = FastAgent("My Interactive Agent")

@fast.agent(instruction="You are a helpful assistant")
async def main():
    async with fast.run() as agent:
        # Start interactive prompt
        await agent()

if __name__ == "__main__":
    asyncio.run(main())
```

When started with `uv run agent.py`, this begins an interactive prompt where you can chat directly with the configured agents, apply prompts, save history and so on.

## Command Line Execution

**fast-agent** supports command-line arguments to run agents and workflows with specific messages.

```
# Send a message to a specific agent
uv run agent.py --agent default --message "Analyze this dataset"

# Override the default model
uv run agent.py --model gpt-4o --agent default --message "Complex question"

# Run with minimal output
uv run agent.py --quiet --agent default --message "Background task"
```

This is perfect for scripting, automation, or one-off queries.

The `--quiet` flag switches off the Progress, Chat and Tool displays.

## MCP Server Deployment

Any **fast-agent** application can be deployed as an MCP (Message Control Protocol) server with a simple command-line switch.

### Starting an MCP Server

```
# Start as an SSE server (HTTP)
uv run agent.py --server --transport sse --port 8080

# Start as a stdio server (for piping to other processes)
uv run agent.py --server --transport stdio
```

Each agent exposes an MCP Tool for sending messages to the agent, and a Prompt that returns the conversation history.

This enables cross-agent state transfer via the MCP Prompts.

The MCP Server can also be started programmatically.

### Programmatic Server Startup

```
import asyncio
from mcp_agent.core.fastagent import FastAgent

fast = FastAgent("Server Agent")

@fast.agent(instruction="You are an API agent")
async def main():
    # Start as a server programmatically
    await fast.start_server(
        transport="sse",
        host="0.0.0.0",
        port=8080,
        server_name="API-Agent-Server",
        server_description="Provides API access to my agent"
    )

if __name__ == "__main__":
    asyncio.run(main())
```

## Python Program Integration

Embed **fast-agent** into existing Python applications to add MCP agent capabilities.

```
import asyncio
from mcp_agent.core.fastagent import FastAgent

fast = FastAgent("Embedded Agent")

@fast.agent(instruction="You are a data analysis assistant")
async def analyze_data(data):
    async with fast.run() as agent:
        result = await agent.send(f"Analyze this data: {data}")
        return result

# Use in your application
async def main():
    user_data = get_user_data()
    analysis = await analyze_data(user_data)
    display_results(analysis)

if __name__ == "__main__":
    asyncio.run(main())
```


# https://fast-agent.ai/mcp/

MCP Servers are configured in the `fastagent.config.yaml` file. Secrets can be kept in `fastagent.secrets.yaml`, which follows the same format (**fast-agent** merges the contents of the two files).

## Adding a STDIO Server

The below shows an example of configuring an MCP Server named `server_one`.

fastagent.config.yaml

```
mcp:
# name used in agent servers array
  server_one:
    # command to run
    command: "npx" 
    # list of arguments for the command
    args: ["@modelcontextprotocol/server-brave-search"]
    # key/value pairs of environment variables
    env:
      BRAVE_API_KEY: your_key
      KEY: value
  server_two:
    # and so on ...
```

This MCP Server can then be used with an agent as follows:

```
@fast.agent(name="Search", servers=["server_one"])
```

## Adding an SSE Server

To use SSE Servers, specify the `sse` transport and specify the endpoint URL and headers:

fastagent.config.yaml

```
mcp:
# name used in agent servers array
  server_two:
    transport: "sse"
    # url to connect
    url: "http://localhost:8000/sse"
    # timeout in seconds to use for sse sessions (optional)
    read_transport_sse_timeout_seconds: 300
    # request headers for connection
    headers: 
          Authorization: "Bearer <secret>"
```

## Roots

**fast-agent** supports MCP Roots. Roots are configured on a per-server basis:

fastagent.config.yaml

```
mcp:
  server_three:
    transport: "sse"
    url: "http://localhost:8000/sse"
    roots:
       uri: "file://...." 
       name: Optional Name
       server_uri_alias: # optional
```

As per the [MCP specification](https://github.com/modelcontextprotocol/specification/blob/41749db0c4c95b97b99dc056a403cf86e7f3bc76/schema/2025-03-26/schema.ts#L1185-L1191) roots MUST be a valid URI starting with `file://`.

If a server_uri_alias is supplied, **fast-agent** presents this to the MCP Server. This allows you to present a consistent interface to the MCP Server. An example of this usage would be mounting a local directory to a docker volume, and presenting it as `/mnt/data` to the MCP Server for consistency.

The data analysis example (`fast-agent bootstrap data-analysis` has a working example of roots).

## Sampling

Sampling is configured by specifying a sampling model for the MCP Server.

fastagent.config.yaml

```
mcp:
  server_four:
    transport: "sse"
    url: "http://localhost:8000/sse"
    sampling:
      model: "provider.model.<reasoning_effort>"        
```

Read more about The model string and settings [here](../models/). Sampling requests support vision - try [`@llmindset/mcp-webcam`](https://github.com/evalstate/mcp-webcam) for an example.


# https://fast-agent.ai/mcp/resources/

* [fast-agent](../..)
* [Agents](../../agents/defining/)
* [Models](../../models/)
* [MCP](../)

Below are some recommended resources for developing with the Model Context Protocol (MCP):

| Resource | Description |
| --- | --- |
| [Working with Files and Resources](https://llmindset.co.uk/posts/2025/01/mcp-files-resources-part1/) | Examining the options MCP Server and Host developers have for sharing rich content |
| [PulseMCP Community](https://www.pulsemcp.com/) | A community focussed site offering news, up-to-date directories and use-cases of MCP Servers |
| [Basic Memory](https://memory.basicmachines.co/docs/introduction) | High quality, markdown based knowledge base for LLMs - also good for Agent development |
| [Repomix](https://repomix.com/guide/) | Create LLM Friendly files from folders or directly from GitHub. Include as an MCP Server - or run from a script prior to create Agent inputs |
| [PromptMesh Tools](https://promptmesh.io/) | High quality tools and libraries at the cutting edge of MCP development |
| [mcp-hfspace](https://github.com/evalstate/mcp-hfspace) | Seamlessly connect to hundreds of Open Source models including Image and Audio generators and more |


# https://fast-agent.ai/mcp/types/

## MCP Type Compatibility

FastAgent is built to seamlessly integrate with the MCP SDK type system:

Conversations with assistants are based on `PromptMessageMultipart` – an extension of the MCP `PromptMessage` type, with support for multiple content sections. This type is expected to become native in a future version of MCP: https://github.com/modelcontextprotocol/specification/pull/198

## Message History Transfer

FastAgent makes it easy to transfer conversation history between agents:

history_transfer.py

```
@fast.agent(name="haiku", model="haiku")
@fast.agent(name="openai", model="o3-mini.medium")

async def main() -> None:
    async with fast.run() as agent:
        # Start an interactive session with "haiku"
        await agent.prompt(agent_name="haiku")
        # Transfer the message history to "openai" (using PromptMessageMultipart)
        await agent.openai.generate(agent.haiku.message_history)
        # Continue the conversation
        await agent.prompt(agent_name="openai")
```


# https://fast-agent.ai/models/

Models in **fast-agent** are specified with a model string, that takes the format `provider.model_name.<reasoning_effort>`

### Precedence

Model specifications in fast-agent follow this precedence order (highest to lowest):

1. Explicitly set in agent decorators
2. Command line arguments with `--model` flag
3. Default model in `fastagent.config.yaml`

### Format

Model strings follow this format: `provider.model_name.reasoning_effort`

* **provider**: The LLM provider (e.g., `anthropic`, `openai`, `deepseek`, `generic`, `openrouter`)
* **model_name**: The specific model to use in API calls
* **reasoning_effort** (optional): Controls the reasoning effort for supported models

Examples:

* `anthropic.claude-3-7-sonnet-latest`
* `openai.gpt-4o`
* `openai.o3-mini.high`
* `generic.llama3.2:latest`
* `openrouter.google/gemini-2.5-pro-exp-03-25:free`

#### Reasoning Effort

For models that support it (`o1`, `o1-preview` and `o3-mini`), you can specify a reasoning effort of **`high`**, **`medium`** or **`low`** - for example `openai.o3-mini.high`. **`medium`** is the default if not specified.

#### Aliases

For convenience, popular models have an alias set such as `gpt-4o` or `sonnet`. These are documented on the [LLM Providers](llm_providers/) page.

### Default Configuration

You can set a default model for your application in your `fastagent.config.yaml`:

```
default_model: "openai.gpt-4o" # Default model for all agents
```

### History Saving

You can save the conversation history to a file by sending a `***SAVE_HISTORY <filename>` message. This can then be reviewed, edited, loaded, or served with the `prompt-server` or replayed with the `playback` model.

File Format / MCP Serialization

If the filetype is `json`, then messages are serialized/deserialized using the MCP Prompt schema. The `load_prompt`, `load_prompt_multipart` and `prompt-server` will load either the text or JSON format directly.

This can be helpful when developing applications to:

* Save a conversation for editing
* Set up in-context learning
* Produce realistic test scenarios to exercise edge conditions etc. with the [Playback model](about:blank/internal_models/#playback)


# https://fast-agent.ai/models/internal_models/

**fast-agent** comes with two internal models to aid development and testing: `passthrough` and `playback`.

## Passthrough

By default, the `passthrough` model echoes messages sent to it.

### Fixed Responses

By sending a `***FIXED_RESPONSE <message>` message, the model will return `<message>` to any request.

### Tool Calling

By sending a `***CALL_TOOL <tool_name> [<json>]` message, the model will call the specified MCP Tool, and return a string containing the results.

## Playback

The `playback` model replays the first conversation sent to it. A typical usage may look like this:

playback.txt

```
---USER
Good morning!
---ASSISTANT
Hello
---USER
Generate some JSON
---ASSISTANT
{
   "city": "London",
   "temperature": 72
}
```

This can then be used with the `prompt-server`. You can apply the MCP Prompt to the agent programmatically with `apply_prompt` or with the `/prompts` command in the interactive shell.

Alternatively, you can load the file with `load_message_multipart`.

JSON contents can be converted to structured outputs:

```
@fast.agent(name="playback", model="playback")

...

playback_messages: List[PromptMessageMultipart] = load_message_multipart(Path("playback.txt"))
# Set up the Conversation
assert ("HISTORY LOADED") == agent.playback.generate(playback_messages)

response: str = agent.playback.send("Good morning!") # Returns Hello
temperature, _ = agent.playback.structured("Generate some JSON")
```

When the `playback` runs out of messages, it returns `MESSAGES EXHAUSTED (list size [a]) ([b] overage)`.

List size is the total number of messages originally loaded, and overage is the number of requests made after exhaustion.


# https://fast-agent.ai/models/llm_providers/

## Providers

For each model provider, you can configure parameters either through environment variables or in your `fastagent.config.yaml` file.

### Common Configuration Format

```
<provider>:
  api_key: "your_api_key" # Override with API_KEY env var
  base_url: "https://api.example.com" # Base URL for API calls
```

### Anthropic

Anthropic models support Text, Vision and PDF content.

**YAML Configuration:**

```
anthropic:
  api_key: "your_anthropic_key" # Required
  base_url: "https://api.anthropic.com/v1" # Default, only include if required
```

**Environment Variables:**

* `ANTHROPIC_API_KEY`: Your Anthropic API key
* `ANTHROPIC_BASE_URL`: Override the API endpoint

**Model Name Aliases:**

| Model Alias | Maps to                    |
| ----------- | -------------------------- |
| `claude`    | `claude-3-7-sonnet-latest` |
| `sonnet`    | `claude-3-7-sonnet-latest` |
| `sonnet35`  | `claude-3-5-sonnet-latest` |
| `sonnet37`  | `claude-3-7-sonnet-latest` |
| `haiku`     | `claude-3-5-haiku-latest`  |
| `haiku3`    | `claude-3-haiku-20240307`  |
| `haiku35`   | `claude-3-5-haiku-latest`  |
| `opus`      | `claude-3-opus-latest`     |
| `opus3`     | `claude-3-opus-latest`     |

### OpenAI

**fast-agent** supports OpenAI `gpt-4o`, `gpt-4o-mini`, `o1-preview`, `o1` and `o3-mini` models. Arbitrary model names are supported with `openai.<model_name>`. Supported modalities are model-dependent; check the [OpenAI Models Page](https://platform.openai.com/docs/models) for the latest information.

Structured outputs use the OpenAI API Structured Outputs feature. Future versions of **fast-agent** will have enhanced model capability handling.

**YAML Configuration:**

```
openai:
  api_key: "your_openai_key" # Default
  base_url: "https://api.openai.com/v1" # Default, only include if required
```

**Environment Variables:**

* `OPENAI_API_KEY`: Your OpenAI API key
* `OPENAI_BASE_URL`: Override the API endpoint

**Model Name Aliases:**

| Model Alias   | Maps to      |
| ------------- | ------------ |
| `gpt-4o`      | `gpt-4o`     |
| `gpt-4o-mini` | `gpt-4o-mini`|
| `o1`          | `o1`         |
| `o1-mini`     | `o1-mini`    |
| `o1-preview`  | `o1-preview` |
| `o3-mini`     | `o3-mini`


# https://fast-agent.ai/welcome/

# Index - fast-agent documentation

As featured on [PulseMCP](https://www.pulsemcp.com/posts/newsletter-cursor-10b-levels-flies-mcp-hype#featured) – find thousands of MCP Servers for your Agents [here](https://www.pulsemcp.com/servers).
