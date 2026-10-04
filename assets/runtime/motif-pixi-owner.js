/* Fresh-transform ownership transfer for externally seeked Pixi v8 scenes.
 * getGlobalTransform() recomputes the hierarchy; cached worldTransform can be
 * stale before a render. This helper does not start a ticker or own time. */
(function(root){
 function reparentWithFreshTransform(child,parent){
  if(!child || !parent)throw new TypeError("child and parent required");
  for(let node=parent;node;node=node.parent){
   if(node===child)throw new RangeError("self or descendant destination is unsupported");
  }
  // Pixi8.22 Matrix.decompose compensates pivot, but not the child's origin.
  // Reject unsupported/noninvertible inputs before changing owner or pose.
  const origin=child.origin;
  if(origin && (origin.x!==0 || origin.y!==0))throw new RangeError("nonzero child origin is unsupported");
  const world=child.getGlobalTransform();
  const inverse=parent.getGlobalTransform();
  const keys=['a','b','c','d','tx','ty'];
  if(!keys.every(k=>Number.isFinite(world[k]) && Number.isFinite(inverse[k])))throw new RangeError("finite transforms required");
  const determinant=inverse.a*inverse.d-inverse.b*inverse.c;
  if(!Number.isFinite(determinant) || determinant===0)throw new RangeError("nonsingular destination transform required");
  inverse.invert();world.prepend(inverse);
  if(!keys.every(k=>Number.isFinite(world[k])))throw new RangeError("finite resulting transform required");
  parent.addChild(child);child.setFromMatrix(world);
  return child;
 }
 if(typeof module!=="undefined")module.exports={reparentWithFreshTransform};
 else root.MotifPixiOwner={reparentWithFreshTransform};
})(typeof globalThis!=="undefined"?globalThis:this);
