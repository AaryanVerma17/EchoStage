from .schemas import SceneState, StageAction

INITIAL_STATE = SceneState()

def apply_action(state: SceneState, action: StageAction) -> SceneState:
    # Pure transition function. Never execute arbitrary model-provided code.
    new = state.model_copy(deep=True)
    new.last_action = action
    if action == StageAction.INTENSIFY:
        new.stage_intensity = min(1.0, new.stage_intensity + 0.16)
        new.current_lighting = "electric_violet"
    elif action == StageAction.CONTRAST:
        new.current_lighting = "amber_contrast" if new.current_lighting != "amber_contrast" else "deep_blue"
        new.stage_intensity = max(0.25, min(0.9, new.stage_intensity))
    elif action == StageAction.SOFTEN:
        new.stage_intensity = max(0.15, new.stage_intensity - 0.18)
        new.current_lighting = "soft_teal"
    elif action == StageAction.TRANSITION:
        phases = ["opening", "rising_tension", "climax", "resolution"]
        index = phases.index(new.scene_phase) if new.scene_phase in phases else 0
        new.scene_phase = phases[min(index + 1, len(phases) - 1)]
        new.narrative_progress = min(1.0, new.narrative_progress + 0.2)
        new.current_lighting = "golden_resolution" if new.scene_phase == "resolution" else "electric_violet"
    new.seconds_since_last_transition = 0 if action == StageAction.TRANSITION else new.seconds_since_last_transition + 1
    return new
