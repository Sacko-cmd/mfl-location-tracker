import {enqueue} from "./discord";
import {headers, readBounded} from "./diagnostics";
import {comparePools, parsePool, type Pool} from "./tracking";

interface StateRow {
  state_json: string;
  initialized: number;
  last_attempt: string | null;
}
interface Detail {
  id: number;
  name?: string;
  city?: string;
  country?: string;
  ownedBy?: {walletAddress?: string; name?: string};
}
interface Transfer {
  event_id: string;
  detected_at: string;
  club_id: string;
  city: string;
  country: string;
  manager: string;
  wallet: string;
  club_name: string;
}

async function getJson(path: string): Promise<unknown> {
  const response = await fetch(`https://api.playmfl.com${path}`, {
    headers, redirect: "manual", signal: AbortSignal.timeout(12000),
  });
  if (!response.ok) {
    await response.body?.cancel();
    throw new Error(`MFL HTTP ${response.status} (${path.split("?")[0]})`);
  }
  return JSON.parse(await readBounded(response));
}

async function deliver(env: Env) {
  if (!env.DISCORD_WEBHOOK_URL) return;
  const url = new URL(env.DISCORD_WEBHOOK_URL);
  if (url.protocol !== "https:" || url.hostname !== "discord.com" || !url.pathname.startsWith("/api/webhooks/")) {
    throw new Error("Invalid Discord webhook configuration");
  }
  const pending = await env.DB.prepare("SELECT * FROM transfers WHERE delivery = 'pending' ORDER BY detected_at LIMIT 5").all<Transfer>();
  for (const event of pending.results) {
    await enqueue(env, `transfer:${event.event_id}`, "global", event.event_id, {
      username: "MFL Location Tracker", embeds: [{
        title: `${event.city}, ${event.country}`.slice(0, 256),
        description: `Location moved to **${event.manager}**`.slice(0, 4096),
        url: `https://app.playmfl.com/clubs/${event.club_id}`,
        fields: [{name: "Club ID", value: event.club_id}, {name: "Wallet", value: event.wallet}],
        timestamp: event.detected_at,
      }],
    });
  }
}

