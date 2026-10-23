import boto3
from botocore.exceptions import BotoCoreError, ClientError
from .config import get_settings

class BedrockUnavailable(RuntimeError):
    pass

def generate_scene_brief(theme: str, style: str):
    settings = get_settings()
    try:
        client = boto3.client("bedrock-runtime", region_name=settings.aws_region)
        prompt = (
            "Create a concise creative direction brief for a simulated virtual theatre scene. "
            "Do not claim to observe a real audience. Return mood, palette, pacing arc and stage "
            "constraints in under 140 words. Theme: " + theme + "\nStyle: " + style
        )
        response = client.converse(
            modelId=settings.bedrock_model_id,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": 300, "temperature": 0.6}
        )
        parts = response["output"]["message"]["content"]
        brief = "\n".join(x.get("text", "") for x in parts if x.get("text")).strip()
        if not brief:
            raise BedrockUnavailable("Bedrock returned an empty brief.")
        return brief, settings.bedrock_model_id
    except (BotoCoreError, ClientError, KeyError) as exc:
        raise BedrockUnavailable(
            "Bedrock call failed. Check AWS credentials, region, model ID and model access."
        ) from exc
