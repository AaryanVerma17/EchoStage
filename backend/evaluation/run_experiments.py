import json
from pathlib import Path
from app.schemas import SceneState
from app.state import apply_action
from .baselines import fixed_schedule, rule_based

def run_controller(controller, initial, signals, name):
    state, actions, violations = initial, [], 0
    for signal in signals:
        state = state.model_copy(update=signal)
        action = controller(state)
        if action.value == "TRANSITION" and (not state.transition_allowed or state.seconds_since_last_transition < 12):
            violations += 1
            from app.schemas import StageAction
            action = StageAction.HOLD
        actions.append(action.value)
        state = apply_action(state, action)
    return {
        "controller": name, "steps": len(actions), "actions": actions,
        "transition_constraint_violations": violations,
        "action_repetition_rate": sum(actions[i] == actions[i-1] for i in range(1, len(actions))) / max(1, len(actions)-1)
    }

def main():
    signals = [
        {"simulated_engagement": .70, "pacing_pressure": .30},
        {"simulated_engagement": .60, "pacing_pressure": .45},
        {"simulated_engagement": .40, "pacing_pressure": .68},
        {"simulated_engagement": .35, "pacing_pressure": .78},
        {"simulated_engagement": .52, "pacing_pressure": .55},
        {"simulated_engagement": .72, "pacing_pressure": .35}
    ]
    initial = SceneState()
    results = [
        run_controller(fixed_schedule, initial, signals, "fixed_schedule"),
        run_controller(rule_based, initial, signals, "rule_based")
    ]
    out = Path("evaluation-results.json")
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))
    print(f"Saved baseline results to {out.resolve()}")
    print("Baseline outputs only; these are not measured Decider results.")

if __name__ == "__main__":
    main()
