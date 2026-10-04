/* Fresh-transform ownership transfer for externally seeked Pixi v8 scenes.
 * getGlobalTransform() recomputes the hierarchy; cached worldTransform can be
 * stale before a render. This helper does not start a ticker or own time. */
(function(root){
 function reparentWithFreshTransform(child,parent){
  if(!child || !parent)throw new TypeError("child and parent required");
  const world=child.getGlobalTransform();
  const inverse=parent.getGlobalTransform().invert();
  parent.addChild(child);
  child.setFromMatrix(world.prepend(inverse));
  return child;
 }
 if(typeof module!=="undefined")module.exports={reparentWithFreshTransform};
 else root.MotifPixiOwner={reparentWithFreshTransform};
})(typeof globalThis!=="undefined"?globalThis:this);
