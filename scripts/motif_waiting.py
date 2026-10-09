"""Optional waiting-1.0 technical fixture: flat frontal shapes, pure frame state.

One bounded request/pending/response family, not a general film/artwork compiler.
Its placeholder actors cannot enter original-film mode or the canonical catalog.
"""
import argparse
import json
import math
import re
import subprocess
import tempfile
from pathlib import Path
from motif_evidence import read,write,sha,declare,require_scope,freeze_capture,seal_capture,completion
from motif_causal import validate_map
from motif_media_contracts import native_text,saved_audio,resource_inventory

ROLES=('worker','requester','work','input','result','support')
EVENTS=('request','stop','response','resume','complete')


def event_order(scene):
    return ('request','stop','response','arrival','resume','complete') if 'arrival' in scene['events'] else EVENTS


def painted_bounds(scene):
    """All extrema of this family's linear motion, including hands and strokes."""
    nodes={n['role']:n for n in scene['nodes']}
    wx,wy=nodes['work']['position'];ww,wh=nodes['work']['size'];grip=(wx,wy+wh/2)
    bounds=[]
    for node in scene['nodes']:
        role=node['role'];x,y=node['position'];w,h=node['size']
        if role in ('worker','requester'):
            if scene.get('mascot_contract') is not None:
                from motif_flat_mascot import bounds as mascot_bounds
                bounds.extend(mascot_bounds(node,None))
                if role=='worker':bounds.extend(mascot_bounds(node,grip))
                continue
            if h<=w:raise ValueError('actor body needs positive height below head')
            bounds.append((x,y,x+w,y+h))
            cx=x+w/2;head=y+w/2
            bounds.extend((a-2.4,head-2.4,a+2.4,head+2.4) for a in (cx-w*.16,cx+w*.16))
            bounds.append((cx-3.5,y+h*.55-3.5,cx+3.5,y+h*.55+3.5))
            hands=[(x+w if role=='worker' else x,y+h*.65)]
            if role=='worker':hands.append(grip)
            bounds.extend((a-6,b-6,a+6,b+6) for a,b in hands)
        elif role=='input':
            # Position is packet center; final packet edge meets the work grip.
            bounds.extend((a-w/2,b-h/2,a+w/2,b+h/2) for a,b in ((x,y),(grip[0]-w/2,grip[1])))
        else:
            bounds.append((x,y,x+w,y+h))
            if role=='work' and (w<12 or h<22):raise ValueError('work progress ink exceeds object')
    if any(a<0 or b<0 or c>360 or d>640 for a,b,c,d in bounds):
        raise ValueError('painted native phone geometry clipped')
    return bounds


