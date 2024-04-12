"""Validate and replay synthetic voice-session lifecycle events offline."""
import argparse
import json
import math
from pathlib import Path

def replay(events):
    if not isinstance(events, list):
        raise ValueError('Events must be a list')
    state = 'new'
    previous = -1
    ids = set()
    transitions = []
    transcripts = []
    started = None
    closed = None
    allowed = {'new': {'connect': 'idle'}, 'idle': {'speech_start': 'listening', 'close': 'closed'}, 'listening': {'transcript': 'listening', 'speech_end': 'thinking', 'close': 'closed'}, 'thinking': {'tts_start': 'speaking', 'close': 'closed'}, 'speaking': {'tts_end': 'idle', 'barge_in': 'listening', 'close': 'closed'}, 'closed': {}}
    counts = {'barge_ins': 0, 'completed_utterances': 0}
    for event in events:
        if not isinstance(event, dict):
            raise ValueError('Event must be object')
        (eid, kind, now) = (event.get('id'), event.get('type'), event.get('at_ms'))
        if not isinstance(eid, str) or not eid or eid in ids:
            raise ValueError('Event IDs must be unique nonempty strings')
        if not isinstance(kind, str) or kind not in allowed[state]:
            raise ValueError('Illegal event for state ' + state)
        if isinstance(now, bool) or not isinstance(now, (int, float)) or (not math.isfinite(now)) or (now < 0) or (now < previous):
            raise ValueError('Timestamps must be finite, nonnegative and ordered')
        if kind == 'transcript' and (not isinstance(event.get('text'), str)):
            raise ValueError('Transcript needs text')
        previous = now
        ids.add(eid)
        before = state
        state = allowed[state][kind]
        transitions.append({'id': eid, 'at_ms': now, 'event': kind, 'from': before, 'to': state})
        if kind == 'connect':
            started = now
        elif kind == 'close':
            closed = now
        elif kind == 'transcript':
            transcripts.append(event['text'])
        elif kind == 'barge_in':
            counts['barge_ins'] += 1
        elif kind == 'tts_end':
            counts['completed_utterances'] += 1
    return {'state': state, 'complete': state == 'closed', 'duration_ms': closed - started if closed is not None else None, **counts, 'transcripts': transcripts, 'transitions': transitions}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, help='JSON event list with id,type,at_ms and optionaltext')
    args = parser.parse_args()
    try:
        events = json.loads(args.input.read_text()) if args.input else [{'id': '1', 'type': 'connect', 'at_ms': 0}, {'id': '2', 'type': 'speech_start', 'at_ms': 20}, {'id': '3', 'type': 'transcript', 'at_ms': 100, 'text': 'show the weather'}, {'id': '4', 'type': 'speech_end', 'at_ms': 150}, {'id': '5', 'type': 'tts_start', 'at_ms': 220}, {'id': '6', 'type': 'tts_end', 'at_ms': 400}, {'id': '7', 'type': 'close', 'at_ms': 450}]
        print(json.dumps({'source': 'Synthetic event trace; no real call, ASR, LLM or TTS executed' if not args.input else 'provided event trace', **replay(events)}, indent=2))
    except (ValueError, TypeError, OSError) as exc:
        parser.error(str(exc))
if __name__ == '__main__':
    main()
