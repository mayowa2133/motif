/* Run with a project-local PixiJS package path; no GPU, downloads or global install. */
const assert=require('node:assert/strict');
const {Container}=require(process.argv[2]||'pixi.js');
const {reparentWithFreshTransform}=require('../assets/runtime/motif-pixi-owner.js');
const keys=['a','b','c','d','tx','ty'];
function fixture(f){
 const stage=new Container();
 const a=new Container({x:130+f*2,y:75-f,rotation:.19+f*.007,scale:{x:1.3,y:.81}});
 const b=new Container({x:370-f,y:220+f,rotation:-.27-f*.003,scale:{x:.72,y:1.8}});
 const child=new Container({x:31+f*.6,y:19-f*.2,rotation:.33,scale:{x:1.14,y:.78}});
 stage.addChild(a,b);a.addChild(child);return {a,b,child};
}
// A real failing control: cached-world transfer before the render refreshes caches.
{
 const {b,child}=fixture(7),before=child.getGlobalTransform();b.reparentChild(child);
 const after=child.getGlobalTransform();
 assert(keys.some(k=>Math.abs(before[k]-after[k])>1),'Expected cached-transfer counterexample');
}
let checks=0,maxDelta=0;
for(const f of [0,29,7,18,1,25,4,16,9,28]){
 const {a,b,child}=fixture(f),before=child.getGlobalTransform();
 for(const parent of [b,a,b,a]){
  const ret=reparentWithFreshTransform(child,parent);assert.equal(ret,child);assert.equal(child.parent,parent);
  const after=child.getGlobalTransform();for(const k of keys){const delta=Math.abs(after[k]-before[k]);maxDelta=Math.max(maxDelta,delta);assert(delta<1e-9,`${f}/${k}: ${delta}`)}checks++;
 }
}
// One additional fixture covers explicit pivot/skew; all tested scales positive.
{
 const {a,b,child}=fixture(13);child.pivot.set(17,-9);child.skew.set(.12,-.08);
 const before=child.getGlobalTransform();
 for(const parent of [b,a,b,a]){
  reparentWithFreshTransform(child,parent);const after=child.getGlobalTransform();
  for(const k of keys){const delta=Math.abs(after[k]-before[k]);maxDelta=Math.max(maxDelta,delta);assert(delta<1e-9)}checks++;
 }
}
// A combined pivot/skew/reflection success fixture exercises Matrix.decompose.
{
 const {a,b,child}=fixture(16);child.pivot.set(17,-9);child.skew.set(.12,-.08);child.scale.x=-1.14;b.scale.y=-1.8;
 const before=child.getGlobalTransform();
 for(const parent of [b,a,b,a]){
  reparentWithFreshTransform(child,parent);const after=child.getGlobalTransform();
  for(const k of keys){const delta=Math.abs(after[k]-before[k]);maxDelta=Math.max(maxDelta,delta);assert(delta<1e-9)}checks++;
 }
}
let rejectionChecks=0;
for(const kind of ['origin','singular-destination','nonfinite-destination','self','descendant']){
 const {a,b,child}=fixture(3);
 let destination=b;
 if(kind==='origin')child.origin.set(10,20);
 if(kind==='singular-destination')b.scale.x=0;
 if(kind==='nonfinite-destination')b.x=Infinity;
 if(kind==='self')destination=child;
 if(kind==='descendant'){destination=new Container();child.addChild(destination)}
 const before=child.getGlobalTransform();const pose=[child.x,child.y,child.scale.x,child.scale.y,child.rotation,child.skew.x,child.skew.y];
 assert.throws(()=>reparentWithFreshTransform(child,destination),RangeError);assert.equal(child.parent,a);
 assert.deepEqual([child.x,child.y,child.scale.x,child.scale.y,child.rotation,child.skew.x,child.skew.y],pose);
 const after=child.getGlobalTransform();for(const k of keys)assert.equal(before[k],after[k]);rejectionChecks++;
}
console.log(JSON.stringify({transferChecks:checks,freshFixtures:12,rejectionChecks,cachedTransferCounterexample:'unrendered identity caches',maxMatrixDelta:maxDelta,downloads:false,gpu:false}));