def validate(scene):
    if scene.get('schema_version')!='waiting-1.0' or scene.get('style')!='flat-frontal-fixture':
        raise ValueError('only explicit waiting-1.0 flat frontal fixture supported')
    if scene.get('fps')!=30 or type(scene.get('frames')) is not int or not 30<=scene['frames']<=900:
        raise ValueError('bounded 30fps frame schedule (30–900 frames) required')
    events=scene.get('events',{})
    if set(events) not in (set(EVENTS),set(EVENTS)|{'arrival'}) or any(type(v) is not int for v in events.values()):
        raise ValueError('resolved integer event frames required')
    ordered=[events[e] for e in event_order(scene)]
    if not 0<ordered[0] or not all(a<b for a,b in zip(ordered,ordered[1:])) or ordered[-1]>=scene['frames']:
        raise ValueError('request/stop/response/optional-arrival/resume/complete order invalid')
    nodes=scene.get('nodes',[])
    if len(nodes)!=len(ROLES) or {n['role'] for n in nodes}!=set(ROLES):
        raise ValueError('exact bounded scene roles required')
    identities=[n['id'] for n in nodes]
    identities.extend(n['id']+'-hand' for n in nodes if n['role'] in ('worker','requester'))
    identities.extend(n['id']+'-progress' for n in nodes if n['role']=='work')
    if scene.get('mascot_contract') is not None:
        identities.extend(n['id']+suffix for n in nodes if n['role'] in ('worker','requester')
                          for suffix in ('-shell','-eye-0','-eye-1','-hand-left','-connector'))
    if len(set(identities))!=len(identities):raise ValueError('unique native/generated element identities required')
    if len({n['layer'] for n in nodes})!=len(nodes):raise ValueError('resolved distinct layer order required')
    for node in nodes:
        if not re.fullmatch(r'[a-z][a-z0-9-]*',node['id']) or type(node['layer']) is not int:
            raise ValueError('safe native ID and integer layer required')
        if not re.fullmatch(r'#[0-9A-Fa-f]{6}',node['color']):raise ValueError('resolved opaque color required')
        for pair in (node['position'],node['size']):
            if len(pair)!=2 or any(type(v) not in (int,float) or not math.isfinite(v) for v in pair):
                raise ValueError('finite dense 2D geometry required')
        if min(node['size'])<=0:raise ValueError('positive dimensions required')
        x,y=node['position'];w,h=node['size']
        if node['role']!='input' and (x<0 or y<0 or x+w>360 or y+h>640):raise ValueError('native phone geometry clipped')
    if scene.get('mascot_contract') is not None:
        from motif_flat_mascot import validate_binding
        validate_binding(scene)
    painted_bounds(scene)
    response=scene.get('response_cue')
    if response is not None:
        if (set(response)!= {'shape','color'} or response['shape']!='check-packet' or
                not re.fullmatch(r'#[0-9A-Fa-f]{6}',response['color'])):
            raise ValueError('response cue requires explicit check-packet and opaque color')
        request=next(n for n in nodes if n['role']=='input')
        if response['color'].lower()==request['color'].lower():raise ValueError('response needs distinct color plus shape')
        if min(request['size'])<18:raise ValueError('response check needs declared native visibility floor')
    validate_map(scene['causal_map'],scene['script'],scene['frames'])
    props=scene['causal_map']['propositions']
    if (len(props)!=1 or props[0]['shot_id']!='wait' or
            props[0]['stimulus_frame']!=events['request'] or props[0]['action_frame']!=events['stop'] or
            props[0]['persistent_until_frame']!=scene['frames']-1):
        raise ValueError('waiting causal map differs from resolved event schedule')
    for label in scene.get('text',[]):
        if len(label['frames'])!=2 or any(type(n) is not int for n in label['frames']) or not 0<=label['frames'][0]<=label['frames'][1]<scene['frames']:
            raise ValueError('locked text interval outside scene')
        if label.get('timing_source')!='manual-lock':
            raise ValueError('silent fixture text requires manual-lock; measured speech is unsupported')
        meaning=label.get('state_label')
        if meaning is not None:
            phrases={'request':'Request submitted','pending':'Await input','response':'Response in transit',
                     'received':'Response received','resumed':'Work resumes','complete':'Complete'}
            spans={'request':(events['request'],events['stop']-1),
                   'pending':(events['stop'],events['response']-1),
                   'response':(events['response'],events.get('arrival',events['resume'])-1),
                   'resumed':(events['resume'],events['complete']-1),
                   'complete':(events['complete'],scene['frames']-1)}
            if 'arrival' in events:spans['received']=(events['arrival']+1,events['complete']-1)
            if meaning not in phrases or label['text']!=phrases[meaning]:
                raise ValueError('state-bound caption wording conflicts with bounded state')
            if meaning not in spans:raise ValueError('receipt caption requires explicit pictured arrival before reaction')
            start,end=spans[meaning]
            if not start<=label['frames'][0]<=label['frames'][1]<=end:
                raise ValueError('state-bound caption interval conflicts with bounded state')
    return {'status':'DATA_VALID','style_identity':'APPROVED_GEOMETRY_FLAT_BINDING_REVIEW_REQUIRED' if scene.get('mascot_contract') is not None else 'PLACEHOLDER_ONLY','perception':'UNASSESSED'}


def state_at(scene,frame,control=None):
    if type(frame) is not int or not 0<=frame<scene['frames']:raise ValueError('frame outside scene')
    if control not in (None,'no-stimulus','continues-pending'):raise ValueError('unknown diagnostic control')
    e=scene['events'];stopped=e['stop']<=frame<e['resume']
    before=min(frame,e['stop'])/e['stop']*.35
    after=max(0,frame-e['resume'])/(e['complete']-e['resume'])*.65
    progress=min(1,before+after)
    if control=='continues-pending' and stopped:progress=.35+.4*(frame-e['stop'])/(e['resume']-e['stop'])
    request=e['request']<=frame<e['response'] and control!='no-stimulus'
    response=e['response']<=frame<(scene['frames'] if 'arrival' in e else e['resume'])
    status='complete' if frame>=e['complete'] else 'pending' if stopped else 'working'
    state={'frame':frame,'status':status,'progress':progress,'request_visible':request,
           'response_visible':response,'result_visible':frame>=e['complete'],'contact':not stopped and frame<e['complete']}
    if 'arrival' in e:
        state.update(response_in_transit=e['response']<=frame<e['arrival'],response_arrived=frame>=e['arrival'])
    return state