export async function runPoll(env: Env) {
  const now = new Date().toISOString();
  const token = crypto.randomUUID();
  // A lease and minimum interval prevent cron retries/manual checks from counting
  // as multiple missing polls. The bounded requests finish before lease expiry.
  const row = await env.DB.prepare(
    "UPDATE tracker SET lock_token = ?, locked_until = ?, last_attempt = ? WHERE id = 1 AND locked_until < ? AND (last_attempt IS NULL OR last_attempt < ?) RETURNING state_json, initialized, last_attempt",
  ).bind(token, Date.now() + 180000, now, Date.now(), new Date(Date.now() - 45000).toISOString()).first<StateRow>();
  if (!row) return {skipped: true};
  try {
    const current = parsePool(await getJson(`/clubs?walletAddress=${encodeURIComponent(env.CENTRAL_WALLET)}`));
    const previous: Pool = JSON.parse(row.state_json);
    const {next, missing} = comparePools(previous, current, now);
    const threshold = Number(env.CONFIRM_MISSING_POLLS);
    if (!Number.isInteger(threshold) || threshold < 1) throw new Error("Invalid missing-poll threshold");
    const confirmed: Transfer[] = [];
    const failures: string[] = [];
    const candidates = missing.filter(club => (club.missingPolls ?? 0) >= threshold);
    // Bound subrequests per tick. Remaining departures stay pending for later polls.
    const selected = candidates.sort((a, b) => (a.lastLookup ?? 0) - (b.lastLookup ?? 0)).slice(0, 10);
    for (let i = 0; i < selected.length; i += 5) {
      await Promise.all(selected.slice(i, i + 5).map(async club => {
        if (Date.now() - Date.parse(club.missingSince!) > 6 * 3600000) {
          delete next[club.id];
          return;
        }
        club.lastLookup = Date.now();
        try {
          const detail = await getJson(`/clubs/${club.id}`) as Detail;
          if (String(detail?.id) !== club.id) throw new Error("Club ID mismatch");
          const wallet = detail.ownedBy?.walletAddress;
          if (!wallet || wallet.toLowerCase() === env.CENTRAL_WALLET.toLowerCase()) return;
          confirmed.push({
            event_id: `${club.id}:${club.missingSince}`, detected_at: now, club_id: club.id,
            city: detail.city || club.city, country: detail.country || club.country,
            manager: detail.ownedBy?.name || "Unknown", wallet, club_name: detail.name || "",
          });
          delete next[club.id];
        } catch (error) {
          failures.push(error instanceof Error ? error.message : "Club lookup failed");
        }
      }));
    }
    const subscribers = await env.DB.prepare("SELECT * FROM subscribers WHERE paused = 0").all<{user_id: string; webhook: string; cities: string; countries: string; club_ids: string}>();
    const statements = confirmed.map(event => env.DB.prepare(
      "INSERT OR IGNORE INTO transfers(event_id, detected_at, club_id, city, country, manager, wallet, club_name, delivery) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",
    ).bind(event.event_id, event.detected_at, event.club_id, event.city, event.country, event.manager, event.wallet,
      event.club_name, env.DISCORD_WEBHOOK_URL ? "pending" : "not_configured"));
    for (const event of confirmed) {
      for (const sub of subscribers.results) {
        if (sub.webhook === env.DISCORD_WEBHOOK_URL) continue;
        const cities: string[] = JSON.parse(sub.cities), countries: string[] = JSON.parse(sub.countries), ids: string[] = JSON.parse(sub.club_ids);
        if (!cities.includes("*") && !cities.some(city => city.toLowerCase() === event.city.toLowerCase()) && !countries.some(country => country.toLowerCase() === event.country.toLowerCase()) && !ids.includes(event.club_id)) continue;
        const payload = {username: "MFL Location Tracker", embeds: [{title: `${event.city}, ${event.country}`.slice(0, 256), description: `Location moved to **${event.manager}**`.slice(0, 4096), url: `https://app.playmfl.com/clubs/${event.club_id}`, timestamp: event.detected_at}]};
        statements.push(env.DB.prepare("INSERT OR IGNORE INTO notifications(id, source_kind, source_id, payload) VALUES(?, 'subscriber', ?, ?)").bind(`subscriber:${sub.user_id}:${event.event_id}`, sub.user_id, JSON.stringify(payload)));
      }
    }
    statements.push(env.DB.prepare(
      "UPDATE tracker SET state_json = ?, initialized = 1, pool_count = ?, pending_count = ?, last_success = ?, last_error = ? WHERE id = 1 AND lock_token = ?",
    ).bind(JSON.stringify(next), Object.keys(current).length, Object.values(next).filter(club => club.missingSince).length,
      now, failures.length ? failures[0] : null, token));
    await env.DB.batch(statements);
    console.log(JSON.stringify({event: "pool_poll", pool: Object.keys(current).length, transfers: confirmed.length, lookup_failures: failures.length}));
    return {ok: failures.length === 0, pool_count: Object.keys(current).length, transfers: confirmed.length};
  } catch (error) {
    // Upstream error text is generated here; do not persist arbitrary fetch errors
    // that could contain a secret webhook URL.
    const message = error instanceof Error && /^(MFL HTTP|Discord HTTP|Invalid |Club ID)/.test(error.message)
      ? error.message : "Polling failed; inspect Cloudflare logs";
    await env.DB.prepare("UPDATE tracker SET last_error = ? WHERE id = 1 AND lock_token = ?").bind(message, token).run();
    console.error(JSON.stringify({event: "poll_failed", error: message}));
    return {ok: false, error: message};
  } finally {
    try {await deliver(env);} catch (error) {
      const safe = error instanceof Error && error.message.startsWith("Discord ") ? error.message : "Discord delivery failed";
      await env.DB.prepare("UPDATE tracker SET last_error = ? WHERE id = 1 AND lock_token = ?").bind(safe, token).run();
    }
    await env.DB.prepare("UPDATE tracker SET lock_token = NULL, locked_until = 0 WHERE id = 1 AND lock_token = ?").bind(token).run();
  }
}

export async function status(env: Env) {
  const row = await env.DB.prepare("SELECT initialized, pool_count, pending_count, last_attempt, last_success, last_error FROM tracker WHERE id = 1").first<{
    initialized: number; pool_count: number; pending_count: number;
    last_attempt: string | null; last_success: string | null; last_error: string | null;
  }>();
  const deliveries = await env.DB.prepare("SELECT delivery, COUNT(*) AS count FROM transfers GROUP BY delivery").all();
  const registered = await env.DB.prepare("SELECT value FROM service_settings WHERE key = 'commands_registered'").first<{value: string}>();
  const notificationSummary = await env.DB.prepare("SELECT SUM(state = 'sent') AS sent, SUM(state = 'pending' AND last_error IS NOT NULL) AS errors, MAX(sent_at) AS last_confirmed_delivery FROM notifications").first();
  const healthy = !!row?.last_success && Date.now() - Date.parse(row.last_success) < 180000 && !row.last_error;
  return {
    service: "MFL Location Tracker", runtime: "Cloudflare Workers", storage: "D1",
    status: healthy ? "ok" : "degraded", healthy, schedule: "every minute",
    confirm_missing_polls: Number(env.CONFIRM_MISSING_POLLS),
    alerts_enabled: !!env.DISCORD_WEBHOOK_URL,
    discord_bot_commands: !!env.DISCORD_APPLICATION_ID && !!env.DISCORD_PUBLIC_KEY && !!registered,
    bot: {application_configured: !!env.DISCORD_APPLICATION_ID && !!env.DISCORD_PUBLIC_KEY, commands_registered_at: registered?.value ?? null},
    discord_delivery: notificationSummary,
    marketplace_monitors: false,
    notifications: (await env.DB.prepare("SELECT state, COUNT(*) AS count FROM notifications GROUP BY state").all()).results,
    tracker: row, deliveries: deliveries.results,
  };
}
