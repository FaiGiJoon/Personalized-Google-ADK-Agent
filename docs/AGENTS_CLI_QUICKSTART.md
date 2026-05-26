# Agents CLI Quickstart

This guide provides instructions on how to use the `agents-cli` tool to scaffold, build, evaluate, and deploy agents using the Google ADK.

## Setup

1. **Install `uv`**: `uv` is a fast Python package installer. For instructions, see the [uv installation guide](https://github.com/astral-sh/uv).
2. **Run Setup**: Run the Agents CLI setup command using `uvx` (included with `uv`). This is the only Agents CLI command you execute directly:
   ```bash
   uvx google-agents-cli setup
   ```
3. **Open AI Development Tool**: Open your AI development tool, such as Antigravity.

## Scaffold project

Instruct your AI development tool with the following prompt:
> Use agents-cli to build an agent that compresses verbose text into concise, caveman-style summaries.

Your AI development tool activates the `google-agents-cli-workflow` and `google-agents-cli-scaffold` skills. It performs the following actions:
- Asks clarifying questions, such as its deployment target and safety constraints.
- Writes a `DESIGN_SPEC.md` file capturing the agent's purpose.
- Scaffolds the project:
  ```bash
  agents-cli create caveman-agent --prototype --yes
  cd caveman-agent && agents-cli install
  ```
This process creates a project with boilerplate agent code, tests, and evaluation sets.

## Build agent

Your AI development tool edits `core/agent.py`, replacing the default agent with the caveman compressor logic. It utilizes the `google-agents-cli-adk-code` skill for ADK design patterns.

The resulting agent definition resembles the following:

```python
root_agent = Agent(
   name="caveman_agent",
   model=Gemini(model="gemini-flash-latest"),
   instruction="""You are a text compressor. Convert verbose input text into short, simple summaries with a caveman-like tone. Rules:
   - Omit articles, filler words, and politeness.
   - Use short sentences and simple words.
   - Preserve technical terms.
   - The tone should be abrupt and funny, but the core meaning must be retained.

   Example input:  "I would like to deploy the application to production environment."
   Example output: "Me deploy. Production. Now."
   """,
)
```

Your AI development tool then performs a basic functionality test:
```bash
agents-cli run "Please help me understand the deployment options available for my project"
```
**Expected output**: "Deploy options: Agent Runtime, Cloud Run, GKE. Pick one. Ship."

## Evaluate agent

To evaluate the agent, instruct your AI development tool with the following prompt:
> Write evaluations for the caveman agent and run them.

Your AI development tool activates the `google-agents-cli-eval` skill and performs these tasks:
- Creates `tests/eval/evalsets/caveman.evalset.json` with test cases covering compression quality, technical term preservation, and tone.
- Configures LLM-as-judge criteria in `tests/eval/eval_config.json`.
- Runs the evaluation:
  ```bash
  agents-cli eval run
  ```
If test cases fail, provide corrective feedback. For example:
> The response to the greeting test is too polite. Make it more brusque.

Your AI development tool adjusts the agent's instructions, re-runs `agents-cli eval run`, and iterates until the desired quality is achieved.

## Deploy agent

To deploy and run the agent on Google Cloud, instruct your AI development tool:
> Deploy this agent to Cloud Run.

Your AI development tool activates the `google-agents-cli-deploy` skill and:
- Adds the necessary deployment infrastructure configuration:
  ```bash
  agents-cli scaffold enhance --deployment-target cloud_run
  ```
- Deploys the agent:
  ```bash
  agents-cli deploy
  ```
The agent is now deployed on Cloud Run. The output includes the service URL.

## Observe agent

Cloud Trace is enabled by default. To view traces, open the Cloud Trace explorer in the Google Cloud console.

To enable more detailed observability, instruct your AI development tool:
> Set up observability infrastructure for my agent.

Your AI development tool provisions a service account, a Cloud Storage bucket, and a BigQuery dataset, and updates the deployed service.

## Summary of actions

| User instruction | Your AI development tool actions |
| :--- | :--- |
| "Build a caveman compressor agent" | Scaffolds project, writes agent code, tests locally. |
| "Write evals and run them" | Creates evalset, configures LLM-as-judge, runs `agents-cli eval run`. |
| "Deploy this to Cloud Run" | Adds deployment target configuration, deploys to Cloud Run. |
| "Set up observability" | Provisions service account, Cloud Storage bucket, and BigQuery dataset. |

Agents CLI skills provide the necessary context for your AI development tool to use appropriate ADK patterns, structure evaluations, and configure deployments.

---
**Source**: [Google Cloud Documentation](https://docs.cloud.google.com/gemini-enterprise-agent-platform/agents/quickstart-adk)
