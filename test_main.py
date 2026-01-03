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

    def test_barge_in_loop(self):
        r = replay(events(['connect', 'speech_start', 'speech_end', 'tts_start', 'barge_in', 'speech_end', 'tts_start', 'tts_end']))
        self.assertEqual(r['state'], 'idle')
        self.assertEqual(r['barge_ins'], 1)
        self.assertIsNone(r['duration_ms'])

    def test_illegal_order(self):
        with self.assertRaises(ValueError):
            replay(events(['connect', 'tts_start']))

    def test_duplicates_and_time(self):
        e = events(['connect', 'close'])
        e[1]['id'] = '0'
        with self.assertRaises(ValueError):
            replay(e)
        e = events(['connect', 'close'])
        e[1]['at_ms'] = -1
        with self.assertRaises(ValueError):
            replay(e)

    def test_transcript_validation(self):
        e = events(['connect', 'speech_start', 'transcript'])
        with self.assertRaises(ValueError):
            replay(e)
        e[-1]['text'] = 'synthetic text'
        self.assertEqual(replay(e)['transcripts'], ['synthetic text'])
if __name__ == '__main__':
    unittest.main()
