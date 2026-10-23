from app.schemas import SceneState, StageAction

def fixed_schedule(state: SceneState):
    sequence = [StageAction.INTENSIFY, StageAction.HOLD, StageAction.CONTRAST, StageAction.SOFTEN]
    return sequence[int(state.narrative_progress * 100) % len(sequence)]

def rule_based(state: SceneState):
    if state.stage_intensity > 0.82:
        return StageAction.SOFTEN
    if state.simulated_engagement < 0.42:
        return StageAction.CONTRAST
    if state.pacing_pressure > 0.72 and state.transition_allowed and state.seconds_since_last_transition >= 12 and state.narrative_progress < 0.95:
        return StageAction.TRANSITION
    if state.stage_intensity < 0.42:
        return StageAction.INTENSIFY
    return StageAction.HOLD
