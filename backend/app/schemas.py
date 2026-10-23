from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

class StageAction(str, Enum):
    HOLD = "HOLD"
    INTENSIFY = "INTENSIFY"
    CONTRAST = "CONTRAST"
    SOFTEN = "SOFTEN"
    TRANSITION = "TRANSITION"

class SceneState(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    scene_id: str = "suspense"
    scene_phase: str = "rising_tension"
    narrative_progress: float = Field(default=0.42, ge=0, le=1)
    stage_intensity: float = Field(default=0.58, ge=0, le=1)
    simulated_engagement: float = Field(default=0.64, ge=0, le=1)
    pacing_pressure: float = Field(default=0.48, ge=0, le=1)
    current_lighting: str = "deep_blue"
    last_action: StageAction = StageAction.HOLD
    seconds_since_last_transition: int = Field(default=30, ge=0, le=3600)
    transition_allowed: bool = True

class DecisionRequest(BaseModel):
    state: SceneState

class DecisionResponse(BaseModel):
    requested_action: str
    executed_action: StageAction
    confidence: float | None = None
    confidence_threshold: float
    source: str
    fallback_reason: str | None = None
    constraint_note: str | None = None
    latency_ms: float
    state_after: SceneState
    event_id: str

class SceneBriefRequest(BaseModel):
    theme: str = Field(min_length=3, max_length=500)
    style: str = Field(default="cinematic theatre", max_length=100)

class SceneBriefResponse(BaseModel):
    brief: str
    model_id: str
