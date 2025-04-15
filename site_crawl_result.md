# https://github.com/google/A2A/tree/main/samples/python/common

The site's robots.txt disallows autonomous fetching of this page, so I was unable to retrieve its content automatically.

You can try manually fetching the page using your browser or another tool if you need to view it.


# https://github.com/google/A2A

The site’s robots.txt disallows autonomous fetching of that page. You may try using your browser or another tool, or manually fetch the page using the fetch prompt in your UI if that's available.


# https://github.com/google/A2A/tree/main/samples

The site's robots.txt disallows autonomous fetching of that page. You might consider using your browser or another tool to view it.


# https://github.com/google/A2A/blob/main/samples/python/hosts/cli/README.md

The CLI is a small host application that demonstrates the capabilities of an A2AClient. It supports reading a server's AgentCard and text-based collaboration with a remote agent. All content received from the A2A server is printed to the console.

The client will use streaming if the server supports it.

## Prerequisites

* Python 3.13 or higher
* UV
* A running A2A server

## Running the CLI

1. Navigate to the samples directory:

   ```
   cd samples/python
   ```
2. Run the example client

   ```
   uv run hosts/cli --agent [url-of-your-a2a-server]
   ```

   for example `--agent http://localhost:10000`. More command line options are documented in the source code.


# https://github.com/google/A2A/tree/main/samples/python/agents/crewai/README.md

## CrewAI Agent with A2A Protocol

