# Reusable Pattern: Context-Aware Creative Action Policy

**Hackathon pattern:** `#policy`

## Typed question
- Type: `choice`
- Prompt: choose the single best next stage cue for a coherent performance.
- Options: `HOLD`, `INTENSIFY`, `CONTRAST`, `SOFTEN`, `TRANSITION`.

## State
Scene phase, narrative progress, stage intensity, simulated engagement, pacing pressure, lighting, previous action, seconds since transition, and whether transition is allowed.

## Wiring
1. Serialize current state.
2. Submit state and typed choice question to Decider's `/v1/systemone`.
3. Parse selected action and confidence.
4. Use `HOLD` if model is unavailable, output is malformed, or confidence is below threshold.
5. Validate transition and intensity constraints deterministically.
6. Execute only an enumerated action; never execute generated code.
7. Log requested/executed action, confidence, latency and fallback reason.

## Reuse
Replace the enum, state schema, criteria and validator with your domain's bounded actions. Keep adapter, confidence handling, validation and logging separate from the domain executor.

Confidence is not a guarantee of correctness. The threshold must be evaluated for the task. Audience signals in EchoStage are synthetic.
