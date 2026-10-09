"""Validate bounded causal maps and freeze comprehension study inputs.

Validation establishes data consistency, never semantic perception or factual
truth. Use motif_experiment_gate for candidate promotion and rollback.
"""
import argparse
import json
import math
from pathlib import Path
from motif_evidence import read, write, sha

QUESTIONS = ('cause-of-stop', 'responsible-actor', 'persistent-pending-state', 'resume-condition')


def interval(value, frame_count):
    if (not isinstance(value, list) or len(value) != 2 or
            any(type(x) is not int for x in value) or
            not 0 <= value[0] <= value[1] < frame_count):
        raise ValueError('inclusive critical interval outside movie')
    return range(value[0], value[1] + 1)


def validate_map(mapping, script, frame_count):
    if type(frame_count) is not int or frame_count < 1:
        raise ValueError('positive frame count required')
    words = script.split()
    propositions = mapping.get('propositions', [])
    if not propositions:
        raise ValueError('explicit causal propositions required')
    seen = set()
    for prop in propositions:
        identifier = prop.get('id')
        if not isinstance(identifier, str) or not identifier or identifier in seen:
            raise ValueError('unique proposition IDs required')
        seen.add(identifier)
        span = prop.get('word_range', [])
        if (len(span) != 2 or any(type(x) is not int for x in span) or
                not 0 <= span[0] < span[1] <= len(words) or
                prop.get('text') != ' '.join(words[span[0]:span[1]])):
            raise ValueError('exact script proposition span required')
        for key in ('shot_id', 'subject', 'initiator', 'stimulus', 'action', 'before', 'after',
                    'persistent_result', 'diagnostic_feature'):
            if not isinstance(prop.get(key), str) or not prop[key].strip():
                raise ValueError('missing causal field: ' + key)
        reviewed=interval(prop.get('review_interval'), frame_count)
        onset, effect = prop.get('stimulus_frame'), prop.get('action_frame')
        if (type(onset) is not int or type(effect) is not int or
                not 0 <= onset <= effect < frame_count):
            raise ValueError('stimulus must precede or coincide with action')
        until=prop.get('persistent_until_frame')
        if type(until) is not int or not effect<=until<frame_count or onset not in reviewed or until not in reviewed:
            raise ValueError('review interval must include stimulus, action and retained consequence')
        claim = prop.get('claim', {})
        if claim.get('status') not in ('supported', 'unverified', 'illustrative'):
            raise ValueError('explicit factual claim classification required')
        if claim['status'] == 'supported':
            for key in ('source', 'as_of', 'excerpt', 'uncertainty'):
                if not isinstance(claim.get(key), str) or not claim[key].strip():
                    raise ValueError('supported claim needs attribution/date/excerpt/uncertainty')
    return {'status': 'DATA_VALID', 'propositions': len(seen),
            'semantic_perception': 'UNASSESSED', 'factual_truth': 'UNASSESSED'}


def coverage(shots, frame_count, plan_ids):
    if len(shots) != len(plan_ids) or {s['id'] for s in shots} != set(plan_ids):
        raise ValueError('shot evidence IDs differ from saved plan')
    required = {}
    for shot in shots:
        bounds = shot.get('critical_intervals', [])
        if not bounds:
            raise ValueError('complete critical intervals required for ' + shot['id'])
        required[shot['id']] = sorted({n for bound in bounds for n in interval(bound, frame_count)})
    return required


def verify_coverage(required, observed):
    if set(observed) != set(required):
        raise ValueError('critical shot coverage incomplete')
    for shot, frames in required.items():
        actual = observed[shot]
        if (any(type(x) is not int for x in actual) or len(actual) != len(set(actual)) or
                not set(frames).issubset(actual)):
            raise ValueError('consecutive critical frame coverage incomplete: ' + shot)


def freeze_study(destination, protocol, pairs):
    """Four supplied novel briefs; no generated winners or hidden source reads."""
    destination = Path(destination)
    if destination.exists():
        raise ValueError('study destination exists; preserve frozen study')
    if len(pairs) != 4 or len({p['id'] for p in pairs}) != 4:
        raise ValueError('four unique unfamiliar script pairs required')
    if not protocol.get('author_minutes_ceiling') or not protocol.get('randomization_seed'):
        raise ValueError('preregister effort ceiling and randomization seed')
    for pair in pairs:
        if not pair.get('unfamiliar_to_author_attestation'):
            raise ValueError('unfamiliar-script attestation required')
        for key in ('script', 'style', 'mode', 'audio', 'geometry'):
            if not pair.get(key):
                raise ValueError('matched input missing: ' + key)
        for arm in ('baseline', 'candidate'):
            if not pair.get(arm, {}).get('components'):
                raise ValueError('frozen baseline/candidate component hashes required')
            for path, digest in pair[arm]['components'].items():
                if sha(path) != digest:
                    raise ValueError('component hash mismatch')
    write(destination / 'protocol.json', protocol)
    write(destination / 'pairs.json', pairs)
    result = {'protocol_sha256': sha(destination / 'protocol.json'),
              'pairs_sha256': sha(destination / 'pairs.json'),
              'normal_speed': 'UNASSESSED', 'listening_av': 'UNASSESSED',
              'promotion': 'Use existing experiment gate after actual independent review.'}
    write(destination / 'freeze.json', result)
    return result


def playback_counts(records, artifact_sha256, protocol_sha256):
    """Summarize attested first exposures; never manufacture viewer answers."""
    if len(records) != 5:
        raise ValueError('five fresh viewer records required per arm')
    viewers = set()
    counts = dict.fromkeys(QUESTIONS, 0)
    for record in records:
        viewer = record.get('viewer')
        if not viewer or viewer in viewers or record.get('viewer_is_author') is not False:
            raise ValueError('distinct independent viewers required')
        viewers.add(viewer)
        if (record.get('artifact_sha256') != artifact_sha256 or
                record.get('protocol_sha256') != protocol_sha256 or
                record.get('method') != 'human-normal-speed-playback' or
                record.get('speed') != 1 or record.get('first_exposure') is not True or
                record.get('producer_rationale_shown') is not False or not record.get('observation')):
            raise ValueError('fresh actual normal-speed playback attestation required')
        answers = record.get('correct', {})
        if set(answers) != set(QUESTIONS) or any(type(x) is not bool for x in answers.values()):
            raise ValueError('all preregistered causal questions required')
        for question, correct in answers.items():
            counts[question] += int(correct)
    return {'counts': counts, 'proposed_floor_met': all(n >= 4 for n in counts.values()),
            'scope': 'attested normal-speed comprehension only; no listening/AV inference'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--map', type=Path, required=True)
    parser.add_argument('--script', type=Path, required=True)
    parser.add_argument('--frames', type=int, required=True)
    args = parser.parse_args()
    print(json.dumps(validate_map(read(args.map), args.script.read_text().strip(), args.frames), indent=2))


if __name__ == '__main__':
    main()
