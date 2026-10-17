// Motif 3D experiment: turn the library's own 2D SVG art into lit 3D paper.
//
// Every filled shape becomes an extruded card (or a puffed, bevelled shape),
// every stroke becomes a round tube, text becomes a printed decal on its card.
// Draw order becomes depth, and each set layer (room, props, rig, host) gets
// its own plane, so the 2D composition is kept exactly when seen head on.
import * as THREE from 'three';
import { SVGLoader } from 'three/addons/loaders/SVGLoader.js';

const q = new URLSearchParams(location.search);
const MODE = q.get('mode') || 'card';          // card | puffy
const STYLE = {
  card:  { depth: 2.2, bevel: 0.7, gap: 1.0, tube: 1.0, layerGap: 45 },
  puffy: { depth: 3.0, bevel: 14,  gap: 2.6, tube: 1.0, layerGap: 55 },
}[MODE];

const loader = new SVGLoader();
const SKIP_PARENTS = 'defs,clipPath,pattern,mask,symbol,linearGradient,radialGradient,filter';

// --- paper grain: Motif's own procedural fibre texture -----------------------
function paperTexture() {
  const c = document.createElement('canvas'); c.width = c.height = 512;
  const g = c.getContext('2d'); g.fillStyle = '#fff'; g.fillRect(0, 0, 512, 512);
  let s = 7; const rnd = () => (s = (s * 16807) % 2147483647) / 2147483647;
  for (let i = 0; i < 9000; i++) {
    const v = 225 + rnd() * 30 | 0; g.fillStyle = `rgba(${v},${v - 4},${v - 10},${0.25 + rnd() * 0.3})`;
    g.fillRect(rnd() * 512, rnd() * 512, 1 + rnd() * 2, 1 + rnd() * 2);
  }
  for (let i = 0; i < 400; i++) {
    g.strokeStyle = `rgba(150,130,110,${0.05 + rnd() * 0.08})`; g.lineWidth = 0.6;
    const x = rnd() * 512, y = rnd() * 512, a = rnd() * Math.PI;
    g.beginPath(); g.moveTo(x, y); g.lineTo(x + Math.cos(a) * 9, y + Math.sin(a) * 9); g.stroke();
  }
  const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.repeat.set(1 / 260, 1 / 260); t.colorSpace = THREE.SRGBColorSpace; return t;
}
const PAPER = paperTexture();
const matCache = new Map();
function material(color, opacity = 1) {
  const key = color + opacity;
  if (!matCache.has(key)) {
    const m = new THREE.MeshStandardMaterial({ color: new THREE.Color().setStyle(color), roughness: 0.92, metalness: 0,
      map: PAPER, transparent: opacity < 1, opacity, depthWrite: opacity >= 1, side: THREE.DoubleSide });
    matCache.set(key, m);
  }
  return matCache.get(key);
}

// --- SVG DOM walk ------------------------------------------------------------
function mount(svgText, w, h) {
  const holder = document.createElement('div');
  holder.style.cssText = `position:absolute;left:0;top:0;width:${w}px;height:${h}px;opacity:0;pointer-events:none`;
  holder.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">${svgText}</svg>`;
  document.body.appendChild(holder);
  return holder;
}

function shapeD(el) {
  const n = (a) => parseFloat(el.getAttribute(a) || 0);
  switch (el.tagName) {
    case 'path': return el.getAttribute('d');
    case 'rect': {
      const x = n('x'), y = n('y'), w = n('width'), h = n('height');
      let rx = el.hasAttribute('rx') ? n('rx') : n('ry'), ry = el.hasAttribute('ry') ? n('ry') : rx;
      rx = Math.min(rx, w / 2); ry = Math.min(ry, h / 2);
      if (!rx) return `M${x} ${y}H${x + w}V${y + h}H${x}Z`;
      return `M${x + rx} ${y}H${x + w - rx}A${rx} ${ry} 0 0 1 ${x + w} ${y + ry}V${y + h - ry}A${rx} ${ry} 0 0 1 ${x + w - rx} ${y + h}` +
             `H${x + rx}A${rx} ${ry} 0 0 1 ${x} ${y + h - ry}V${y + ry}A${rx} ${ry} 0 0 1 ${x + rx} ${y}Z`;
    }
    case 'circle': case 'ellipse': {
      const cx = n('cx'), cy = n('cy'), rx = el.tagName === 'circle' ? n('r') : n('rx'), ry = el.tagName === 'circle' ? n('r') : n('ry');
      return `M${cx - rx} ${cy}A${rx} ${ry} 0 1 0 ${cx + rx} ${cy}A${rx} ${ry} 0 1 0 ${cx - rx} ${cy}Z`;
    }
    case 'line': return `M${n('x1')} ${n('y1')}L${n('x2')} ${n('y2')}`;
    case 'polyline': case 'polygon': {
      const p = (el.getAttribute('points') || '').trim().split(/[\s,]+/).map(Number);
      let d = ''; for (let i = 0; i + 1 < p.length; i += 2) d += (i ? 'L' : 'M') + p[i] + ' ' + p[i + 1];
      return d + (el.tagName === 'polygon' ? 'Z' : '');
    }
  }
  return null;
}

