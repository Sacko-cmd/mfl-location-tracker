import {readBounded} from "./diagnostics";

export interface Embed {
  title: string;
  description?: string;
  url?: string;
  fields?: {name: string; value: string; inline?: boolean}[];
  timestamp?: string;
}
export interface Payload {username?: string; content?: string; embeds?: Embed[]; allowed_mentions?: {parse: string[]}}

export function webhookUrl(value: string): URL {
  const url = new URL(value);
  if (url.protocol !== "https:" || url.hostname !== "discord.com" || !/^\/api(?:\/v\d+)?\/webhooks\/\d+\/[A-Za-z0-9_-]+$/.test(url.pathname)) {
    throw new Error("Invalid Discord webhook");
  }
  return url;
}

export async function sendWebhook(value: string, payload: Payload) {
  const url = webhookUrl(value);
  url.searchParams.set("wait", "true");
  let response: Response;
  try {
    response = await fetch(url, {method: "POST", redirect: "manual", signal: AbortSignal.timeout(8000),
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({...payload, allowed_mentions: {parse: []}})});
  } catch { throw new Error("Discord request failed"); }
  const body = await readBounded(response);
  if (!response.ok) throw new Error(`Discord HTTP ${response.status}`);
  const result = JSON.parse(body) as {id?: string; channel_id?: string};
  if (!result.id || !result.channel_id) throw new Error("Discord did not confirm a saved message");
  return {message_id: result.id, channel_id: result.channel_id};
}

export async function enqueue(env: Env, id: string, kind: string, source: string, payload: Payload) {
  return env.DB.prepare("INSERT OR IGNORE INTO notifications(id, source_kind, source_id, payload) VALUES(?, ?, ?, ?)")
    .bind(id, kind, source, JSON.stringify(payload)).run();
}

export async function flushNotifications(env: Env) {
  const due = await env.DB.prepare("SELECT id FROM notifications WHERE (state = 'pending' OR (state = 'sending' AND lease_until < ?)) AND next_attempt <= ? ORDER BY next_attempt, rowid LIMIT 5")
    .bind(Date.now(), Date.now()).all<{id: string}>();
  for (const item of due.results) {
    const token = crypto.randomUUID();
    const row = await env.DB.prepare("UPDATE notifications SET state = 'sending', lock_token = ?, lease_until = ?, attempts = attempts + 1 WHERE id = ? AND (state = 'pending' OR (state = 'sending' AND lease_until < ?)) RETURNING *")
      .bind(token, Date.now() + 60000, item.id, Date.now()).first<{id: string; source_kind: string; source_id: string; payload: string; attempts: number}>();
    if (!row) continue;
    try {
      let webhook = env.DISCORD_WEBHOOK_URL;
      if (row.source_kind === "monitor") {
        webhook = ""; // Marketplace alerts are disabled.
      } else if (row.source_kind === "subscriber") {
        const subscriber = await env.DB.prepare("SELECT webhook FROM subscribers WHERE user_id = ? AND paused = 0").bind(row.source_id).first<{webhook: string}>();
        webhook = subscriber?.webhook ?? "";
      }
      if (!webhook) {
        await env.DB.prepare("UPDATE notifications SET state = 'cancelled', lock_token = NULL WHERE id = ? AND lock_token = ?").bind(row.id, token).run();
        continue;
      }
      const receipt = await sendWebhook(webhook, JSON.parse(row.payload));
      await env.DB.prepare("UPDATE notifications SET state = 'sent', message_id = ?, channel_id = ?, sent_at = ?, last_error = NULL, lock_token = NULL WHERE id = ? AND lock_token = ?")
        .bind(receipt.message_id, receipt.channel_id, new Date().toISOString(), row.id, token).run();
      if (row.source_kind === "global" && row.source_id) {
        await env.DB.prepare("UPDATE transfers SET delivery = 'sent', delivery_attempts = ?, message_id = ?, delivered_at = ? WHERE event_id = ?")
          .bind(row.attempts, receipt.message_id, new Date().toISOString(), row.source_id).run();
      }
    } catch (error) {
      const safe = error instanceof Error && /^(Discord |Invalid Discord)/.test(error.message) ? error.message : "Notification delivery failed";
      await env.DB.prepare("UPDATE notifications SET state = 'pending', last_error = ?, next_attempt = ?, lock_token = NULL WHERE id = ? AND lock_token = ?")
        .bind(safe, Date.now() + Math.min(3600000, 60000 * 2 ** Math.min(row.attempts - 1, 6)), row.id, token).run();
    }
  }
}

export async function testAlert(env: Env) {
  const id = "setup-location-alert-v1";
  await enqueue(env, id, "global", "", {username: "MFL Location Tracker", embeds: [{
    title: "TEST — MFL Location Tracker",
    description: "Discord alerts are connected to the Cloudflare tracker. This is a setup test, not a real location transfer.",
    timestamp: new Date().toISOString(),
  }]});
  await flushNotifications(env);
  return (await env.DB.prepare("SELECT id, state, message_id, channel_id, sent_at, last_error FROM notifications WHERE id = ?").bind(id).all()).results;
}
