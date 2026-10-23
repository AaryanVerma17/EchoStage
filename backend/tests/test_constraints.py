from app.constraints import validate_action
from app.schemas import SceneState, StageAction

def test_transition_blocked_when_not_allowed():
    valid, reason = validate_action(StageAction.TRANSITION, SceneState(transition_allowed=False, seconds_since_last_transition=30))
    assert not valid and reason == "transition_not_allowed_by_scene"

def test_transition_blocked_too_soon():
    valid, reason = validate_action(StageAction.TRANSITION, SceneState(seconds_since_last_transition=2))
    assert not valid and reason == "minimum_transition_interval_not_met"

def test_hold_valid():
    assert validate_action(StageAction.HOLD, SceneState()) == (True, None)