// Drop-shadow and edge copies (same path, nudged, translucent) are 2D fakes of
// depth; real thickness and real shadows replace them in 3D.
function isFakeDepth(el, opacity) {
  if (opacity > 0.7 || !/^\s*translate/.test(el.getAttribute('transform') || '')) return false;
  for (let s = el.nextElementSibling; s; s = s.nextElementSibling) {
    if (s.tagName === el.tagName && s.getAttribute('d') === el.getAttribute('d') && !s.getAttribute('transform')) return true;
  }
  return false;
}

function cumulativeOpacity(el, root) {
  let op = 1;
  for (let n = el; n && n !== root; n = n.parentElement) {
    const cs = getComputedStyle(n);
    op *= parseFloat(cs.opacity || 1);
  }
  return op;
}

function parsePath(d, m, fillRule) {
  const doc = `<svg xmlns="http://www.w3.org/2000/svg"><path d="${d}" fill-rule="${fillRule}" ` +
              `transform="matrix(${m.a} ${m.b} ${m.c} ${m.d} ${m.e} ${m.f})"/></svg>`;
  return loader.parse(doc).paths[0];
}

// --- builders ----------------------------------------------------------------
function fillMesh(shapePath, color, opacity, z, unit) {
  const shapes = SVGLoader.createShapes(shapePath);
  if (!shapes.length) return null;
  const box = new THREE.Box2();
  for (const s of shapes) for (const p of s.getPoints()) box.expandByPoint(p);
  const size = box.getSize(new THREE.Vector2()), minDim = Math.min(size.x, size.y);
  if (minDim < 0.3) return null;
  let geo;
  if (opacity < 0.98) {
    geo = new THREE.ShapeGeometry(shapes, 16); geo.translate(0, 0, z + STYLE.depth * unit + 0.05);
  } else {
    const bevel = Math.min(STYLE.bevel * unit, minDim * (MODE === 'puffy' ? 0.32 : 0.2));
    geo = new THREE.ExtrudeGeometry(shapes, {
      depth: STYLE.depth * unit, curveSegments: 20, bevelEnabled: bevel > 0.05,
      bevelThickness: MODE === 'puffy' ? bevel * 0.9 : bevel, bevelSize: bevel * (MODE === 'puffy' ? 0.7 : 0.6),
      bevelOffset: -bevel * (MODE === 'puffy' ? 0.7 : 0.6), bevelSegments: MODE === 'puffy' ? 6 : 2,
    });
    geo.translate(0, 0, z);
  }
  const mesh = new THREE.Mesh(geo, material(color, opacity));
  mesh.castShadow = opacity >= 0.98; mesh.receiveShadow = true;
  return mesh;
}

