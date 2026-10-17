// Render the 3D experiment headless: stills, a 2D-vs-3D comparison and short orbit clips.
//   node render.mjs OUT_DIR [scene ...] [--modes card,puffy] [--clip SECONDS] [--fps N]
import { chromium } from 'playwright-core';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '../..');
const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); if (i < 0) return d; const v = args[i + 1]; args.splice(i, 2); return v; };
const modes = opt('--modes', 'card,puffy').split(',');
const clip = parseFloat(opt('--clip', '0'));
const fps = parseInt(opt('--fps', '24'), 10);
const OUT = path.resolve(args.shift() || 'out');
const scenes = args.length ? args : fs.readdirSync(path.join(HERE, 'scenes')).filter((f) => f.endsWith('.json')).map((f) => f.slice(0, -5));
fs.mkdirSync(OUT, { recursive: true });

const MOUNTS = { '/three/': path.join(HERE, 'node_modules/three/'), '/fonts/': path.join(ROOT, 'assets/fonts/'), '/': HERE + '/' };
const TYPES = { '.js': 'text/javascript', '.mjs': 'text/javascript', '.html': 'text/html', '.json': 'application/json', '.woff2': 'font/woff2' };
const server = http.createServer((req, res) => {
  const url = decodeURIComponent(req.url.split('?')[0]);
  const prefix = Object.keys(MOUNTS).find((p) => url.startsWith(p));
  const file = path.join(MOUNTS[prefix], url.slice(prefix.length));
  if (!file.startsWith(MOUNTS[prefix]) || !fs.existsSync(file)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'content-type': TYPES[path.extname(file)] || 'application/octet-stream' });
  fs.createReadStream(file).pipe(res);
});
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const base = `http://127.0.0.1:${server.address().port}`;

const browser = await chromium.launch({
  executablePath: process.env.CHROMIUM || '/opt/pw-browsers/chromium',
  args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'],
});

async function flat2d(spec, file) {
  // The same layers drawn flat, exactly as the 2D pipeline composes them.
  const [W, H] = spec.size, out = spec.kind === 'set' ? [720, 1280] : [1080, 1080];
  const page = await browser.newPage({ viewport: { width: out[0], height: out[1] } });
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${out[0]}" height="${out[1]}" viewBox="0 0 ${W} ${H}">` +
    (spec.kind === 'set' ? '' : `<rect width="${W}" height="${H}" fill="#E8D9BF"/>`) + spec.layers.map((l) => l.svg).join('') + '</svg>';
  await page.setContent(`<style>@font-face{font-family:Inter;src:url('${base}/fonts/Inter-900-latin.woff2');font-weight:100 900}body{margin:0}</style>${svg}`);
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: file }); await page.close();
}

const report = [];
for (const name of scenes) {
  const spec = JSON.parse(fs.readFileSync(path.join(HERE, 'scenes', `${name}.json`)));
  await flat2d(spec, path.join(OUT, `${name}-2d.png`));
  for (const mode of modes) {
    const page = await browser.newPage({ viewport: spec.kind === 'set' ? { width: 720, height: 1280 } : { width: 1080, height: 1080 } });
    page.on('pageerror', (e) => console.error(name, mode, e.message));
    const t0 = Date.now();
    await page.goto(`${base}/stage.html?scene=${name}&mode=${mode}`);
    await page.waitForFunction(() => window.ready || window.failed, null, { timeout: 600000 });
    const failed = await page.evaluate(() => window.failed);
    if (failed) throw new Error(`${name}/${mode}: ${failed}`);
    const info = await page.evaluate(() => ({ layers: window.stage.layers, meshes: window.stage.meshes }));
    const canvas = await page.$('canvas');
    const swing = spec.kind === 'set' ? 12 : 24;
    const shots = { front: [0, 0], left: [-swing, 5], right: [swing, 5] };
    for (const [label, [yaw, pitch]] of Object.entries(shots)) {
      await page.evaluate(([a, b]) => window.stage.frame(a, b), [yaw, pitch]);
      await canvas.screenshot({ path: path.join(OUT, `${name}-${mode}-${label}.png`) });
    }
    if (clip > 0) {
      const dir = path.join(OUT, `${name}-${mode}-frames`); fs.mkdirSync(dir, { recursive: true });
      const n = Math.round(clip * fps);
      for (let i = 0; i < n; i++) {
        const t = i / n, yaw = swing * Math.sin(t * Math.PI * 2), pitch = 3 + 3 * Math.sin(t * Math.PI * 4);
        // The machine acts 0.6 s in, at its own frame rate, then holds its end state.
        const k = Math.round((i / fps - 0.6) * 30);
        await page.evaluate(([a, b, f]) => { window.stage.setFrame(f); window.stage.frame(a, b, 1); }, [yaw, pitch, k]);
        await canvas.screenshot({ path: path.join(dir, `f${String(i).padStart(4, '0')}.png`) });
      }
      execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', String(fps), '-i', path.join(dir, 'f%04d.png'),
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', path.join(OUT, `${name}-${mode}-orbit.mp4`)]);
      fs.rmSync(dir, { recursive: true });
    }
    report.push({ scene: name, mode, ...info, seconds: Math.round((Date.now() - t0) / 1000) });
    console.log(name, mode, info.meshes, 'meshes', Math.round((Date.now() - t0) / 1000), 's');
    await page.close();
  }
}
fs.writeFileSync(path.join(OUT, 'report.json'), JSON.stringify(report, null, 1) + '\n');
await browser.close(); server.close();
