# AWS deployment guide (hackathon-sized)

## Recommended deadline-friendly topology

- **Frontend:** deploy `frontend/` to AWS Amplify Hosting or another static host.
- **API + Decider:** keep the FastAPI API and Strands Decider on the same private EC2 host for the first live demo. The Decider endpoint binds to localhost by default and has no authentication; do not expose port 8099 to the internet.
- **Generative briefs:** call Amazon Bedrock from FastAPI using the instance's IAM role.
- **Ingress:** expose only HTTPS API traffic through a reverse proxy or load balancer. Restrict CORS to the frontend domain.

The live 2B model can require substantial RAM and first-run downloads. Select an instance only after measuring model memory on the target device; do not assume a small serverless container is sufficient. A CPU-only instance may be slow. Stop GPU/large-memory instances when not being used to control costs.

## IAM

1. Create an EC2 instance role with `bedrock:InvokeModel` limited to the approved model ARN/resource scope for the selected region.
2. Attach the role to the instance; do not put access keys in source control or bake them into an image.
3. Verify the selected model ID and region in the Bedrock console. Model IDs and availability vary by region and account.
4. The policy template at `infra/bedrock-invoke-policy.json` deliberately contains a placeholder resource. Replace it with the correct resource scope before use; do not attach it unchanged.

## Runtime environment

Configure the backend environment:

```dotenv
APP_ENV=production
DECIDER_URL=http://127.0.0.1:8099
DECIDER_MODEL=StrandsAgents/strands-decider-2B-qwen3.5-v1-2610
DECIDER_MODE=live
CONFIDENCE_THRESHOLD=0.60
CORS_ORIGINS=https://YOUR-FRONTEND-DOMAIN
AWS_REGION=YOUR_BEDROCK_REGION
BEDROCK_MODEL_ID=YOUR_AVAILABLE_BEDROCK_MODEL_ID
EVENT_LOG_PATH=/var/lib/echostage/events.jsonl
```

Run Decider as a separate supervised service bound to loopback. Run FastAPI behind HTTPS ingress. Create `/var/lib/echostage` with ownership for the service user. Configure log rotation/retention and restart policies.

## Before making it public

- Add authentication and rate limiting to the API.
- Restrict CORS to the actual frontend origin.
- Keep Decider bound to loopback/private networking.
- Use HTTPS and an IAM role/temporary credentials.
- Set request limits, timeouts and log retention.
- Add monitoring and an operational cost alarm.
- Never log AWS credentials or personal audience data. Current engagement signals are synthetic.

## CI

GitHub Actions runs Python tests and a Vite production build on pushes and pull requests. Configure deployment secrets/roles only after CI is green; prefer GitHub OIDC to long-lived AWS keys for automated deployment.
