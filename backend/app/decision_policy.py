import uuid
from .config import get_settings
from .constraints import validate_action
from .decider_adapter import DeciderAdapter, DeciderUnavailable
from .schemas import DecisionResponse, SceneState, StageAction
from .state import apply_action
from .logger import append_event

async def decide(state: SceneState, adapter=None):
    settings = get_settings()
    adapter = adapter or DeciderAdapter()
    event_id = str(uuid.uuid4())
    requested, confidence, latency = StageAction.HOLD.value, None, 0.0
    source, fallback_reason, constraint_note = getattr(adapter, "source", "strands-decider-2b"), None, None
    action = StageAction.HOLD
    try:
        action, confidence, latency = await adapter.choose(state)
        source = getattr(adapter, "source", source)
        requested = action.value
        if confidence is not None and confidence < settings.confidence_threshold:
            action, source, fallback_reason = StageAction.HOLD, "fallback", "low_confidence"
        else:
            valid, reason = validate_action(action, state)
            if not valid:
                action, source, fallback_reason = StageAction.HOLD, "fallback", reason
                constraint_note = reason
    except DeciderUnavailable as exc:
        source, fallback_reason, constraint_note = "fallback", "decider_unavailable", str(exc)[:300]
        action = StageAction.HOLD

    new_state = apply_action(state, action)
    response = DecisionResponse(
        requested_action=requested, executed_action=action, confidence=confidence,
        confidence_threshold=settings.confidence_threshold, source=source,
        fallback_reason=fallback_reason, constraint_note=constraint_note,
        latency_ms=round(latency, 2), state_after=new_state, event_id=event_id
    )
    append_event({
        "event_id": event_id, "state_before": state.model_dump(mode="json"),
        "requested_action": requested, "executed_action": action.value,
        "confidence": confidence, "source": source, "fallback_reason": fallback_reason,
        "latency_ms": response.latency_ms, "state_after": new_state.model_dump(mode="json")
    })
    return response