function strokeMeshes(shapePath, color, opacity, width, cap, z, unit) {
  const out = [];
  const r = Math.max(0.4, width / 2);
  const mat = material(color, opacity);
  for (const sub of shapePath.subPaths) {
    const len = sub.getLength();
    if (!(len > 0.5)) continue;
    const n = Math.max(4, Math.min(220, Math.round(len / 3)));
    const pts2 = sub.getSpacedPoints(n);
    const closed = pts2[0].distanceTo(pts2[pts2.length - 1]) < 0.5;
    if (closed) pts2.pop();
    const zc = z + STYLE.depth * unit * 0.5 + (opacity < 0.98 ? STYLE.depth * unit : 0);
    const pts = pts2.map((p) => new THREE.Vector3(p.x, p.y, zc));
    if (pts.length < 2) continue;
    const curve = new THREE.CatmullRomCurve3(pts, closed, 'centripetal');
    // Thin lines stay flat-ish on the card; wide strokes (limbs) become round.
    const geo = new THREE.TubeGeometry(curve, Math.min(400, pts.length * 2), r, r > 6 ? 18 : 8, closed);
    const mesh = new THREE.Mesh(geo, mat); mesh.castShadow = opacity >= 0.98; mesh.receiveShadow = true;
    if (r > 6) mesh.scale.z = 1;  // keep limbs round
    out.push(mesh);
    if (!closed && cap !== 'butt') {
      for (const p of [pts[0], pts[pts.length - 1]]) {
        const s = new THREE.Mesh(new THREE.SphereGeometry(r, 18, 12), mat);
        s.position.copy(p); s.castShadow = mesh.castShadow; s.receiveShadow = true; out.push(s);
      }
    }
  }
  return out;
}

