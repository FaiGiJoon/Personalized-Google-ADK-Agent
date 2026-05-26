# Agents CLI Workflow

This repository utilizes the `agents-cli` for agent lifecycle management.

## Setup
Install `uv` and run `uvx google-agents-cli setup` to initialize the environment.

## Scaffolding
Use `agents-cli create <agent-name> --prototype --yes` to scaffold new agents.

## Development
Edit `core/agent.py` using ADK design patterns. Use `agents-cli run "<prompt>"` for local testing.

## Evaluation
Run evaluations using `agents-cli eval run`. Ensure `tests/eval/evalsets/` and `tests/eval/eval_config.json` are properly configured.

## Deployment
Deploy to Cloud Run using `agents-cli deploy`. Ensure the deployment target is enhanced with `agents-cli scaffold enhance --deployment-target cloud_run`.

## Observability
Detailed observability can be set up via `agents-cli` which provisions the necessary Google Cloud resources (GCS, BigQuery, Service Accounts).

---
For a detailed guide on using the `agents-cli` workflow, see [docs/AGENTS_CLI_QUICKSTART.md](docs/AGENTS_CLI_QUICKSTART.md).
