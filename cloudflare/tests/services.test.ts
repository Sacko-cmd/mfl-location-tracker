import {test} from "node:test";
import assert from "node:assert/strict";
import {sendWebhook, webhookUrl} from "../src/discord";
import {commands} from "../src/bot";
import {verifyDiscordSignature} from "../src/bot";
import {generateKeyPairSync, sign} from "node:crypto";

test("Discord commands require valid signatures and reject replayed timestamps", async () => {
  const pair = generateKeyPairSync("ed25519");
  const key = pair.publicKey.export({type: "spki", format: "der"}).subarray(-32).toString("hex");
  const body = JSON.stringify({type: 1});
  const timestamp = String(Math.floor(Date.now() / 1000));
  const signature = sign(null, Buffer.from(timestamp + body), pair.privateKey).toString("hex");
  assert.equal(await verifyDiscordSignature(body, signature, timestamp, key), true);
  assert.equal(await verifyDiscordSignature(body + " ", signature, timestamp, key), false);
  assert.equal(await verifyDiscordSignature(body, signature, "0", key), false);
  assert.equal(await verifyDiscordSignature(body, "invalid", timestamp, key), false);
});

test("webhooks reject arbitrary hosts and malformed paths", () => {
  for (const url of ["https://example.com/api/webhooks/123/token", "http://discord.com/api/webhooks/123/token", "https://discord.com/api/users/@me"])
    assert.throws(() => webhookUrl(url));
});

test("delivery requires Discord to acknowledge a saved message", async () => {
  const original = globalThis.fetch;
  try {
    globalThis.fetch = async (input, init) => {
      assert.equal(new URL(String(input)).searchParams.get("wait"), "true");
      assert.deepEqual(JSON.parse(String(init?.body)).allowed_mentions, {parse: []});
      return Response.json({id: "message-1", channel_id: "channel-1"});
    };
    assert.deepEqual(await sendWebhook("https://discord.com/api/webhooks/123/test", {content: "Test"}), {message_id: "message-1", channel_id: "channel-1"});
    globalThis.fetch = async () => Response.json({message: "rate limited"}, {status: 429});
    await assert.rejects(sendWebhook("https://discord.com/api/webhooks/123/test", {content: "Test"}), /Discord HTTP 429/);
    globalThis.fetch = async () => Response.json({});
    await assert.rejects(sendWebhook("https://discord.com/api/webhooks/123/test", {content: "Test"}), /did not confirm/);
  } finally {globalThis.fetch = original;}
});

test("slash-command registration has unique valid names", () => {
  assert.equal(new Set(commands.map(command => command.name)).size, commands.length);
  for (const command of commands) assert.match(command.name, /^[a-z_]{1,32}$/);
  for (const name of ["register", "watchall", "wallet", "club", "recent", "health", "export_history"]) assert.ok(commands.some(command => command.name === name));
});