function textMesh(el, cs, opacity, z, unit) {
  const rect = el.getBoundingClientRect();
  if (rect.width < 1 || rect.height < 1) return null;
  const pad = 6, k = 3;
  const x0 = Math.floor(rect.left - pad), y0 = Math.floor(rect.top - pad);
  const w = Math.ceil(rect.width + 2 * pad), h = Math.ceil(rect.height + 2 * pad);
  const c = document.createElement('canvas'); c.width = w * k; c.height = h * k;
  const g = c.getContext('2d'); const m = el.getCTM();
  g.setTransform(k * m.a, k * m.b, k * m.c, k * m.d, k * (m.e - x0), k * (m.f - y0));
  g.font = `${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
  if ('letterSpacing' in g && cs.letterSpacing !== 'normal') g.letterSpacing = cs.letterSpacing;
  const anchor = el.getAttribute('text-anchor') || cs.textAnchor;
  g.textAlign = anchor === 'middle' ? 'center' : anchor === 'end' ? 'right' : 'left';
  g.fillStyle = cs.fill;
  g.fillText(el.textContent, parseFloat(el.getAttribute('x') || 0), parseFloat(el.getAttribute('y') || 0));
  const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 4;
  const mat = new THREE.MeshStandardMaterial({ map: tex, transparent: true, opacity, roughness: 0.9, depthWrite: false });
  const mesh = new THREE.Mesh(new THREE.PlaneGeometry(w, h), mat);
  mesh.position.set(x0 + w / 2, y0 + h / 2, z + STYLE.depth * unit + 0.3 * unit);
  mesh.scale.y = -1;  // world is flipped back to y-up at the root
  mesh.receiveShadow = true;
  return mesh;
}

// --- one SVG layer -> THREE.Group ---------------------------------------------
// Each shape rests on whatever earlier shapes it overlaps (a height map built in
// draw order), so small pieces sit on the bulge of big ones instead of sinking in.
function buildLayer(svgText, w, h, zBase, unit) {
  const holder = mount(svgText, w, h);
  const root = holder.firstElementChild;
  const group = new THREE.Group();
  const placed = [];
  let front = zBase, count = 0;
  for (const el of root.querySelectorAll('path,rect,circle,ellipse,line,polyline,polygon,text')) {
    if (el.closest(SKIP_PARENTS)) continue;
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    const op = cumulativeOpacity(el, root);
    if (op < 0.02 || (el.tagName !== 'text' && isFakeDepth(el, op))) continue;
    const r = el.getBoundingClientRect(), pad = parseFloat(cs.strokeWidth || 0) / 2;
    const box = { x0: r.left - pad, y0: r.top - pad, x1: r.right + pad, y1: r.bottom + pad };
    let z = zBase;
    for (const p of placed) {
      if (box.x0 < p.box.x1 && box.x1 > p.box.x0 && box.y0 < p.box.y1 && box.y1 > p.box.y0) {
        // Text is printed on the top surface; shapes sink a little into a puffed shape below.
        const sink = el.tagName === 'text' || MODE !== 'puffy' ? 0 : 0.3;
        z = Math.max(z, p.front - (p.front - p.z) * sink + STYLE.gap * unit * 0.25);
      }
    }
    const meshes = [];
    if (el.tagName === 'text') {
      const t = textMesh(el, cs, op, z - STYLE.depth * unit, unit); if (t) meshes.push(t);
    } else {
      const d = shapeD(el); if (!d) continue;
      const m = el.getCTM();
      const fill = cs.fill, stroke = cs.stroke;
      let sp = null;
      const fillOp = op * parseFloat(cs.fillOpacity || 1), strokeOp = op * parseFloat(cs.strokeOpacity || 1);
      if (fill && fill !== 'none' && !fill.startsWith('url') && el.tagName !== 'line' && el.tagName !== 'polyline') {
        sp = parsePath(d, m, cs.fillRule);
        const mesh = sp && fillMesh(sp, fill, fillOp, z, unit); if (mesh) meshes.push(mesh);
      }
      const sw = parseFloat(cs.strokeWidth || 0) * Math.sqrt(Math.abs(m.a * m.d - m.b * m.c));
      if (stroke && stroke !== 'none' && !stroke.startsWith('url') && sw > 0.3) {
        sp = sp || parsePath(d, m, cs.fillRule);
        meshes.push(...strokeMeshes(sp, stroke, strokeOp, sw, cs.strokeLinecap, z, unit));
      }
    }
    if (!meshes.length) continue;
    const b = new THREE.Box3(); for (const mesh of meshes) { b.expandByObject(mesh); group.add(mesh); }
    // Translucent decals and text add no height: later shapes should not climb onto them.
    const solid = meshes.some((mesh) => mesh.castShadow);
    placed.push({ box, z, front: solid ? b.max.z : z });
    front = Math.max(front, b.max.z); count++;
  }
  holder.remove();
  return { group, count, front };
}

// --- diorama floor ---------------------------------------------------------------
// The room is drawn as one flat picture: wall above floor_y, floor below. Every
// piece that lies wholly below floor_y is folded down onto a horizontal floor and
// stretched forward under the props, machine and host, so they stand on it.
function foldFloor(world, room, floorY, H, depthTotal) {
  const below = [];
  for (const mesh of room.children) {
    const b = new THREE.Box3().setFromObject(mesh);
    if (b.min.y >= floorY - 2) below.push(mesh);
  }
  const stretch = Math.max(1, (depthTotal + 120) / (H - floorY));
  const outer = new THREE.Group(); outer.scale.z = stretch;
  const hinge = new THREE.Group(); hinge.position.y = floorY; hinge.rotation.x = Math.PI / 2;
  const inner = new THREE.Group(); inner.position.y = -floorY;
  for (const mesh of below) { room.remove(mesh); inner.add(mesh); }
  hinge.add(inner); outer.add(hinge); world.add(outer);
  return below.length;
}

// --- stage --------------------------------------------------------------------
export async function build(name) {
  await document.fonts.load('900 30px Inter'); await document.fonts.load('800 30px Inter');
  const spec = await (await fetch(`scenes/${name}.json`)).json();
  const [W, H] = spec.size; const unit = W / 720;
  const isSet = spec.kind === 'set';
  const out = isSet ? [720, 1280] : [1080, 1080];

  const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1); renderer.setSize(out[0], out[1]);
  renderer.outputColorSpace = THREE.SRGBColorSpace; renderer.toneMapping = THREE.NoToneMapping;
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  document.body.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  const world = new THREE.Group(); world.scale.y = -1; world.position.set(-W / 2, H / 2, 0); scene.add(world);

  let z = 0, layers = [];
  for (const layer of spec.layers) {
    const { group, count, front } = buildLayer(layer.svg, W, H, z, unit);
    world.add(group); layers.push({ name: layer.name, count, z, front: Math.round(front), group, frames: layer.frames });
    z = front + STYLE.layerGap * unit;
  }
  const depthTotal = z;
  const fov = 24;
  const fit = isSet ? H : H * 0.98;
  const D = (fit / 2) / Math.tan(THREE.MathUtils.degToRad(fov / 2));
  if (isSet && spec.floor_y) {
    const room = layers[0].group, fy = spec.floor_y;
    const wallColor = room.children[0].material.color.clone();
    foldFloor(world, room, fy, H, depthTotal);
    // Perspective would blow up the nearer layers; scale each about its foot point so
    // head on it keeps the 2D composition's sizes while still standing on the floor.
    for (const l of layers.slice(1)) {
      const s = (D - l.z) / D;
      l.place = (g) => { g.scale.set(s, s, 1); g.position.set(W / 2 * (1 - s), fy * (1 - s), 0); };
      l.place(l.group);
    }
    // Paper sweep around the room so an orbit never sees past the set's edges.
    const floorMesh = world.children.at(-1).getObjectByProperty('isMesh', true);
    const floorColor = floorMesh ? floorMesh.material.color.clone() : wallColor.clone().multiplyScalar(0.7);
    const sweep = (color, w, h) => new THREE.Mesh(new THREE.PlaneGeometry(w, h),
      new THREE.MeshStandardMaterial({ color, roughness: 0.95, map: PAPER, side: THREE.DoubleSide }));
    const wall = sweep(wallColor, W * 4, H * 3); wall.position.set(W / 2, H / 2, -2); wall.receiveShadow = true;
    const floor = sweep(floorColor, W * 4, depthTotal * 4); floor.rotation.x = Math.PI / 2;
    floor.position.set(W / 2, fy + 1, depthTotal * 2); floor.receiveShadow = true;
    world.add(wall, floor);
  }
  // Animated layers (a rig's action) are rebuilt from the library's own frame SVGs.
  function setFrame(i) {
    for (const l of layers) {
      if (!l.frames) continue;
      const k = Math.max(0, Math.min(l.frames.length - 1, i));
      if (k === (l.shown || 0)) continue;
      const { group } = buildLayer(l.frames[k], W, H, l.z, unit);
      if (l.place) l.place(group);
      world.remove(l.group);
      l.group.traverse((o) => { if (o.isMesh) { o.geometry.dispose(); if (o.material.map && o.material.map !== PAPER) { o.material.map.dispose(); o.material.dispose(); } } });
      world.add(group); l.group = group; l.shown = k;
    }
  }
  const info = layers.map(({ name, count, z, front, frames }) => ({ name, count, z: Math.round(z), front, frames: frames ? frames.length : 0 }));

  if (!isSet) {  // a plain paper backdrop and floor for a lone character
    const wall = new THREE.Mesh(new THREE.PlaneGeometry(W * 4, H * 4), material('#E8D9BF'));
    wall.position.z = -60 * unit; wall.receiveShadow = true; scene.add(wall);
    const floor = new THREE.Mesh(new THREE.PlaneGeometry(W * 4, W * 4), material('#CDB993'));
    floor.rotation.x = -Math.PI / 2; floor.position.y = H / 2 - 905; floor.receiveShadow = true; scene.add(floor);
  }

  scene.add(new THREE.HemisphereLight(0xfff6e8, 0xb8a58c, 2.1));
  const key = new THREE.DirectionalLight(0xfff1dc, 1.5);
  key.castShadow = true; key.shadow.mapSize.set(2048, 2048); key.shadow.bias = -0.0004; key.shadow.normalBias = 0.6;
  const sc = key.shadow.camera; sc.left = -W; sc.right = W; sc.top = H; sc.bottom = -H; sc.near = 1; sc.far = 6000;
  key.shadow.radius = 4;
  scene.add(key); scene.add(key.target);
  key.position.set(-W * 0.55, H * 0.6, 1800); key.target.position.set(0, 0, depthTotal * 0.3);

  const camera = new THREE.PerspectiveCamera(fov, out[0] / out[1], 1, 20000);
  const pivot = new THREE.Vector3(0, 0, isSet ? depthTotal * 0.55 : depthTotal * 0.5);

  function frame(yaw = 0, pitch = 0, dolly = 1) {
    const y = THREE.MathUtils.degToRad(yaw), p = THREE.MathUtils.degToRad(pitch);
    const dist = (D - pivot.z) * dolly;
    camera.position.set(pivot.x + Math.sin(y) * Math.cos(p) * dist, pivot.y + Math.sin(p) * dist, pivot.z + Math.cos(y) * Math.cos(p) * dist);
    camera.lookAt(pivot);
    renderer.render(scene, camera);
  }
  frame();
  let meshes = 0; scene.traverse((o) => { if (o.isMesh) meshes++; });
  const fps = (spec.layers.find((l) => l.frames) || {}).fps || 30;
  return { frame, setFrame, layers: info, meshes, size: out, fps };
}
