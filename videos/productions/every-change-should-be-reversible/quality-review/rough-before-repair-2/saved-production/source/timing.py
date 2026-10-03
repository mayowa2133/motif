"""Production-local event timing. Missing routes fail instead of using stale times."""

def resolve(shot, tick):
    route = shot['timing']['landmarks'][tick]
    if 'event_id' in route:
        matches = [e for e in shot['events'] if e['id'] == route['event_id']]
        if len(matches) != 1:
            raise ValueError('missing or duplicate event: ' + route['event_id'])
        return matches[0]['local_frame'] + route.get('offset', 0)
    if route.get('boundary') == 'end':
        return shot['endFrame'] - shot['startFrame'] + route.get('offset', 0)
    return route['local_frame']

def validate(plan):
    previous = 0
    for shot in plan['shots']:
        if shot['startFrame'] != previous:
            raise ValueError('shot schedule is not contiguous')
        count = shot['endFrame'] - shot['startFrame']
        previous = shot['endFrame']
        ids = [e['id'] for e in shot['events']]
        if len(ids) != len(set(ids)):
            raise ValueError('duplicate event ids')
        if any(not 0 <= e['local_frame'] < count for e in shot['events']):
            raise ValueError('event outside shot')
        values = [resolve(shot, key) for key in shot['timing']['landmarks']]
        if any(not 0 <= value <= count for value in values):
            raise ValueError('motion landmark outside shot')
        keys = list(shot['timing']['landmarks'])
        if any(resolve(shot, a) > resolve(shot, b) for a, b in zip(keys, keys[1:])):
            raise ValueError('motion landmarks reverse causal order')
        windows = sum(e['kind'] in ('contact','landing','handoff','impact') for e in shot['events'])
        if windows > 8:
            raise ValueError('too many temporal evidence windows')
    if previous != plan['targetFrames']:
        raise ValueError('film duration does not match shots')
