import pytest
from app.config import get_settings
from app.decider_adapter import DeciderAdapter
from app.schemas import SceneState, StageAction

@pytest.mark.asyncio
async def test_mock_mode_is_explicit_and_deterministic(monkeypatch):
    monkeypatch.setenv("DECIDER_MODE", "mock")
    get_settings.cache_clear()
    adapter = DeciderAdapter()
    state = SceneState(stage_intensity=0.9)
    action, confidence, latency = await adapter.choose(state)
    assert adapter.source == "mock-policy"
    assert action == StageAction.SOFTEN
    assert confidence == 0.78
    assert latency >= 0
    get_settings.cache_clear()
