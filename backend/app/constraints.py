from .schemas import SceneState, StageAction

MIN_SECONDS_BETWEEN_TRANSITIONS = 12

def validate_action(action: StageAction, state: SceneState):
    if action == StageAction.TRANSITION:
        if not state.transition_allowed:
            return False, "transition_not_allowed_by_scene"
        if state.seconds_since_last_transition < MIN_SECONDS_BETWEEN_TRANSITIONS:
            return False, "minimum_transition_interval_not_met"
        if state.narrative_progress >= 0.98:
            return False, "scene_already_at_end"
    if action == StageAction.INTENSIFY and state.stage_intensity >= 0.96:
        return False, "intensity_already_at_ceiling"
    if action == StageAction.SOFTEN and state.stage_intensity <= 0.16:
        return False, "intensity_already_at_floor"
    return True, None
