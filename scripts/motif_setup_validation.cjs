"use strict";

// Optional guards extracted from the reviewed frontal-kit v0.1.2 setup boundary.
// No artwork, geometry, sampling, DOM mutation or production integration.
function record(value, path) {
  if (value === null || typeof value !== "object" || Array.isArray(value)) {
    throw new Error(path + ": record required");
  }
}
function denseArray(value, path, minimum = 0) {
  if (!Number.isInteger(minimum) || minimum < 0) {
    throw new Error("minimum: nonnegative integer required");
  }
  if (!Array.isArray(value) || value.length < minimum) {
    throw new Error(path + ": dense array with at least " + minimum + " entries required");
  }
  for (let i = 0; i < value.length; i++) {
    if (!Object.prototype.hasOwnProperty.call(value, i)) throw new Error(path + ": dense array required");
  }
}
function tuple(value, length, path) {
  if (!Number.isInteger(length) || length < 0) throw new Error("length: nonnegative integer required");
  if (!Array.isArray(value) || value.length !== length) {
    throw new Error(path + ": exactly " + length + " finite coordinates required");
  }
  for (let i = 0; i < length; i++) {
    if (!Object.prototype.hasOwnProperty.call(value, i) || !Number.isFinite(value[i])) {
      throw new Error(path + ": exactly " + length + " finite coordinates required");
    }
  }
}
function finite(value, path) {
  if (!Number.isFinite(value)) throw new Error(path + ": finite number required");
}
function instanceId(value) {
  if (typeof value !== "string" || !/^[A-Za-z][A-Za-z0-9_-]*$/.test(value)) {
    throw new Error("safe instance id required");
  }
}
module.exports = Object.freeze({record, denseArray, tuple, finite, instanceId});