This sample demonstrates a simple image generation agent built with [CrewAI](https://www.crewai.com/open-source) and exposed through the A2A protocol.

## How It Works

This agent utilizes CrewAI and the Google Gemini API to generate images based on text prompts. The A2A protocol enables standardized interaction with the agent, allowing clients to send requests and receive images as artifacts.

```
sequenceDiagram
    participant Client as A2A Client
    participant Server as A2A Server
    participant Agent as CrewAI Agent
    participant API as Gemini API

    Client->>Server: Send task with text prompt
    Server->>Agent: Forward prompt to image agent
    Note over Server,Agent: Optional: Simulated streaming updates
    Agent->>API: Generate image using Gemini
    API->>Agent: Return generated image
    Agent->>Server: Store image and return ID
    Server->>Client: Respond with image artifact
```

## Key Components

* **CrewAI Agent**: Image generation agent with specialized tools
* **A2A Server**: Provides standardized protocol for interacting with the agent
* **Image Generation**: Uses Gemini API to create images from text descriptions
* **Cache System**: Stores generated images for retrieval (in-memory or file-based)

## Prerequisites

* Python 3.12 or higher
* UV package manager (recommended)
* Google API Key (for Gemini access)

## Setup & Running

1. Navigate to the samples directory:

   ```
   cd samples/python/agents/crewai
   ```
2. Create an environment file with your API key:

   ```
   echo "GOOGLE_API_KEY=your_api_key_here" > .env
   ```
3. Set up the Python environment:

   ```
   uv python pin 3.12
   uv venv
   source .venv/bin/activate
   ```
4. Run the agent with desired options:

   ```
   # Basic run
   uv run .

   # On custom host/port
   uv run . --host 0.0.0.0 --port 8080
   ```
5. In a separate terminal, run the A2A client:

   ```
   # Connect to the agent (specify the agent URL with correct port)
   uv run hosts/cli --agent http://localhost:10001

   # If you changed the port when starting the agent, use that port instead
   # uv run hosts/cli --agent http://localhost:YOUR_PORT
   ```

## Features & Improvements

**Features:**

* Text-to-image generation using Google Gemini
* Support for modifying existing images using references
* Robust error handling with automatic retries
* Optional file-based cache persistence
* Improved artifact ID extraction from queries

**Limitations:**

* No true streaming (CrewAI doesn't natively support it)
* Limited agent interactions (no multi-turn conversations)

## Learn More

* [A2A Protocol Documentation](https://google.github.io/A2A/#/documentation)
* [CrewAI Documentation](https://docs.crewai.com/introduction)
* [Google Gemini API](https://ai.google.dev/gemini-api)


# https://github.com/google/A2A/tree/main/samples/python/agents/google_adk/README.md

## ADK Agent

This sample uses the Agent Development Kit (ADK) to create a simple "Expense Reimbursement" agent that is hosted as an A2A server.

This agent takes text requests from the client and, if any details are missing, returns a webform for the client (or its user) to fill out. After the client fills out the form, the agent will complete the task.

## Prerequisites

* Python 3.9 or higher
* UV
* Access to an LLM and API Key

## Running the Sample

1. Navigate to the samples directory:

   ```
   cd samples/python/agents/google_adk
   ```
2. Create an environment file with your API key:

   ```
   echo "GOOGLE_API_KEY=your_api_key_here" > .env
   ```
3. Run an agent:

   ```
   uv run .
   ```
4. Run one of the [client apps](/google/A2A/blob/main/samples/python/hosts/README.md)


# https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/

APR 09, 2025

[Miku Jha](/en/search/?author=Miku+Jha)  
Director, AI/ML Partner Engineering  
Google Cloud

[Todd Segal](/en/search/?author=Todd+Segal)  
Principal Engineer  
Business Application Platform

## **A new era of Agent Interoperability**

AI agents offer a unique opportunity to help people be more productive by autonomously handling many daily recurring or complex tasks. Today, enterprises are increasingly building and deploying autonomous agents to help scale, automate and enhance processes throughout the workplace–from ordering new laptops, to aiding customer service representatives, to assisting in supply chain planning.

To maximize the benefits from agentic AI, it is critical for these agents to be able to collaborate in a dynamic, multi-agent ecosystem across siloed data systems and applications. Enabling agents to interoperate with each other, even if they were built by different vendors or in a different framework, will increase autonomy and multiply productivity gains, while lowering long-term costs.

**Today, we’re launching a new, open protocol called Agent2Agent (A2A), with support and contributions from more than 50 technology partners** like Atlassian, Box, Cohere, Intuit, Langchain, MongoDB, PayPal, Salesforce, SAP, ServiceNow, UKG and Workday; and leading service providers including Accenture, BCG, Capgemini, Cognizant, Deloitte, HCLTech, Infosys, KPMG, McKinsey, PwC, TCS, and Wipro. The A2A protocol will allow AI agents to communicate with each other, securely exchange information, and coordinate actions on top of various enterprise platforms or applications. We believe the A2A framework will add significant value for customers, whose AI agents will now be able to work across their entire enterprise application estates.

This collaborative effort signifies a shared vision of a future when AI agents, regardless of their underlying technologies, can seamlessly collaborate to automate complex enterprise workflows and drive unprecedented levels of efficiency and innovation.

A2A is an open protocol that complements Anthropic's Model Context Protocol (MCP), which provides helpful tools and context to agents. Drawing on Google's internal expertise in scaling agentic systems, we designed the A2A protocol to address the challenges we identified in deploying large-scale, multi-agent systems for our customers. A2A empowers developers to build agents capable of connecting with any other agent built using the protocol and offers users the flexibility to combine agents from various providers. Critically, businesses benefit from a standardized method for managing their agents across diverse platforms and cloud environments. We believe this universal interoperability is essential for fully realizing the potential of collaborative AI agents.

![Google Cloud - Partners contributing to the Agent 2 Agent protocol - Accenture, Arize, Articul, ask-ai, Atlassian, BCG, Box, c3.ai, Capgemini, Chronosphere, Cognizant, Cohere, Colibra, Contextual.ai, Cotality, Datadog, and more](https://storage.googleapis.com/gweb-developer-goog-blog-assets/images/image1_yEPzdSr.original.png)

## A2A design principles

A2A is an open protocol that provides a standard way for agents to collaborate with each other, regardless of the underlying framework or vendor. While designing the protocol with our partners, we adhered to five key principles:

* **Embrace agentic capabilities**: A2A focuses on enabling agents to collaborate in their natural, unstructured modalities, even when they don’t share memory, tools and context. We are enabling true multi-agent scenarios without limiting an agent to a “tool.”

* **Build on existing standards:** The protocol is built on top of existing, popular standards including HTTP, SSE, JSON-RPC, which means it’s easier to integrate with existing IT stacks businesses already use daily.

* **Secure by default**: A2A is designed to support enterprise-grade authentication and authorization, with parity to OpenAPI’s authentication schemes at launch.

* **Support for long-running tasks:** We designed A2A to be flexible and support scenarios where it excels at completing everything from quick tasks to deep research that may take hours and or even days when humans are in the loop. Throughout this process, A2A can provide real-time feedback, notifications, and state updates to its users.

* **Modality agnostic:** The agentic world isn’t limited to just text, which is why we’ve designed A2A to support various modalities, including audio and video streaming.

## How A2A works

![an illustrated flow chart showing the flow of data between the remote agent and the client agent to produce secure collaboration, task and state management, user experience negotiation, and capability discovery](https://storage.googleapis.com/gweb-developer-goog-blog-assets/images/image5_VkAG0Kd.original.png)

A2A facilitates communication between a "client" agent and a “remote” agent. A client agent is responsible for formulating and communicating tasks, while the remote agent is responsible for acting on those tasks in an attempt to provide the correct information or take the correct action. This interaction involves several key capabilities:

* **Capability discovery:** Agents can advertise their capabilities using an “Agent Card” in JSON format, allowing the client agent to identify the best agent that can perform a task and leverage A2A to communicate with the remote agent.

* **Task management:** The communication between a client and remote agent is oriented towards task completion, in which agents work to fulfill end-user requests. This “task” object is defined by the protocol and has a lifecycle. It can be completed immediately or, for long-running tasks, each of the agents can communicate to stay in sync with each other on the latest status of completing a task. The output of a task is known as an “artifact.”

* **Collaboration:** Agents can send each other messages to communicate context, replies, artifacts, or user instructions.

* **User experience negotiation:** Each message includes “parts,” which is a fully formed piece of content, like a generated image. Each part has a specified content type, allowing client and remote agents to negotiate the correct format needed and explicitly include negotiations of the user’s UI capabilities–e.g., iframes, video, web forms, and more.

See the full details of how the protocol works in our [draft specification](https://github.com/google/A2A).

## A real-world example: candidate sourcing

[![Video thumbnail](https://storage.googleapis.com/gweb-developer-goog-blog-assets/original_videos/wagtailvideo-jtw5bpu9_thumb.jpg)](https://storage.googleapis.com/gweb-developer-goog-blog-assets/original_videos/A2A_demo_v4.mp4)

right click to view in new tab

Hiring a software engineer can be significantly simplified with A2A collaboration. Within a unified interface like Agentspace, a user (e.g., a hiring manager) can task their agent to find candidates matching a job listing, location, and skill set. The agent then interacts with other specialized agents to source potential candidates. The user receives these suggestions and can then direct their agent to schedule further interviews, streamlining the candidate sourcing process. After the interview process completes, another agent can be engaged to facilitate background checks. This is just one example of how AI agents need to collaborate across systems to source a qualified job candidate.

## The future of agent interoperability

A2A has the potential to unlock a new era of agent interoperability, fostering innovation and creating more powerful and versatile agentic systems. We believe that this protocol will pave the way for a future where agents can seamlessly collaborate to solve complex problems and enhance our lives.

We’re committed to building the protocol in collaboration with our partners and the community in the open. We’re releasing the protocol as open source and setting up clear pathways for contribution.

Review the [full specification draft](https://github.com/google/A2A), try out code samples, and see example scenarios on the [A2A website](https://google.github.io/A


# https://github.com/google/A2A/tree/main/samples/python/agents/langgraph/README.md

## LangGraph Currency Agent with A2A Protocol

This sample demonstrates a currency conversion agent built with [LangGraph](https://langchain-ai.github.io/langgraph/) and exposed through the A2A protocol. It showcases conversational interactions with support for multi-turn dialogue and streaming responses.

## How It Works

This agent uses LangGraph with Google Gemini to provide currency exchange information through a ReAct agent pattern. The A2A protocol enables standardized interaction with the agent, allowing clients to send requests and receive real-time updates.

```
sequenceDiagram
    participant Client as A2A Client
    participant Server as A2A Server
    participant Agent as LangGraph Agent
    participant API as Frankfurter API

    Client->>Server: Send task with currency query
    Server->>Agent: Forward query to currency agent

    alt Complete Information
        Agent->>API: Call get_exchange_rate tool
        API->>Agent: Return exchange rate data
        Agent->>Server: Process data & return result
        Server->>Client: Respond with currency information
    else Incomplete Information
        Agent->>Server: Request additional input
        Server->>Client: Set state to "input-required"
        Client->>Server: Send additional information
        Server->>Agent: Forward additional info
        Agent->>API: Call get_exchange_rate tool
        API->>Agent: Return exchange rate data
        Agent->>Server: Process data & return result
        Server->>Client: Respond with currency information
    end

    alt With Streaming
        Note over Client,Server: Real-time status updates
        Server->>Client: "Looking up exchange rates..."
        Server->>Client: "Processing exchange rates..."
        Server->>Client: Final result
    end
```

Loading

## Key Features

* **Multi-turn Conversations**: Agent can request additional information when needed
* **Real-time Streaming**: Provides status updates during processing
* **Push Notifications**: Support for webhook-based notifications
* **Conversational Memory**: Maintains context across interactions
* **Currency Exchange Tool**: Integrates with Frankfurter API for real-time rates

## Prerequisites

* Python 3.13 or higher
* UV
* Access to an LLM and API Key

## Setup & Running

1. Navigate to the samples directory:

   ```
   cd samples/python/agents/langgraph
   ```
2. Create an environment file with your API key:

   ```
   echo "GOOGLE_API_KEY=your_api_key_here" > .env
   ```
3. Run the agent:

   ```
   # Basic run on default port 10000
   uv run .

   # On custom host/port
   uv run . --host 0.0.0.0 --port 8080
   ```
4. In a separate terminal, run an A2A [client](/google/A2A/blob/main/samples/python/hosts/README.md):

   ```
   uv run hosts/cli
   ```

## Technical Implementation

* **LangGraph ReAct Agent**: Uses the ReAct pattern for reasoning and tool usage
* **Streaming Support**: Provides incremental updates during processing
* **Checkpoint Memory**: Maintains conversation state between turns
* **Push Notification System**: Webhook-based updates with JWK authentication
* **A2A Protocol Integration**: Full compliance with A2A specifications

## Limitations

* Only supports text-based input/output (no multi-modal support)
* Uses Frankfurter API which has limited currency options
* Memory is session-based and not persisted between server restarts

## Examples

**Synchronous request**

Request:

```
POST http://localhost:10000
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "id": 11,
  "method": "tasks/send",
  "params": {
    "id": "129",
    "sessionId": "8f01f3d172cd4396a0e535ae8aec6687",
    "acceptedOutputModes": [
      "text"
    ],
    "message": {
      "role": "user",
      "parts": [
        {
          "type": "text",
          "text": "How much is the exchange rate for 1 USD to INR?"
        }
      ]
    }
  }
}
```

Response:

```
{
  "jsonrpc": "2.0",
  "id": 11,
  "result": {
    "id": "129",
    "status": {
      "state": "completed",
      "timestamp": "2025-04-02T16:53:29.301828"
    },
    "artifacts": [
      {
        "parts": [
          {
            "type": "text",
            "text": "The exchange rate for 1 USD to INR is 85.49."
          }
        ],
        "index": 0
      }
    ],
    "history": []
  }
}
```

**Multi-turn example**

Request - Seq 1:

```
POST http://localhost:10000
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "id": 10,
  "method": "tasks/send",
  "params": {
    "id": "130",
    "sessionId": "a9bb617f2cd94bd585da0f88ce2ddba2",
    "acceptedOutputModes": [
      "text"
    ],
    "message": {
      "role": "user",
      "parts": [
        {
          "type": "text",
          "text": "How much is the exchange rate for 1 USD?"
        }
      ]
    }
  }
}
```

Response - Seq 2:

```
{
  "jsonrpc": "2.0",
  "id": 10,
  "result": {
    "id": "130",
    "status": {
      "state": "input-required",
      "message": {
        "role": "agent",
        "parts": [
          {
            "type": "text",
            "text": "Which currency do you want to convert to? Also, do you want the latest exchange rate or a specific date?"
          }
        ]
      },
      "timestamp": "2025-04-02T16:57:02.336787"
    },
    "history": []
  }
}
```

Request - Seq 3:

```
POST http://localhost:10000
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "id": 10,
  "method": "tasks/send",
  "params": {
    "id": "130",
    "sessionId": "a9bb617f2cd94bd585da0f88ce2ddba2",
    "acceptedOutputModes": [
      "text"
    ],
    "message": {
      "role": "user",
      "parts": [
        {
          "type": "text",
          "text": "CAD"
        }
      ]
    }
  }
}
```

Response - Seq 4:

```
{
  "jsonrpc": "2.0",
  "id": 10,
  "result": {
    "id": "130",
    "status": {
      "state": "completed",
      "timestamp": "2025-04-02T16:57:40.033328"
    },
    "artifacts":


# https://github.com/google/A2A/tree/main/samples/js/src/agents/README.md




# https://github.com/google/A2A/tree/main/specification/json

The site's robots.txt disallows autonomous fetching of that page. You might consider using your browser or another tool to view it manually.


# https://github.com/google/A2A/tree/main/demo/README.md

## Demo Web App

This demo application showcases agents talking to other agents over A2A.

[![image](/google/A2A/raw/main/images/a2a_demo_arch.png)](/google/A2A/blob/main/images/a2a_demo_arch.png)

* The frontend is a [mesop](https://github.com/mesop-dev/mesop) web application that renders conversations as content between the end user and the "Host Agent". This app can render text content, thought bubbles, web forms (requests for input from agents), and images. More content types coming soon
* The [Host Agent](/google/A2A/blob/main/samples/python/hosts/multiagent/host_agent.py) is a Google ADK agent which orchestrates user requests to Remote Agents.
* Each [Remote Agent](/google/A2A/blob/main/samples/python/hosts/multiagent/remote_agent_connection.py) is an A2AClient running inside a Google ADK agent. Each remote agent will retrieve the A2AServer's [AgentCard](https://google.github.io/A2A/#documentation?id=agent-card) and then proxy all requests using A2A.

## Features

### Dynamically add agents

Clicking on the robot icon in the web app lets you add new agents. Enter the address of the remote agent's AgentCard and the app will fetch the card and add the remote agent to the local set of known agents.

### Speak with one or more agents

Click on the chat button to start or continue an existing conversation. This conversation will go to the Host Agent which will then delegate the request to one or more remote agents.

If the agent returns complex content - like an image or a web-form - the frontend will render this in the conversation view. The Remote Agent will take care of converting this content between A2A and the web app’s native representation.

### Explore A2A Tasks

Click on the history to see the messages sent between the web app and all of the agents (Host agent and Remote agents).

Click on the task list to see all the A2A task updates from the remote agents.

## Prerequisites

* Python 3.12 or higher
* UV
* Agent servers speaking A2A ([use these samples](/google/A2A/blob/main/samples/python/agents/README.md))

## Running the Examples

1. Navigate to the demo UI directory:

   ```
   cd demo/ui
   ```
2. Create an environment file with your API key:

   ```
   echo "GOOGLE_API_KEY=your_api_key_here" > .env
   ```
3. Run the front end example:

   ```
   uv run main.py
   ```

Note: The application runs on port 12000 by default
