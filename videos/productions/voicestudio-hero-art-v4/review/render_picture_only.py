"""Native moving inspection with the caption host removed; same finite film."""
from pathlib import Path
import re,shutil,subprocess
p=Path(__file__).resolve().parents[1];native=p;q=p/'review/picture-only-final-project';q.mkdir(exist_ok=True)
if not (q/'assets').exists():(q/'assets').symlink_to(native/'assets',target_is_directory=True)
shutil.copytree(native/'compositions',q/'compositions',dirs_exist_ok=True)
for f in (q/'compositions').glob('*.html'):f.write_text(f.read_text().replace('data-width="1080"','data-width="360"').replace('data-height="1920"','data-height="640"'))
html=(native/'index.html').read_text().replace('data-width="1080"','data-width="360"').replace('data-height="1920"','data-height="640"')
html=re.sub(r'<div id="host-captions"[^>]*></div>','',html)
assert 'id="host-captions"' not in html
html=re.sub(r'<audio[^>]*>.*?</audio>','',html)
(q/'index.html').write_text(html)
shutil.copy2(native/'hyperframes.json',q/'hyperframes.json')
subprocess.run(['npx','--yes','hyperframes@0.8.99','render',str(q),'--output',str(p/'review/picture-only-raw.mp4'),'--quality','looks','--workers','1','--experimental-fast-capture=false'],check=True)
print('picture-only raw capture complete; mux final audio after full/native export')
