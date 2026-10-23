import time
import httpx
from .config import get_settings
from .schemas import SceneState, StageAction

class DeciderUnavailable(RuntimeError):
    pass

class DeciderAdapter:
    # Thin adapter for the official Strands Decider HTTP API.
    def __init__(self):
        self.settings = get_settings()
        self.source = "strands-decider-2b"

    async def health(self):
        if self.settings.decider_mode.lower() == "mock":
            return {"available": True, "mode": "mock", "details": {"note": "Deterministic development policy; not a live model."}}
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                r = await client.get(f"{self.settings.decider_url.rstrip('/')}/health")
                r.raise_for_status()
                return {"available": True, "details": r.json()}
        except Exception as exc:
            return {"available": False, "error": str(exc)}

    async def choose(self, state: SceneState):
        if self.settings.decider_mode.lower() == "mock":
            # Explicit local-demo mode. It is never presented as a live model decision.
            self.source = "mock-policy"
            started = time.perf_counter()
            if state.stage_intensity > 0.82:
                action = StageAction.SOFTEN
            elif state.simulated_engagement < 0.40:
                action = StageAction.CONTRAST
            elif (state.pacing_pressure > 0.72 and state.transition_allowed
                  and state.seconds_since_last_transition >= 12 and state.narrative_progress < 0.95):
                action = StageAction.TRANSITION
            elif state.stage_intensity < 0.42:
                action = StageAction.INTENSIFY
            else:
                action = StageAction.HOLD
            return action, 0.78, (time.perf_counter() - started) * 1000
        self.source = "strands-decider-2b"
        prompt_state = (
            "EchoStage virtual performance controller. Choose the next stage action. "
            "Use narrative coherence, intensity, engagement, pacing, scene phase and prior action. "
            "Audience engagement is simulated, not a real measurement. State: "
            + state.model_dump_json()
        )
        body = {
            "state": prompt_state,
            "model": self.settings.decider_model,
            "questions": {
                "stage_action": {
                    "type": "choice",
                    "instructions": (
                        "Choose the single best next stage cue for a coherent performance. "
                        "HOLD preserves state; INTENSIFY builds dramatic intensity; CONTRAST changes "
                        "visual mood; SOFTEN reduces sensory intensity; TRANSITION advances the scene."
                    ),
                    "criteria": {
                        "HOLD": "Keep the current state when a change is unnecessary or risky.",
                        "INTENSIFY": "Build intensity when useful and safe.",
                        "CONTRAST": "Change visual mood to create variety or breathing room.",
                        "SOFTEN": "Reduce intensity when the scene is overloaded.",
                        "TRANSITION": "Advance the narrative phase when pacing and constraints allow."
                    }
                }
            }
        }
        started = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds) as client:
                r = await client.post(f"{self.settings.decider_url.rstrip('/')}/v1/systemone", json=body)
                r.raise_for_status()
                payload = r.json()
        except Exception as exc:
            raise DeciderUnavailable(f"Decider request failed: {exc}") from exc
        latency = (time.perf_counter() - started) * 1000
        try:
            answer = payload["answers"]["stage_action"]
            raw = answer.get("choice")
            confidence = answer.get("confidence")
            distribution = answer.get("choices") or answer.get("distribution") or answer.get("probabilities")
            if isinstance(raw, dict):
                distribution = distribution or raw.get("distribution") or raw.get("probabilities")
                confidence = confidence if confidence is not None else raw.get("confidence")
                raw = raw.get("option") or raw.get("label") or raw.get("answer")
            if raw is None:
                raw = answer.get("answer") or answer.get("value") or answer.get("selected")
            if raw is None and isinstance(distribution, dict) and distribution:
                raw = max(distribution, key=distribution.get)
            action = StageAction(str(raw).upper())
            if confidence is None and isinstance(distribution, dict) and distribution:
                top_probability = max(float(value) for value in distribution.values())
                option_count = len(distribution)
                # Decider's documented choice confidence rescales the top probability
                # so a uniform distribution is 0 and a certain answer is 1.
                confidence = ((top_probability - 1 / option_count) / (1 - 1 / option_count)) if option_count > 1 else 1.0
            if confidence is not None:
                confidence = float(confidence)
                if not 0 <= confidence <= 1:
                    confidence = None
            return action, confidence, latency
        except Exception as exc:
            raise DeciderUnavailable(f"Unrecognized Decider response schema: {payload}") from exc
