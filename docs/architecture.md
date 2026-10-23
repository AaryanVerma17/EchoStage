# Architecture and DevOps Notes

## Trust boundaries
- Browser input is validated by Pydantic.
- Decider output is untrusted until parsed into `StageAction`.
- The executor maps enums to hard-coded state transitions; it never executes model-generated code.
- AWS credentials remain server-side.
- Do not log secrets or personal audience data.

## Deployment topology
1. React frontend as static site.
2. FastAPI API with AWS SDK and policy code.
3. Decider host/container with enough RAM/GPU, reachable only by backend.
4. Amazon Bedrock through AWS SDK and least-privilege IAM.

## Production hardening still needed
- Add authentication and rate limiting before public API exposure.
- Restrict CORS to deployed frontend origin.
- Protect Decider behind private networking/VPN/authenticated gateway.
- Use HTTPS and an IAM role on AWS rather than long-lived keys.
- Add monitoring, log retention, load tests and concurrency checks.
- Decider server defaults to localhost and has no authentication; do not expose it directly.
