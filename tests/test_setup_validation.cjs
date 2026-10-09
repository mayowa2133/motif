"use strict";
const assert = require("node:assert/strict");
const {test} = require("node:test");
const guards = require("../scripts/motif_setup_validation.cjs");

test("coordinate tuples reject sparse and inherited entries before sampling", () => {
  const hole = [1, 2]; delete hole[1];
  const inherited = [1, 2]; delete inherited[1];
  const prototype = Object.create(Array.prototype); prototype[1] = 2;
  Object.setPrototypeOf(inherited, prototype);
  for (const value of [hole, inherited, Array(2), [1], [1, 2, 3]]) {
    assert.throws(() => guards.tuple(value, 2, "pose.gaze"), /pose.gaze/);
  }
});
test("finite guards reject coercion and nonfinite coordinates", () => {
  for (const value of [NaN, Infinity, -Infinity, "1", null, undefined, true]) {
    assert.throws(() => guards.finite(value, "time"), /time/);
    assert.throws(() => guards.tuple([0, value], 2, "point"), /point/);
  }
  for (const value of [0, -1, 1.25, Number.MAX_VALUE]) assert.doesNotThrow(() => guards.finite(value, "time"));
});
test("action/key arrays reject holes and enforce declared minimum", () => {
  assert.doesNotThrow(() => guards.denseArray([], "actions"));
  assert.doesNotThrow(() => guards.denseArray([{}, {}], "poseKeys", 2));
  for (const value of [null, {}, Array(2), [{}]]) {
    assert.throws(() => guards.denseArray(value, "poseKeys", 2), /poseKeys/);
  }
  for (const minimum of [-1, 0.5, NaN, Infinity, "2"]) {
    assert.throws(() => guards.denseArray([], "actions", minimum), /minimum/);
    assert.throws(() => guards.tuple([], minimum, "point"), /length/);
  }
});
test("valid frozen input is retained without mutation", () => {
  const value = Object.freeze([1.5, -2]); const config = Object.freeze({gaze: value});
  assert.doesNotThrow(() => guards.record(config, "config"));
  assert.doesNotThrow(() => guards.tuple(value, 2, "gaze")); assert.deepEqual(value, [1.5, -2]);
  for (const invalid of [null, [], 4, "config", undefined]) assert.throws(() => guards.record(invalid, "config"), /config/);
});
test("instance identifiers require actual strings without coercion", () => {
  let coercions = 0; const object = {toString() {coercions++; return "actor";}};
  for (const value of [object, null, 123, "", "1actor", "actor slot", "actor<id>"]) {
    assert.throws(() => guards.instanceId(value), /instance id/);
  }
  assert.equal(coercions, 0);
  for (const value of ["actor", "actor-2", "actor_slot"]) assert.doesNotThrow(() => guards.instanceId(value));
});