def svg_at(scene,frame,root=Path('.'),control=None,captions=False):
    if scene.get('mascot_contract') is not None:
        from motif_flat_mascot import validate_binding
        validate_binding(scene)
    state=state_at(scene,frame,control);nodes={n['role']:n for n in scene['nodes']};body=[]
    grip=[nodes['work']['position'][0],nodes['work']['position'][1]+nodes['work']['size'][1]/2]
    for node in sorted(scene['nodes'],key=lambda n:n['layer']):
        role=node['role'];x,y=node['position'];w,h=node['size'];color=node['color'];markup=''
        if role in ('worker','requester'):
            if scene.get('mascot_contract') is not None:
                from motif_flat_mascot import actor
                markup=actor(root,scene['mascot_contract'],node,grip if role=='worker' and state['contact'] else None)
            else:
                cx=x+w/2;head=y+w/2;hand=[x+w if role=='worker' else x,y+h*.65]
                if role=='worker' and state['contact']:hand=grip
                markup=(f'<circle cx="{cx}" cy="{head}" r="{w/2}"/><rect x="{x+w*.15}" y="{y+w}" width="{w*.7}" height="{h-w}" rx="8"/>'
                    f'<path d="M{cx} {y+h*.55}L{hand[0]} {hand[1]}" fill="none" stroke="{color}" stroke-width="7"/>'
                    f'<circle id="{node["id"]}-hand" cx="{hand[0]}" cy="{hand[1]}" r="6"/>'
                    f'<circle cx="{cx-w*.16}" cy="{head}" r="2.4" fill="#FFFFFF"/><circle cx="{cx+w*.16}" cy="{head}" r="2.4" fill="#FFFFFF"/>')
        elif role=='input':
            if state['request_visible'] or state['response_visible']:
                e=scene['events'];start,end=(e['response'],e.get('arrival',e['resume'])) if state['response_visible'] else (e['request'],e['stop'])
                fraction=min(1,max(0,(frame-start)/(end-start)))
                x+=(grip[0]-w/2-x)*fraction;y+=(grip[1]-y)*fraction
                markup=f'<rect x="{x-w/2}" y="{y-h/2}" width="{w}" height="{h}" rx="4"/>'
                if state['response_visible'] and scene.get('response_cue'):
                    color=scene['response_cue']['color']
                    markup+=(f'<path d="M{x-w*.27} {y}L{x-w*.05} {y+h*.22}L{x+w*.29} {y-h*.24}" '
                             'fill="none" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')
        elif role!='result' or state['result_visible']:
            markup=f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5"/>'
            if role=='work':markup+=f'<rect id="{node["id"]}-progress" x="{x+5}" y="{y+10}" width="{max(2,(w-10)*state["progress"])}" height="12" fill="#FFFFFF"/>'
        body.append(f'<g id="{node["id"]}" data-role="{role}" fill="{color}">{markup}</g>')
    if captions:
        for label in scene.get('text',[]):
            start,end=label['frames']
            if start<=frame<=end:
                markup,_=native_text(root,label);body.append('<g fill="#242D39">'+markup+'</g>')
    return '<svg xmlns="http://www.w3.org/2000/svg" width="360" height="640" viewBox="0 0 360 640"><rect width="360" height="640" fill="#F8F6EF"/>'+''.join(body)+'</svg>',state


def compile_waiting(project,scene):
    project=Path(project);validate(scene)
    scope=require_scope(project)
    if scene!=read(project/'production-plan.json'):
        raise ValueError('waiting input differs from saved production plan')
    if scope['actual_mode']!='technical-fixture':
        raise ValueError('waiting family is fixture-only; film perception gates are pending')
    for label in scene.get('text',[]):native_text(project,label)
    audio=saved_audio(project,scene)
    resources=[r for label in scene.get('text',[]) for r in (label['font'],label['license'])]
    if scene.get('mascot_contract') is not None:
        from motif_flat_mascot import CONTRACT_SHA
        if scene['mascot_contract']['sha256']!=CONTRACT_SHA:raise ValueError('approved geometry version changed')
        resources.append(scene['mascot_contract'])
    if scene.get('audio'):resources.append(scene['audio']['resource'])
    write(project/'resource-manifest.json',resource_inventory(project,resources))
    snapshots=[state_at(scene,f) for f in range(scene['frames'])]
    e=scene['events'];pending=snapshots[e['stop']:e['resume']]
    if len({s['progress'] for s in pending})!=1 or any(s['result_visible'] for s in pending):
        raise ValueError('pending state must retain work without accumulation/result')
    if not all(s['result_visible'] for s in snapshots[e['complete']:]):raise ValueError('result must persist')
    write(project/'scene-events.json',{'schemaVersion':'waiting-1.0','fps':30,'durationSec':scene['frames']/30,
          'events':[{'time':e[k]/30,'kind':k} for k in event_order(scene)],'state_trace':snapshots})
    write(project/'causal-map.json',scene['causal_map'])
    write(project/'critical-intervals.json',[{'id':'wait','critical_intervals':[[0,scene['frames']-1]]}])
    write(project/'execution-bindings.json',{'native_ids':[n['id'] for n in scene['nodes']],
          'contact_math':'worker painted hand center equals work grip while working',
          'perceived_contact':'UNASSESSED','mobile_readability':'UNASSESSED',
          'baseline_artistic_gain':'UNASSESSED','rollback':'previous compiler/scene input hashes; no canonical changes'})
    write(project/'composition-manifest.json',{'version':1,'capability':'waiting-1.0',
          'requested_mode':scope['requested_mode'],'actual_mode':'technical-fixture',
          'requirements':[{'proposition_id':p['id'],'route':'registered bounded capability',
                           'script_span':p['word_range'],'capability':'waiting-1.0'} for p in scene['causal_map']['propositions']],
          'source_plan_sha256':sha(project/'production-plan.json'),'integer_picture_frames':scene['frames'],
          'data_truth':'DATA_VALID','rendered_truth':'UNASSESSED','perceived_truth':'UNASSESSED',
          'editing_level':'native source/component edits; no generic timeline editor',
          'saved_audio':audio,'shared_qa':'motif_quality evidence sampler; scope supplements cannot approve film',
          'unsupported_requirements':'stop; record a scoped custom-authoring task instead of substituting a film',
          'interventions':[]})
    return {'status':'TECHNICAL_FIXTURE_COMPILED','frames':len(snapshots),'semantic_perception':'UNASSESSED'}


