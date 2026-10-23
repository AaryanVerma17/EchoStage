import pytest
from app.config import get_settings
from app.decision_policy import decide
from app.schemas import SceneState, StageAction
from app.decider_adapter import DeciderUnavailable

class FakeAdapter:
    def __init__(self, action=StageAction.CONTRAST, confidence=0.9, error=None):
        self.action, self.confidence, self.error = action, confidence, error
    async def choose(self, state):
        if self.error:
            raise self.error
        return self.action, self.confidence, 12.3

@pytest.mark.asyncio
async def test_executes_valid_decision(monkeypatch, tmp_path):
    monkeypatch.setenv("EVENT_LOG_PATH", str(tmp_path / "events.jsonl"))
    get_settings.cache_clear()
    result = await decide(SceneState(), FakeAdapter())
    assert result.executed_action == StageAction.CONTRAST
    assert result.source == "strands-decider-2b"
    get_settings.cache_clear()

@pytest.mark.asyncio
async def test_low_confidence_falls_back(monkeypatch, tmp_path):
    monkeypatch.setenv("EVENT_LOG_PATH", str(tmp_path / "events.jsonl"))
    get_settings.cache_clear()
    result = await decide(SceneState(), FakeAdapter(confidence=0.2))
    assert result.executed_action == StageAction.HOLD
    assert result.fallback_reason == "low_confidence"
    get_settings.cache_clear()

@pytest.mark.asyncio
async def test_unavailable_falls_back(monkeypatch, tmp_path):
    monkeypatch.setenv("EVENT_LOG_PATH", str(tmp_path / "events.jsonl"))
    get_settings.cache_clear()
    result = await decide(SceneState(), FakeAdapter(error=DeciderUnavailable("offline")))
    assert result.executed_action == StageAction.HOLD
    assert result.fallback_reason == "decider_unavailable"
    get_settings.cache_clear()
