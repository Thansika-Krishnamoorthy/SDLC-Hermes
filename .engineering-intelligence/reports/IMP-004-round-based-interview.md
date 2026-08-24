# IMP-004: Round-based interview to cut per-question wait

## Classification
- Type: update
- Risk: low
- Scope: interview prompt, chat UI choice parser, OpenRouter request options
- Depth: Standard

## Analysis
- One LLM round-trip per question causes a 4–5s pause after every click.
- Batch 3–4 questions per assistant turn; the UI collects all answers, then sends one message.
- Single-question Approve/Modify/Add More after a BRD stays as immediate actions.
- Disable extra reasoning tokens on OpenRouter when supported, to shorten time-to-first-token.

## Validation
- Prompt/guidelines mention rounds, not one-question-at-a-time
- pytest for skill discovery and system prompt
