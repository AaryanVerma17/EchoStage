from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from .config import get_settings
from .schemas import DecisionRequest, DecisionResponse, SceneBriefRequest, SceneBriefResponse, SceneState
from .decider_adapter import DeciderAdapter
from .decision_policy import decide
from .state import INITIAL_STATE
from .logger import read_events
from .bedrock_service import generate_scene_brief, BedrockUnavailable

settings = get_settings()
app = FastAPI(title="EchoStage API", description="Adaptive virtual stage director using Strands Decider 2B and Amazon Bedrock.", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=settings.allowed_origins, allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["*"])

@app.get("/health")
async def health():
    decider = await DeciderAdapter().health()
    return {"status": "ok", "service": "echostage-api", "decider": decider}

@app.get("/api/scenarios")
async def scenarios():
    monologue = SceneState(scene_id="monologue", scene_phase="opening", narrative_progress=0.25, stage_intensity=0.48, simulated_engagement=0.68, pacing_pressure=0.35, current_lighting="soft_teal")
    return [
        {"id": "suspense", "name": "Suspense", "description": "Slow-burn scene with protected climax.", "initial_state": INITIAL_STATE.model_dump(mode="json")},
        {"id": "monologue", "name": "Reflective Monologue", "description": "Alternating intensity and reflection.", "initial_state": monologue.model_dump(mode="json")}
    ]

@app.post("/api/decide", response_model=DecisionResponse)
async def make_decision(request: DecisionRequest):
    return await decide(request.state)

@app.post("/api/reset")
async def reset():
    return {"state": INITIAL_STATE.model_dump(mode="json")}

@app.get("/api/events")
async def events(limit: int = Query(default=50, ge=1, le=500)):
    return {"events": read_events(limit)}

@app.post("/api/scene-brief", response_model=SceneBriefResponse)
def scene_brief(request: SceneBriefRequest):
    try:
        brief, model_id = generate_scene_brief(request.theme, request.style)
        return SceneBriefResponse(brief=brief, model_id=model_id)
    except BedrockUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
