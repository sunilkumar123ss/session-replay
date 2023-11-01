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