def encode(project,scene,control=None,captions=False,name='candidate',delivery=False):
    """Local standard-tool encode; complete inputs frozen before any frame paint."""
    import cairosvg
    if type(delivery) is not bool:raise ValueError('explicit delivery boolean required')
    if not re.fullmatch(r'[a-z][a-z0-9-]*',name):raise ValueError('safe fresh encode name required')
    if control not in (None,'no-stimulus','continues-pending'):raise ValueError('unknown diagnostic control')
    project=Path(project)
    output=project/'renders'/(name+'.mp4');output.parent.mkdir(parents=True,exist_ok=True)
    if output.exists():raise ValueError('preserve existing encode; choose a fresh name')
    compile_waiting(project,scene)
    if captions:
        for label in scene.get('text',[]):native_text(project,label)
    config={'version':1,'control':control,'captions':captions,
          'compiler_sha256':sha(__file__),'media_contract_sha256':sha(Path(__file__).with_name('motif_media_contracts.py')),
          'flat_mascot_sha256':sha(Path(__file__).with_name('motif_flat_mascot.py')) if scene.get('mascot_contract') is not None else None,
          'codec':'libx264 CRF18 yuv420p; optional saved PCM to AAC192k',
          'saved_audio':saved_audio(project,scene),'source_scene_sha256':sha(project/'production-plan.json')}
    if delivery:config['delivery_dimensions']=[1080,1920]
    write(project/'render-config.json',config)
    capture=freeze_capture(project)
    with tempfile.TemporaryDirectory(prefix='waiting-frames-',dir=project) as temporary:
        directory=Path(temporary)
        for frame in range(scene['frames']):
            svg,_=svg_at(scene,frame,project,control,captions)
            size={'output_width':1080,'output_height':1920} if delivery else {}
            cairosvg.svg2png(bytestring=svg.encode(),write_to=str(directory/f'f-{frame:05d}.png'),**size)
        command=['ffmpeg','-v','error','-n','-framerate','30','-i',str(directory/'f-%05d.png')]
        if scene.get('audio'):
            command+=['-i',str(project/scene['audio']['resource']['path']),'-map','0:v','-map','1:a','-c:a','aac','-b:a','192k']
        command+=['-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(output)]
        subprocess.run(command,check=True)
    seal_capture(project,capture,[output]);completion(project,output)
    write(project/'renders'/(name+'.scope.json'),{'artifact_sha256':sha(output),'caption_mode':captions,
          'control':control,'normal_speed_comprehension':'UNASSESSED','listening_av':'UNASSESSED',
          'audio':saved_audio(project,scene),'baseline_comparison':'NOT_A_MAIN_METHOD_AB'})
    return output


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scene',type=Path,required=True);parser.add_argument('--project',type=Path,required=True)
    parser.add_argument('--encode',action='store_true');parser.add_argument('--captions',action='store_true')
    parser.add_argument('--delivery',action='store_true',help='direct vector raster at1080x1920')
    parser.add_argument('--control',choices=['no-stimulus','continues-pending']);parser.add_argument('--name',default='candidate')
    args=parser.parse_args();scene=read(args.scene);p=args.project
    if p.exists():raise ValueError('fresh isolated project required')
    p.mkdir(parents=True);write(p/'brief.json',{'script':scene['script'],'style':scene['style']})
    write(p/'production-plan.json',scene);declare(p,'technical-fixture','motif_waiting')
    result=encode(p,scene,args.control,args.captions,args.name,args.delivery) if args.encode else compile_waiting(p,scene)
    print(result)


if __name__=='__main__':main()
