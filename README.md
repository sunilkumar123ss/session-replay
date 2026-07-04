# Voice Session Event Replayer

**Demo/starter · Python standard library only.**

Validate a voice-session lifecycle and produce an auditable transition log.

All bundled fixtures are synthetic and contain no customer data or secrets.

## Run

Use Python 3.9 or later (validated with Python 3.9.6). No installation or network access is needed. From this project directory:

```sh
python3 main.py
python3 main.py --input fixtures/demo.json
python3 -m unittest -v
```

The default CLI executes a deterministic working demo. Invalid input exits with a readable error and nonzero status.

## Behavior

Input is an ordered JSON event list with unique `id`, `type`, `at_ms` and optional transcript `text`. Events cover connect, listening, transcript, thinking, TTS, barge-in and close. The output includes transitions, final state, transcripts, utterance and barge-in counts, and closed-session duration.

## Limits and optional provider boundary

This is synthetic event replay, not a real call. No ASR, LLM, TTS, microphone or persistence layer is executed. An open trace reports `complete=false` and null duration. Timestamps are assumed to share one clock.

Real adapters could emit the normalized events. This offline validator rejects duplicate IDs, unordered times and illegal transitions.

## Tests

`test_main.py` checks fixed expected results, edge cases and invalid inputs with `unittest`. These tests validate the local implementation, not real-world speech accuracy or production readiness. Run `python3 verify.py` to repeat this repository’s checks.

## Scope

This is an educational implementation with synthetic fixtures. Run the tests and inspect the documented limits before adapting it.

## Repository checks

```sh
python3 verify.py
```

This runs the isolated test suite, synthetic example, and CLI help. The included GitHub Actions workflow repeats these checks when the repository is published. No hosted CI result is claimed by the local verification report.
