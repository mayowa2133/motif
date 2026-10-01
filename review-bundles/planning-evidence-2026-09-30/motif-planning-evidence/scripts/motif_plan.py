"""Validated production plan and finite state review, independent of any example brief."""
import json
import re
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / 'schemas/production-plan.schema.json').read_text())
ASSETS = {
 'wall': 'assets/scenes/scene-02/environment/arena-wall.svg',
 'floor': 'assets/scenes/scene-02/environment/arena-floor.svg',
 'desk': 'assets/scenes/scene-01/furniture/desk.svg',
 'calendar-board': 'assets/scenes/demo-03/calendar-board.svg',
 'appointment': 'assets/scenes/demo-03/appointment-card.svg',
 'proposal': 'assets/scenes/demo-03/proposal-slip.svg',
 'decision-tab': 'assets/scenes/demo-03/approval-tab.svg',
 'human-hand': 'assets/scenes/demo-03/human-fingertip.svg',
 'arena-arch': 'assets/scenes/scene-02/environment/arena-arch.svg',
 'crowd': 'assets/scenes/scene-02/environment/crowd-tiers.svg',
 'stage': 'assets/scenes/scene-02/furniture/arena-stage.svg',
 'answer-sheet': 'assets/scenes/scene-02/story/answer-sheet.svg',
 'stencil': 'assets/scenes/scene-02/story/link-test-stencil.svg',
 'bot': 'assets/characters/motif-bot/canonical/v1/motif-bot-v1.json',
}
WORLD_ASSETS = {
 'calendar': ['wall','floor','desk','calendar-board','appointment','proposal','decision-tab','human-hand','bot'],
 'arena': ['wall','floor','arena-arch','crowd','stage','answer-sheet','stencil','human-hand','bot'],
}
WORLD_SHOTS = {'calendar': {'calendar-wide','calendar-detail'}, 'arena': {'arena-pair','arena-a','arena-b','arena-review'}}

def tokens(text):
    return re.findall(r"[a-z0-9]+(?:'[a-z]+)?", text.lower())

def cue_index(sentence, cue):
    words, needle = tokens(sentence), tokens(cue)
    matches = [i for i in range(len(words)-len(needle)+1) if words[i:i+len(needle)] == needle]
    if not needle or len(matches) != 1:
        raise ValueError(f'cue must occur exactly once in its beat: {cue!r}')
    return matches[0]

def narration(plan):
    return ' '.join(b['narration'].strip() for b in plan['beats'])

