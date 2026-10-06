"""Resolve explicit semantic cuts from aligned source words, never equal fractions.

Consumes source-word alignment records, including disclosed uncertain onsets.
No ASR/provider call, creative scene selection, time estimation or script rewrite.
"""
import math
import re

def normalized(word):
    return re.sub(r'[^a-z0-9]', '', word.lower())

def resolve_markers(words, requests):
    output = []
    seen = set()
    last = -float('inf')
    for request in requests:
        marker_id = request['id']
        if not marker_id or marker_id in seen:
            raise ValueError('Marker IDs must be nonempty and unique')
        seen.add(marker_id)
        phrase = [normalized(w) for w in request['phrase'].split()]
        if not phrase or not all(phrase):
            raise ValueError('Marker phrase must contain words')
        lo, hi = request.get('word_range', [0, len(words)])
        if not 0 <= lo < hi <= len(words):
            raise ValueError('Invalid half-open source word range')
        found = [i for i in range(lo, hi-len(phrase)+1)
                 if [normalized(w['text']) for w in words[i:i+len(phrase)]] == phrase]
        if len(found) != 1:
            raise ValueError(f'Marker {marker_id} has {len(found)} matches; narrow its word range')
        i = found[0]
        time = float(words[i]['start'])
        if not math.isfinite(time):
            raise ValueError('Aligned onset must be finite')
        if time < last:
            raise ValueError('Requested markers are not in temporal order')
        if time < 0:
            raise ValueError('Negative aligned onset')
        last = time
        output.append({'id': marker_id, 'phrase': request['phrase'], 'time': time,
                       'word_range': [i, i+len(phrase)],
                       'alignment_states': [w.get('status', 'unspecified') for w in words[i:i+len(phrase)]]})
    return output
