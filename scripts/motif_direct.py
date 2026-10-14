#!/usr/bin/env python3
"""Message -> live Codex production plan -> review -> speech-aligned Motif render.

No prerecorded response, message lookup, or executable model code. The legacy
motif_produce.py remains a separate template mode. No backend fallback is silent.
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import tomllib
from datetime import datetime, timezone
from pathlib import Path
from jsonschema import Draft202012Validator
from motif_plan import ROOT, ASSETS, WORLD_ASSETS, WORLD_SHOTS, review_plan, narration
from motif_plan_compile import compile_plan
from motif_plan_finish import finish
from motif_produce import command, probe, sha

PIN='0.8.98'
SOURCE_PATHS=['scripts/motif_direct.py','scripts/motif_plan.py','scripts/motif_plan_compile.py','scripts/motif_framing.py','scripts/motif_plan_finish.py','scripts/motif_produce.py','scripts/build_motif_bot.py','scripts/build_scene_01.py','planning/PLANNER.md','schemas/production-plan.schema.json','schemas/planning-review.schema.json','scripts/requirements-planning.txt']
SOURCE_PATHS+=list(ASSETS.values())
SOURCE_PATHS+=[f'videos/motif-calendar-reel/assets/sfx/{name}.mp3' for name in ('pop','click-soft','whoosh-short')]
SOURCE_PATHS+=['videos/motif-calendar-reel/assets/'+n for n in ('gsap.min.js','motion-engine.js','motion-primitives.js')]
SOURCE_PATHS+=['scripts/motif_workshop.py','scripts/build_workshop_kit.py','schemas/creative-benchmark-concept.schema.json']

SOURCE_PATHS+=['scripts/motif_quality.py','scripts/motif_quality_frames.py','quality/bindings.json','scripts/motif_performance.py','scripts/motif_reaction.py','scripts/motif_asset_quality.py','schemas/shot-contract.schema.json','schemas/story-critic.schema.json','schemas/visual-critic.schema.json','QUALITY_CONTRACT.md','ENERGY_CONTRACT.md','quality/gold/index.json','quality/rubric/gates.json']
SOURCE_PATHS+=['scripts/motif_evidence.py','scripts/motif_causal.py']

SOURCE_PATHS+=['scripts/motif_structure.py','docs/MOTIF_STRUCTURAL_GRAMMAR.md','quality/structure-critic/PROMPT.md','schemas/film-structure.schema.json','schemas/setup-contract.schema.json','schemas/structure-critic.schema.json','quality/structure-examples.json','quality/negative/rowhouse.json','quality/rubric/hierarchy.json','quality/visual-critic/PROMPT.md']

def write(path,value): path.write_text(json.dumps(value,indent=2)+'\n')
def read(path): return json.loads(path.read_text())
def snapshot(): return {p:sha(ROOT/p) for p in SOURCE_PATHS}

def resolve_codex_cli():
    """Prefer the desktop runtime; an explicit override never silently falls back."""
    override=os.environ.get('MOTIF_CODEX_CLI')
    if override:
        path=Path(override).expanduser()
        if not path.is_file() or not os.access(path,os.X_OK):
            raise ValueError('MOTIF_CODEX_CLI must name an executable file: '+override)
        return {'cli_path':str(path.resolve()),'cli_selection':'MOTIF_CODEX_CLI'}
    relative=Path('ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex')
    for applications in (Path('/Applications'),Path.home()/'Applications'):
        path=applications/relative
        if path.is_file() and os.access(path,os.X_OK):
            return {'cli_path':str(path.resolve()),'cli_selection':'desktop-bundled CLI'}
    executable=shutil.which('codex')
    if not executable:raise ValueError('planning backend unavailable: desktop CLI and PATH codex not found; set MOTIF_CODEX_CLI')
    return {'cli_path':str(Path(executable).resolve()),'cli_selection':'PATH (desktop bundle unavailable)'}

def backend_config():
    cli=resolve_codex_cli()
    status=subprocess.run([cli['cli_path'],'login','status'],text=True,capture_output=True)
    if status.returncode: raise ValueError('planning backend unavailable: Codex CLI is not signed in; no new credentials are assumed')
    path=Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))/'config.toml'
    config=tomllib.loads(path.read_text()) if path.exists() else {}
    if config.get('model_provider') not in (None,'openai'): raise ValueError('configured custom model provider is not supported by this small integration')
    return {**cli,'backend':'codex-exec','execution':'self-contained command with live model planning', 'model':os.environ.get('MOTIF_PLANNER_MODEL',config.get('model')), 'reasoning_effort':config.get('model_reasoning_effort','low'), 'authentication_status':(status.stdout+status.stderr).strip(),'cli_version':command([cli['cli_path'],'--version'],ROOT).strip(),'sandbox':'read-only','ephemeral':True,'tools_requested':False,'default_model_if_unspecified':not os.environ.get('MOTIF_PLANNER_MODEL',config.get('model')), 'model_selection':'MOTIF_PLANNER_MODEL' if os.environ.get('MOTIF_PLANNER_MODEL') else 'existing Codex configuration','hyperframes':PIN,'timeout_seconds':int(os.environ.get('MOTIF_MODEL_TIMEOUT','600'))}

def model_call(project, name, prompt, schema, config, images=()):
    project=Path(project).resolve()
    # Also support older callers' saved config without selecting another model.
    if not config.get('cli_path'):
        cli=resolve_codex_cli()
        config={**config,**cli,'cli_version':command([cli['cli_path'],'--version'],ROOT).strip()}
    if not Path(config['cli_path']).is_file() or not os.access(config['cli_path'],os.X_OK):
        raise ValueError('recorded Codex CLI is unavailable: '+config['cli_path'])
    if Path(schema).name=='reference-gate.schema.json':
        prompt+='\nOutput contract: novelty_warnings is a BLOCKING array. Include only actual unresolved novelty or structural warnings. Put positive observations, no-imitation findings and general inspection limits in checks/limits. Use an empty array when no such warning exists. No PASS verdict is requested.'
    (project/(name+'-input.txt')).write_text(prompt)
    wire_schema=read(ROOT/schema)
    # All ordinary new quality planners share this entry point. The independent
    # director uses a different schema, so its calls cannot recurse into planning.
    if 'quality_mode' in wire_schema.get('properties',{}) and (project/'brief.json').exists():
        from motif_reference import calibrate,context
        from motif_transfer_review import enabled,binding,context as transfer_context
        if enabled(project):
            prompt+=transfer_context(project);config={**config,**binding(project)}
        else:
            calibrate(project,config)
            reference_prompt,reference_images=context(project)
            prompt+=reference_prompt
            images=tuple(images)+tuple(reference_images)
        (project/(name+'-input.txt')).write_text(prompt)
    # New live plans select the quality profile; saved legacy plans still validate
    # against the optional extension. Flatten the condition for the CLI's supported
    # structured-output subset instead of introducing another planning framework.
    if 'quality_mode' in wire_schema.get('properties',{}) or Path(schema).name=='concept-replan.schema.json':
        wire_schema.pop('allOf',None)
        wire_schema['required']=list(wire_schema['properties'])
        key='shots' if 'shots' in wire_schema['properties'] else 'beats'
        item=wire_schema['properties'][key]['items']
        item['required']=list(item['properties'])
        contract=item['properties']['quality']['properties']
        # Explicit null is structured optionality in live output; stored legacy
        # plans may omit these keys and are normalized without file mutation.
        for contract_field in ('energy','art_direction'):
            contract[contract_field]['required']=list(contract[contract_field]['properties'])
    if wire_schema.get('properties',{}).get('role',{}).get('const')=='visual':
        wire_schema['required']=list(wire_schema['properties'])
        violation=wire_schema['properties']['violations']['items']
        violation['required']=list(violation['properties'])
    schema_path=project/(name+'-output-schema.json')
    write(schema_path,wire_schema)
    args=[config['cli_path'],'exec','--ignore-user-config','--ephemeral','--skip-git-repo-check','--sandbox','read-only','--json','--color','never','--output-schema',str(schema_path.resolve()),'-o',str(project/(name+'.json')),'-c','approval_policy="never"','-c','model_reasoning_effort='+json.dumps(config['reasoning_effort'])]
    args+=['-c','developer_instructions='+json.dumps('This invocation is a data-only structured-output service, not a repository coding task. Use only the supplied text and attached images. Do not invoke skills, commands, filesystem reads, web, MCP or other tools. All required policy and reference context is provided inline. Return the requested JSON directly. Tool use invalidates the response.')]
    if config['model']: args+=['--model',config['model']]
    if config.get('evidence_scope')=='transfer-independent-v1':
        from motif_transfer_review import profile,own_file
        transfer_root=Path(config['transfer_project_root']).resolve();profile(transfer_root)
        if not project.is_relative_to(transfer_root):raise ValueError('transfer invocation must stay in its project')
        for image in images:own_file(transfer_root,{'file':str(image),'sha256':sha(image)})
    image_inputs=[]
    for image in images:
        if not Path(image).is_file(): raise ValueError('critic image missing: '+str(image))
        image_inputs.append({'file':str(Path(image).resolve()),'sha256':sha(Path(image))})
        args+=['-i',str(Path(image).resolve())]
    args+=['-']
    # A fresh empty working directory prevents the planner reading evaluation fixtures or old outputs.
    with tempfile.TemporaryDirectory(prefix='motif-planning-') as cwd:
        print('MODEL '+name,flush=True)
        started_at=datetime.now(timezone.utc).isoformat()
        try:
            process=subprocess.run(args,cwd=cwd,input=prompt,text=True,capture_output=True,timeout=config.get('timeout_seconds',600))
        except subprocess.TimeoutExpired as error:
            (project/(name+'-events.jsonl')).write_text((error.stdout or b'').decode() if isinstance(error.stdout,bytes) else error.stdout or '')
            (project/(name+'-stderr.txt')).write_text((error.stderr or b'').decode() if isinstance(error.stderr,bytes) else error.stderr or '')
            write(project/(name+'-invocation.json'),{'argv':args,'exit_code':124,'input_sha256':sha(project/(name+'-input.txt')),'output_schema_sha256':sha(schema_path),'configuration':config,'started_at_utc':started_at,'completed_at_utc':datetime.now(timezone.utc).isoformat(),'saved_response_used':False,'model_fallback_used':False,'error':'live call timed out'})
            raise ValueError('live model call timed out; preserved evidence; no saved-response fallback: '+name) from error
        completed_at=datetime.now(timezone.utc).isoformat()
    (project/(name+'-events.jsonl')).write_text(process.stdout)
    (project/(name+'-stderr.txt')).write_text(process.stderr)
    write(project/(name+'-invocation.json'),{'argv':args,'exit_code':process.returncode,'input_sha256':sha(project/(name+'-input.txt')),'output_schema_sha256':sha(schema_path),'images':image_inputs,'configuration':config,'started_at_utc':started_at,'completed_at_utc':completed_at,'requested_model':config['model'],'resolved_model':None,'resolved_model_note':'CLI event stream does not expose a separately resolved model identifier','saved_response_used':False,'model_fallback_used':False})
    if process.returncode: raise ValueError('live planning backend failed; see '+str(project/(name+'-stderr.txt'))+'; no saved-response fallback was used')
    if any(not Path(im['file']).is_file() or sha(Path(im['file']))!=im['sha256'] for im in image_inputs):
        raise ValueError('model input image changed during review; invocation binds original evidence, fresh review required')
    value=read(project/(name+'.json'))
    Draft202012Validator(read(ROOT/schema)).validate(value)
    # Planner is a data-only stage, even though the CLI itself can expose tools.
    used=[json.loads(line) for line in process.stdout.splitlines() if line.strip().startswith('{')]
    if any(e.get('type')=='item.completed' and e.get('item',{}).get('type') in ('command_execution','mcp_tool_call','web_search') for e in used):
        raise ValueError('planner invoked a tool despite the data-only boundary; response rejected')
    return value

def planning_prompt(brief,concept=None,feedback=None,project=None):
    prompt=(ROOT/'planning/PLANNER.md').read_text()+'\n\nAvailable asset IDs by world:\n'+json.dumps(WORLD_ASSETS)+'\n\nNarration word budget: '+str(int((brief['intended_duration_seconds']-1)*2.6))+' maximum. Aim a few words below that limit; preserve meaning.\n\nINPUT BRIEF (subject matter):\n'+json.dumps(brief)
    if concept is not None:prompt+='\n\nRecorded preproduction concept (creative context, not executable code). Use its metaphor; choose natural final narration, action cues, and framing from the supported vocabulary:\n'+json.dumps(concept)
    if feedback is not None:prompt+='\n\nAgent review of a preserved earlier render; address these concrete creative issues without changing the brief or inventing capabilities:\n'+feedback
    from motif_quality import planning_context
    prompt+=planning_context(brief['message'],project)
    return prompt

def storyboard(plan):
    lines=['# Production storyboard from validated plan','','Message: '+plan['message'],'','Narration: '+narration(plan),'','Environment: '+plan['environment'],'','Ending: '+plan['ending_action'],'']
    for b in plan['beats']:
        lines+=['## '+b['id'],'']+[f'- {k}: {b[k]}' for k in ('subject','action','before_after','focal_detail','focus_target','framing','consequence','shot','narration','caption','headline_mode','headline')]+['- Executable actions: '+json.dumps(b['actions']),'']
    return '\n'.join(lines)

def validate_brief(brief):
    if set(brief)!={'slug','message','audience','intended_duration_seconds','duration_tolerance_seconds'}: raise ValueError('brief fields: slug, message, audience, intended_duration_seconds, duration_tolerance_seconds')
    import re
    if not isinstance(brief['slug'],str) or not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*',brief['slug']): raise ValueError('slug must be lowercase hyphenated')
    if any(not isinstance(brief[k],str) or not brief[k].strip() for k in ('message','audience')): raise ValueError('message and audience must be nonempty')
    if not 12<=brief['intended_duration_seconds']<=25 or not 0<brief['duration_tolerance_seconds']<=3: raise ValueError('duration 12–25 s with explicit tolerance >0 and <=3 s')

def run(brief_path,concept_path=None,feedback_path=None):
    brief=read(brief_path); validate_brief(brief)
    project=ROOT/'videos/productions'/brief['slug']
    if project.exists(): raise ValueError('output exists; choose a new slug to preserve this run')
    config=backend_config()
    project.mkdir(parents=True)
    write(project/'brief.json',brief); write(project/'backend.json',config); write(project/'source-hashes.json',snapshot())
    from motif_evidence import entry_scope
    entry_scope(project, 'motif_direct.run')
    for folder in ('assets/voice','assets/sfx','renders'): (project/folder).mkdir(parents=True)
    for name in ('gsap.min.js','motion-engine.js','motion-primitives.js'): shutil.copy2(ROOT/'videos/motif-calendar-reel/assets'/name,project/'assets'/name)
    for name in ('pop','click-soft','whoosh-short'): shutil.copy2(ROOT/f'videos/motif-calendar-reel/assets/sfx/{name}.mp3',project/f'assets/sfx/{name}.mp3')
    from motif_runtime_portability import copy_cleared_font
    write(project/'font-provenance.json',copy_cleared_font(project/'assets/MotifSans.ttf'))
    write(project/'package.json',{'name':brief['slug'],'private':True,'scripts':{k:f'npx --yes hyperframes@{PIN} {v}' for k,v in [('check','check'),('render','render'),('dev','preview')]}})
    shutil.copy2(ROOT/'videos/motif-calendar-reel/hyperframes.json',project/'hyperframes.json')
    concept=None
    if concept_path:
        concept=read(concept_path)
        Draft202012Validator(read(ROOT/'schemas/creative-benchmark-concept.schema.json')).validate(concept)
        write(project/'creative-concept.json',concept)
        write(project/'creative-concept-source.json',{'file':str(concept_path),'sha256':sha(concept_path),'scope':'Preproduction concept supplied as context; not a saved executable production plan'})
    feedback=None
    if feedback_path:
        feedback=feedback_path.read_text()
        (project/'prior-render-feedback.md').write_text(feedback)
    prompt=planning_prompt(brief,concept,feedback,project)
    plan=model_call(project,'initial-plan',prompt,'schemas/production-plan.schema.json',config)
    if plan.get('quality_mode')!='motif-gold-v1': raise ValueError('new directed runs require motif-gold-v1')
    from motif_quality import direction_review
    from motif_structure import structure_review
    (project/'STORYBOARD_INITIAL.md').write_text(storyboard(plan))
    tolerance=brief['duration_tolerance_seconds']; intended=brief['intended_duration_seconds']; bounds=[intended-tolerance,intended+tolerance]
    reviews=[]
    for attempt in range(2):
        deterministic=review_plan(plan,brief)
        write(project/f'deterministic-review-{attempt}.json',deterministic)
        issues=list(deterministic['issues'])
        if not issues:
            write(project/'production-plan.json',plan)
            try:
                structure_review(project,plan,config)
                direction_review(project,plan,config)
            except ValueError as error:issues.append(str(error))
        if not issues:
            (project/'assets/voice/narration.txt').write_text(narration(plan)+'\n')
            env=os.environ.copy()
            if 'HYPERFRAMES_PYTHON' not in env:
                python=Path.home()/'.cache/motif-kokoro-venv/bin/python'
                if not python.exists(): raise ValueError('local Kokoro unavailable: set HYPERFRAMES_PYTHON')
                env['HYPERFRAMES_PYTHON']=str(python)
            print('VOICE + ALIGNMENT',flush=True)
            command(['npx','--yes',f'hyperframes@{PIN}','tts','--text-file=assets/voice/narration.txt','--voice=af_nova','--speed=0.85','--output=assets/voice/narration-af-nova.wav','--json'],project,env,project/f'tts-{attempt}.log')
            voice_duration=round(float(probe(project/'assets/voice/narration-af-nova.wav')['format']['duration']),3)
            command(['npx','--yes',f'hyperframes@{PIN}','transcribe','assets/voice/narration-af-nova.wav','--language','en','--json'],project,log=project/f'alignment-{attempt}.log')
            shutil.copy2(project/'assets/voice/narration-af-nova.wav',project/f'assets/voice/take-{attempt}.wav')
            shutil.copy2(project/'assets/voice/transcript.json',project/f'assets/voice/transcript-{attempt}.json')
            try:
                compile_plan(project,plan,read(project/'assets/voice/transcript.json'),voice_duration,bounds)
            except ValueError as error: issues.append(str(error))
        semantic=None
        # Preserve actual compiled inputs from each planning attempt before a
        # bounded correction can replace the root accepted artifacts.
        attempt_dir=project/'planning-attempts'/str(attempt)
        attempt_dir.mkdir(parents=True)
        write(attempt_dir/'plan.json',plan)
        for pattern in ('quality-structure*','quality-direction*'):
            for artifact in project.glob(pattern):
                if artifact.is_file():shutil.copyfile(artifact,attempt_dir/artifact.name)
        for filename in ('scene-events.json','action-trace.json','label-timing.json','framing-trace.json','alignment-review.json','audio-plan.json','index.html','quality-direction.json','quality-direction-record.json','quality-direction-invocation.json','quality-structure.json','quality-structure-record.json','quality-structure-invocation.json'):
            if (project/filename).exists() and not issues: shutil.copyfile(project/filename,attempt_dir/filename)
        if not issues:
            review_prompt=('Review this illustrative Motif plan against its brief and actual action timings. No tools, files, code, other agents, or web. You review data, NOT rendered frames. Check semantic fidelity, each outcome, visible evidence before labels, same-check fairness, and ending delivered. Check audience_narration: speech should explain the useful idea, choice or consequence for this audience, not narrate stage directions (dashed graphics, stencil geometry, cross rendering or test-harness timing), unless these objects are the subject. Reject unnatural production-checklist speech; let structured visual fields carry choreography. Labels are never substitutes for physical events. Use actual label-timing and explicit set/clear/keep lifecycle; reject stale labels after state changes. Headlines are scheduled after physical evidence. Narration-aligned action captions describe an unfolding action; do not treat their present tense as a completed-result headline. A completed result caption preceding evidence is an issue. Focus prose is rationale only; focus_target/framing and actual framing bounds are operative. Return schema JSON; broader semantic correctness and painted visibility are not guaranteed.\nBrief: '+json.dumps(brief)+'\nPlan: '+json.dumps(plan)+'\nAction timings: '+json.dumps(read(project/'action-trace.json'))+'\nActual labels: '+json.dumps(read(project/'label-timing.json'))+'\nActual framing: '+json.dumps(read(project/'framing-trace.json'))+'\nTimeline duration: '+str(read(project/'scene-events.json')['durationSec'])+'\nSpoken alignment: '+json.dumps(read(project/'alignment-review.json')))
            semantic=model_call(project,f'model-review-{attempt}',review_prompt,'schemas/planning-review.schema.json',config)
            if not semantic['pass'] or not all(semantic[k] for k in ('message_preserved','outcome_preserved','evidence_before_labels','ending_delivered','audience_narration')): issues+=semantic['issues'] or ['model review rejected meaning/storytelling/audience narration']
        reviews.append({'attempt':attempt,'deterministic':deterministic,'timing_or_semantic_issues':issues,'model_review':semantic})
        write(project/'planning-review.json',{'reviews':reviews,'corrections':attempt,'pass':not issues,'semantic_guarantee':False})
        if not issues: break
        if attempt==1: raise ValueError('bounded planning correction exhausted: '+'; '.join(issues))
        print('BOUNDED REPLAN: '+'; '.join(issues),flush=True)
        plan=model_call(project,'corrected-plan',prompt+'\n\nOne bounded correction. Prior plan:\n'+json.dumps(plan)+'\nFix these concrete issues without changing meaning:\n'+json.dumps(issues),'schemas/production-plan.schema.json',config)
    write(project/'production-plan.json',plan)
    (project/'STORYBOARD.md').write_text(storyboard(plan))
    anchors=read(project/'alignment-review.json')['beat_anchors']
    labels=read(project/'label-timing.json')
    caption_starts_match=all(a['start']==l['caption_start'] for a,l in zip(anchors,labels,strict=True))
    spec=read(project/'scene-events.json')
    events_sorted=all(a['time']<=b['time'] for a,b in zip(spec['events'],spec['events'][1:]))
    write(project/'pre-render-checks.json',{'scope':'Structured plan/events/alignment only; not independent encoded-frame inspection','deterministic_review_file':f'deterministic-review-{attempt}.json','model_review_file':f'model-review-{attempt}.json','planning_review_sha256':sha(project/'planning-review.json'),'event_plan_sha256':sha(project/'scene-events.json'),'checks':{'accepted_plan_state_order':deterministic['pass'],'accepted_model_data_review':semantic['pass'],'caption_starts_match_measured_beat_anchors':caption_starts_match,'event_times_sorted':events_sorted},'visual_review':'not assessed','subjective_listening':'not assessed'})
    if not caption_starts_match or not events_sorted: raise ValueError('pre-render alignment/event consistency failed')
    record=read(ROOT/'videos/motif-calendar-reel/audio-source-license-manifest.json')
    record['narration'].update(provider=f'local Kokoro ONNX through HyperFrames {PIN}',rawSha256=sha(project/'assets/voice/narration-af-nova.wav'),status='new script from live validated production plan')
    record['sfx']=[s for s in record['sfx'] if Path(s['file']).stem in ('pop','click-soft','whoosh-short')]
    record['music']={'included':False,'reason':'Narration and restrained reused paper interaction effects.'}
    write(project/'audio-source-license-manifest.json',record)
    if plan.get('quality_mode')=='motif-gold-v1':
        from motif_quality import rough, evidence_bundle, critics
        output=rough(project)
        from motif_evidence import evidence_shots
        shots=evidence_shots(read(project/'quality-bindings.json'),plan)
        evidence_bundle(project,'rough',output/'captions.mp4',output/'no-captions.mp4',shots)
        critics(project,'rough',config)
        return output/'captions.mp4'
    print('CHECK + RENDER',flush=True)
    command(['npm','run','check'],project,log=project/'check.log')
    first=project/'renders/first.mp4'
    command(['npm','run','render','--','-o',str(first),'--skill=general-video','-q','delivery'],project,log=project/'render.log')
    print('ENCODED FINISHING',flush=True)
    final=finish(project,first,bounds)
    if snapshot()!=read(project/'source-hashes.json'): raise ValueError('shared source changed during production')
    write(project/'run-record.json',{'planning_backend':config,'initial_plan_sha256':sha(project/'initial-plan.json'),'production_plan_sha256':sha(project/'production-plan.json'),'input_brief_sha256':sha(project/'brief.json'),'shared_source_unchanged':True,'manual_per_run_edits':[],'duration_range':bounds,'final':str(final.relative_to(ROOT))})
    return final

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['run','validate','capabilities','script-plan','script-preview'])
    parser.add_argument('--brief',type=Path)
    parser.add_argument('--plan',type=Path)
    parser.add_argument('--project',type=Path,help='Saved supplied-script project; preview does not replan or regenerate narration')
    parser.add_argument('--render',action='store_true',help='Render the requested moving preview from saved inputs')
    parser.add_argument('--concept',type=Path,help='Optional recorded creative preproduction concept; not an executable plan')
    parser.add_argument('--feedback',type=Path,help='Optional review of a preserved prior render, supplied to live planning')
    args=parser.parse_args()
    try:
        if args.action=='capabilities':
            from motif_paper_investigation import KINDS
            from motif_script import SCRIPT_ASSETS
            from motif_paper_energy import STAGES
            from motif_ui_actions import KINDS as UI_KINDS
            print(json.dumps({'text_directed_ui':{'schema':'text-directed-1.0','style':'reference-expressive-high-energy-v1','actions':list(UI_KINDS),'components_module':'scripts/motif_ui_components.py','scope':'finite interactive UI reconstruction; agent-authored geometry/choreography'},'worlds':WORLD_SHOTS,'assets':WORLD_ASSETS,'backend':'codex-exec','style':'locked motif-v1','voice':'local Kokoro af_nova','script_preview':{'style':'reference-expressive-v1','actions':list(KINDS),'assets':SCRIPT_ASSETS,'scope':'finite paper investigation; new geometry requires explicit agent-assisted development','high_energy':{'style':'reference-expressive-high-energy-v1','actions':STAGES,'scope':'finite agent-authored overlapping paper actions; explicit opt-in'}}},default=list,indent=2))
        elif args.action=='script-plan':
            from motif_script import plan_script
            if not args.brief: raise ValueError('script-plan requires --brief')
            print('REVIEW_REQUIRED '+str(plan_script(args.brief.resolve())))
        elif args.action=='script-preview':
            from motif_script import align_voice, render_preview
            if not args.project: raise ValueError('script-preview requires --project')
            project=args.project.resolve()
            from motif_evidence import require_scope
            require_scope(project)
            plan=read(project/'production-plan.json'); brief=read(project/'brief.json')
            report=review_plan(plan,brief)
            if not report['pass']: raise ValueError('; '.join(report['issues']))
            if not (project/'review-state.json').exists():
                if (project/'speech-timing.json').exists():
                    speech=read(project/'speech-timing.json'); words=speech['words']; duration=speech['duration']
                else: words,duration=align_voice(project)
                compile_plan(project,plan,words,duration,None)
            if args.render: print('REVIEW_REQUIRED '+str(render_preview(project)))
            else: print('REVIEW_REQUIRED '+str(project/'index.html'))
        elif args.action=='validate':
            if not args.plan or not args.brief: raise ValueError('validate requires --plan and --brief')
            report=review_plan(read(args.plan),read(args.brief)); print(json.dumps(report,indent=2))
            if not report['pass']: sys.exit(2)
        else:
            if not args.brief: raise ValueError('run requires --brief')
            print('REVIEW_REQUIRED '+str(run(args.brief.resolve(),args.concept.resolve() if args.concept else None,args.feedback.resolve() if args.feedback else None)),flush=True)
    except (ValueError,RuntimeError,subprocess.TimeoutExpired) as error:
        print(json.dumps({'status':'capability_or_production_error','reason':str(error)}),file=sys.stderr); sys.exit(2)
