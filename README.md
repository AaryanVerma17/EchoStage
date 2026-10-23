# EchoStage

Adaptive virtual stage director using Strands Decider 2B for bounded stage-cue decisions and Amazon Bedrock for generative scene briefs.

## MVP
- React/Vite cinematic stage UI and live decision inspector
- FastAPI API and real Strands Decider HTTP adapter (`POST /v1/systemone`)
- Five enumerated actions, confidence handling, deterministic transition constraints, `HOLD` fallback
- Amazon Bedrock Converse API scene-brief generation
- JSONL event log, deterministic baselines, tests, CI and reusable policy pattern

Audience engagement is simulated, not inferred from real people.

## Prerequisites
Python 3.11+, Node 20+, npm, Git. For live decisions, the Decider model downloads several GB of weights and requires sufficient RAM/CPU or supported GPU. Bedrock needs valid AWS credentials, model access, and a configured region.

## Run locally (Windows)

Run the React and API services in PowerShell. For the live Decider model, use WSL2 (recommended on Windows) or a supported Linux/macOS environment; see the official device-specific setup because model dependencies and memory requirements vary. The live 2B model downloads multi-gigabyte model assets and CPU inference can be slow. The Decider server binds to localhost and has no authentication, so keep it private.

### 1. Start the Decider server (live hackathon mode)

In WSL2/Linux, follow the current official setup guide at https://github.com/strands-labs/strands-decider/blob/main/docs/inference.md. The current upstream example uses:

```bash
git clone https://github.com/strands-labs/strands-decider
cd strands-decider
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
strands-decider serve StrandsAgents/strands-decider-2B-qwen3.5-v1-2610 --device cpu --port 8099
```

Use `--device cuda` only on a supported Linux machine with the required NVIDIA/CUDA dependencies; use the upstream guide for Apple Silicon. For a Windows PowerShell client connecting to a server in WSL2, `127.0.0.1:8099` is normally reachable while the WSL session remains active.

### 2. Start the backend in a second PowerShell terminal

```powershell
cd echostageackend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --port 8000
```

### 3. Start the frontend in a third terminal

```powershell
cd echostagerontend
npm install
Copy-Item .env.example .env
npm run dev
```

Open http://localhost:5173. If PowerShell blocks activation, use `Set-ExecutionPolicy -Scope Process Bypass` in that terminal or activate using your preferred Python environment manager.

### Fast UI development without downloading the model

Set `DECIDER_MODE=mock` in `backend/.env` and restart the API. The frontend remains interactive and clearly labels this as **MOCK POLICY**. This mode is only for UI development; it does not count as a live Strands Decider demo. Set `DECIDER_MODE=live` before final evaluation/submission.

## Bedrock setup
Configure AWS credentials with an AWS profile, environment or IAM role. Never commit credentials. Set `AWS_REGION` and `BEDROCK_MODEL_ID` in `backend/.env`, restart the API, then use **Generate with Bedrock**. The default model ID is an example; verify model availability and access in your account/region.

## API
- `GET /health`
- `GET /api/scenarios`
- `POST /api/decide` with `{"state": { ...SceneState fields... }}`
- `POST /api/scene-brief` with `{"theme":"...","style":"cinematic theatre"}`
- `GET /api/events?limit=50`
- `POST /api/reset`

## Evaluation and tests
```powershell
cd backend
pytest -q
python -m evaluation.run_experiments
```
The included experiment runner evaluates deterministic baselines only. It does not claim to measure Decider performance. For fair evaluation, replay identical input signals against fixed, rule-based and live adaptive controllers and report actual results.

## Deployment
See [`docs/aws-deployment.md`](docs/aws-deployment.md) for an AWS topology, IAM guidance, production environment variables, security checklist and cost notes. Host Decider on a machine with adequate memory; do not assume a small serverless function can host model weights. The Decider's default local server has no authentication: keep it on a private network and do not expose it publicly.

## Hackathon submission checklist
This repo is a working source scaffold, not proof of an eligible submission until live integrations are verified. Run a real Decider decision, demonstrate Bedrock, publish the repo with the MIT license, publish the Builder Center article, and publish a public video under three minutes. Use `#strands-decider-2b` and `#policy`.

## Official references
- https://github.com/strands-labs/strands-decider
- https://github.com/strands-labs/strands-decider/blob/main/docs/inference.md
- https://builder.aws.com/build/hackathons/4f50957c-1d08-37ab-b11c-97516b9adeb4/agent-experience-hackathon?tab=rules
