import {test} from "node:test";
import assert from "node:assert/strict";
import {comparePools, parsePool} from "../src/tracking";

const current = parsePool([{club: {id: 35, city: "Glasgow", country: "SCOTLAND"}}]);

test("first snapshot seeds ownership without historical departures", () => {
  const result = comparePools({}, current, "2026-09-18T20:00:00Z");
  assert.deepEqual(result.next, current);
  assert.deepEqual(result.missing, []);
});

test("departures require distinct polls and retain the original missing time", () => {
  const first = comparePools(current, {}, "2026-09-18T20:00:00Z");
  const second = comparePools(first.next, {}, "2026-09-18T20:01:00Z");
  const third = comparePools(second.next, {}, "2026-09-18T20:02:00Z");
  assert.equal(first.missing[0].missingPolls, 1);
  assert.equal(second.missing[0].missingPolls, 2);
  assert.equal(third.missing[0].missingPolls, 3);
  assert.equal(third.missing[0].missingSince, "2026-09-18T20:00:00Z");
});

test("reappearance resets the confirmation count", () => {
  const missing = comparePools(current, {}, "2026-09-18T20:00:00Z");
  const restored = comparePools(missing.next, current, "2026-09-18T20:01:00Z");
  const again = comparePools(restored.next, {}, "2026-09-18T20:02:00Z");
  assert.equal(again.missing[0].missingPolls, 1);
  assert.equal(again.missing[0].missingSince, "2026-09-18T20:02:00Z");
});

test("malformed API data is rejected instead of implying an empty pool", () => {
  for (const body of [{error: "Forbidden"}, null, "<html>", [{}], [{club: {id: "../other"}}]]) {
    assert.throws(() => parsePool(body));
  }
});

test("a valid empty pool remains distinguishable from a failed API call", () => {
  assert.deepEqual(parsePool([]), {});
});
