"""Small text, resource and observation contracts for bounded scene adapters."""
import math
import unicodedata
import wave
from pathlib import Path
from motif_evidence import read,sha


def locked_resource(root, record):
    path=Path(record.get('path',''))
    if path.is_absolute() or '..' in path.parts or not path.parts:
        raise ValueError('resource path must be relative to the declared project')
    base=Path(root).resolve()
    path=(base/path).resolve()
    if not path.is_relative_to(base):raise ValueError('resource escapes declared project root')
    if not path.is_file() or sha(path)!=record.get('sha256'):
        raise ValueError('declared resource missing or changed: '+str(path))
    return path


def native_text(root, label):
    """Real glyph geometry; no browser/system font substitution or auto wraps."""
    from fontTools.ttLib import TTFont
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.boundsPen import BoundsPen
    from html import escape
    font=locked_resource(root,label['font'])
    locked_resource(root,label['license'])
    size=label['size'];x,y=label['position'];bounds=label['bounds']
    if len(bounds)!=4:raise ValueError('four text bounds required')
    if any(type(v) not in (int,float) or not math.isfinite(v) for v in (size,x,y,*bounds)) or size<=0:
        raise ValueError('finite text geometry required')
    if not 0<=bounds[0]<bounds[2]<=360 or not 0<=bounds[1]<bounds[3]<=640:
        raise ValueError('text bounds outside native phone canvas')
    text=label['text'];lines=label['lines']
    if not isinstance(text,str) or not text.strip() or not lines or '\n'.join(lines)!=text:
        raise ValueError('exact text and locked line breaks required')
    if label.get('text_policy')!='simple-ltr-unshaped-v1' or not label.get('language'):
        raise ValueError('explicit simple LTR text policy and language required')
    if any(unicodedata.combining(c) or unicodedata.bidirectional(c) in ('R','AL','AN') or c in '\u200c\u200d' for c in text):
        raise ValueError('text needs shaping/bidi adapter; unsupported by this fixture')
    with TTFont(font) as face:
        if type(label.get('weight')) is not int or label['weight']!=face['OS/2'].usWeightClass:
            raise ValueError('locked text weight differs from font file')
        glyphs=face.getGlyphSet();cmap=face.getBestCmap();scale=size/face['head'].unitsPerEm
        markup=[];widths=[];painted=[]
        for n,line in enumerate(lines):
            cursor=x
            for character in line:
                name=cmap.get(ord(character))
                if name is None:raise ValueError('missing glyph: '+character)
                pen=SVGPathPen(glyphs);glyphs[name].draw(pen)
                box=BoundsPen(glyphs);glyphs[name].draw(box)
                if box.bounds:
                    left,bottom,right,top=box.bounds;baseline=y+n*size*1.3
                    painted.append((cursor+left*scale,baseline-top*scale,cursor+right*scale,baseline-bottom*scale))
                markup.append(f'<path d="{pen.getCommands()}" transform="translate({cursor} {y+n*size*1.3}) scale({scale} {-scale})"/>')
                cursor+=face['hmtx'].metrics[name][0]*scale
            widths.append(cursor-x)
    if not painted or any(a<bounds[0] or b<bounds[1] or c>bounds[2] or d>bounds[3] for a,b,c,d in painted):
        raise ValueError('locked text does not fit declared bounds')
    return '<g aria-label="'+escape(text,quote=True)+'">'+''.join(markup)+'</g>',widths


def reference_observation_scope(packet, required_frames):
    """Metadata only; never opens the media or invents unseen in-between motion."""
    observed=packet.get('observed_frames',[])
    if any(type(n) is not int or n<0 for n in observed) or len(set(observed))!=len(observed):
        raise ValueError('distinct observed frame indices required')
    import re
    if not re.fullmatch(r'[0-9a-f]{64}',packet.get('source_sha256','')) or not packet.get('authorization'):
        raise ValueError('authorized source identity required')
    requested=packet.get('requested_mode')
    native=packet.get('native_element_ids',[])
    if requested=='faithful-editable' and (not native or packet.get('raster_only') is not False):
        raise ValueError('faithful-editable requires native elements, not a flattened animatic')
    full=set(required_frames).issubset(observed)
    return {'motion_fidelity':'COVERAGE_PRESENT_REVIEW_REQUIRED' if full else 'UNASSESSED',
            'unobserved_required_frames':sorted(set(required_frames)-set(observed)),
            'source_fidelity':'UNASSESSED','editability':'NATIVE_DATA_DECLARED_REVIEW_REQUIRED' if native else 'UNASSESSED'}


def resource_inventory(root, records):
    paths=[locked_resource(root,r) for r in records]
    return {'resources':[{'path':r['path'],'sha256':sha(p)} for r,p in zip(records,paths)],
            'hidden_path_fallbacks':False,'cross_platform_rebuild':'UNASSESSED'}


def saved_audio(root, scene):
    """Optional saved PCM mix, with integer samples authoritative at 30fps.

    This checks media identity/duration only, never listening or speech quality.
    """
    packet=scene.get('audio')
    if packet is None:return {'status':'SILENT_FIXTURE','listening_av':'UNASSESSED'}
    if packet.get('role') not in ('synthetic-tone','saved-narration-mix'):
        raise ValueError('explicit saved audio role required')
    path=locked_resource(root,packet['resource'])
    expected=scene['frames']*1600
    if type(packet.get('sample_frames')) is not int or packet['sample_frames']!=expected or packet.get('sample_rate')!=48000:
        raise ValueError('30fps/48000Hz integer sample authority conflicts')
    with wave.open(str(path),'rb') as track:
        if (track.getframerate()!=48000 or track.getnframes()!=expected or
                track.getnchannels() not in (1,2) or track.getsampwidth()!=2 or track.getcomptype()!='NONE'):
            raise ValueError('saved PCM mix differs from declared sample contract')
        channels=track.getnchannels()
        if len(track.readframes(expected+1))!=expected*channels*2:
            raise ValueError('saved PCM payload is truncated or differs from sample contract')
    return {'status':'SAVED_PCM_BOUND','resource':packet['resource'],'sample_rate':48000,
            'sample_frames':expected,'channels':channels,'listening_av':'UNASSESSED'}
