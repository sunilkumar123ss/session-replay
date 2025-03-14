import unittest
try:
    from .main import replay
except ImportError:
    from main import replay

def events(kinds):
    return [{'id': str(i), 'type': kind, 'at_ms': i * 10} for (i, kind) in enumerate(kinds)]

class ReplayTests(unittest.TestCase):

    def test_full_lifecycle(self):
        r = replay(events(['connect', 'speech_start', 'speech_end', 'tts_start', 'tts_end', 'close']))
        self.assertEqual(r['duration_ms'], 50)
        self.assertEqual(r['completed_utterances'], 1)
        self.assertTrue(r['complete'])
