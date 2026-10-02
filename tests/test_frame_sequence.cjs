/* Exercise forward, reverse, repeated and end-boundary seeks of the bounded lookup. */
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const element={innerHTML:''};let current=0,update,compiles=0;
const tl={time:()=>current,eventCallback:(name,fn)=>{assert.equal(name,'onUpdate');update=fn;}};
const context={window:{MotifEventEngine:{compile:(spec)=>{compiles++;element.innerHTML=spec.initial[0].props.innerHTML;assert.equal(spec.events.length,1);return tl;}}},document:{querySelector:selector=>selector==='#world'?element:null}};
vm.runInNewContext(fs.readFileSync('assets/runtime/motif-frame-sequence.js','utf8'),context);
const spec={schemaVersion:'1.0',fps:30,durationSec:.1,initial:[{target:'#world',props:{innerHTML:'A'}}],events:[1,2].map((f)=>({time:f/30,target:'#world',action:'SET',params:{props:{innerHTML:['A','B','C'][f]}}}))};
context.window.MotifEventEngine.compileFrames(spec,'sample');assert.equal(compiles,1);
for (const [time,expected] of [[0,'A'],[1/30,'B'],[2/30,'C'],[.1,'C'],[0,'A'],[.049,'B'],[.049,'B'],[.067,'C'],[.001,'A']]){current=time;update();assert.equal(element.innerHTML,expected);}
const bad=JSON.parse(JSON.stringify(spec));bad.events[0].time=.08;assert.throws(()=>context.window.MotifEventEngine.compileFrames(bad,'sample'),/contiguous/);
console.log('PASS: exact boundaries, reverse and repeated seeks; one existing compiler timeline; unsupported timing rejected');