def review_plan(plan, brief):
    issues = [f"schema {'.'.join(map(str,e.path))}: {e.message}" for e in Draft202012Validator(SCHEMA).iter_errors(plan)]
    if issues: return {'pass':False, 'issues':issues, 'states':[], 'final':None}
    if plan['status'] != 'ready': issues.append('capability_error: '+plan['capability_error'])
    if plan['message'] != brief['message'] or plan['audience'] != brief['audience']: issues.append('plan changed input message/audience')
    if plan['asset_requests']: issues.append('unresolved asset requests: '+', '.join(plan['asset_requests']))
    if set(plan['assets']) != set(WORLD_ASSETS[plan['environment']]): issues.append('assets must exactly bind the selected world registry')
    if not 4 <= len(plan['beats']) <= 6: issues.append('require 4–6 narrative beats')
    max_words=int((brief['intended_duration_seconds']-1)*2.6)
    planning_notes = [f'script has {len(tokens(narration(plan)))} words; suggested budget is {max_words}; actual speech duration is the acceptance gate'] if len(tokens(narration(plan))) > max_words else []
    if len({b['id'] for b in plan['beats']}) != len(plan['beats']): issues.append('duplicate beat IDs')
    if not 20 <= len(tokens(narration(plan))) <= 52: issues.append('script must contain 20–52 words; real duration is checked after TTS')
    if plan['environment'] == 'calendar' and any(not re.fullmatch('[A-Z]{2,6}',v) for v in plan['calendar'].values()): issues.append('calendar labels need 2–6 uppercase letters')
    state = {'calendar':'unchanged','A':'untested','B':'untested','winner':'none','handoff':False}
    facts, history = set(), []
    for beat in plan['beats']:
        if beat['shot'] not in WORLD_SHOTS[plan['environment']]: issues.append('shot/world mismatch: '+beat['shot'])
        for key in ('subject','action','before_after','focal_detail','consequence','narration','caption'):
            if not beat[key].strip(): issues.append(f"empty {key} in {beat['id']}")
        meaningful = [a for a in beat['actions'] if a['kind'] != 'bot.pose']
        if len(meaningful) > 1: issues.append('one meaningful action per beat allows visible evidence dwell')
        for action in beat['actions']:
            kind, subject, result = action['kind'], action['subject'], action['result']
            try: cue_index(beat['narration'], action['cue'])
            except ValueError as error: issues.append(str(error))
            if not set(action['requires']) <= facts: issues.append(f"unmet declared prerequisites for {kind}: {action['requires']}")
            before = state.copy()
            if kind.startswith('calendar.') and plan['environment'] != 'calendar' or kind.startswith('arena.') and plan['environment'] != 'arena': issues.append('action/world mismatch: '+kind)
            if kind.startswith('calendar.') and (subject != 'calendar' or result != 'none'): issues.append('invalid calendar action arguments')
            if kind == 'calendar.propose':
                if 'proposal-visible' in facts or 'declined' in facts or 'approved' in facts: issues.append('proposal already decided/present')
                facts.add('proposal-visible')
            elif kind in ('calendar.approve','calendar.decline'):
                if 'proposal-visible' not in facts or 'proposal-visible' not in action['requires']: issues.append('decision requires a visible proposal')
                facts.discard('proposal-visible'); facts.add('approved' if kind.endswith('approve') else 'declined')
            elif kind == 'calendar.commit':
                if 'approved' not in facts or 'approved' not in action['requires']: issues.append('booking requires human approval')
                state['calendar']='booked'; facts.add('booked')
            elif kind == 'arena.check':
                if subject not in ('A','B') or result not in ('pass','fail'): issues.append('check needs A/B and pass/fail')
                elif state[subject] != 'untested': issues.append('candidate already tested')
                else: state[subject]=result; facts.update([subject+'-tested', subject+'-'+result])
                if beat['shot'] != 'arena-'+subject.lower(): issues.append('test requires matching candidate close shot')
            elif kind == 'arena.select':
                if subject not in ('A','B') or state.get(subject) != 'pass' or subject+'-pass' not in action['requires']: issues.append('selection requires candidate pass')
                else: state['winner']=subject
                if result != 'none': issues.append('select result must be none')
            elif kind == 'arena.handoff':
                if subject != 'both' or result != 'none' or not {'A-tested','B-tested'} <= facts or not {'A-tested','B-tested'} <= set(action['requires']): issues.append('handoff requires both tested answers')
                if beat['shot'] != 'arena-review': issues.append('handoff needs receiving-person shot')
                state['handoff']=True; facts.add('handed-off')
            elif kind == 'bot.pose':
                if subject != 'bot' or result not in ('thinking','pointing','presenting','happy'): issues.append('unsupported bot pose')
            history.append({'beat':beat['id'],'kind':kind,'subject':subject,'before':before,'after':state.copy(),'facts':sorted(facts)})
    if state != plan['expected_final']: issues.append(f"expected final {plan['expected_final']} differs from simulated {state}")
    if plan['environment']=='calendar' and ('proposal-visible' in facts or not {'declined','booked'} & facts): issues.append('calendar proposal needs a visible resolved ending')
    if plan['environment']=='arena' and not state['handoff'] and state['winner']=='none': issues.append('tested answers need handoff or supported selection ending')
    if not plan['ending_action'].strip(): issues.append('missing ending action')
    return {'pass':not issues,'issues':issues,'states':history,'final':state,'facts':sorted(facts),'semantic_guarantee':False,'planning_notes':planning_notes}
