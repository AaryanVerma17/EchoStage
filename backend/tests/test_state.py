from app.schemas import SceneState, StageAction
from app.state import apply_action

def test_intensify_increases_intensity():
    state = SceneState(stage_intensity=0.5)
    assert apply_action(state, StageAction.INTENSIFY).stage_intensity > 0.5

def test_transition_advances_phase():
    state = SceneState(scene_phase="rising_tension", narrative_progress=0.4, seconds_since_last_transition=30)
    after = apply_action(state, StageAction.TRANSITION)
    assert after.scene_phase == "climax"
    assert after.seconds_since_last_transition == 0
