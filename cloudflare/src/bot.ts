import {headers, readBounded} from "./diagnostics";
import {webhookUrl} from "./discord";
import type {Pool} from "./tracking";

type Option = {name: string; value?: string | number};
type Interaction = {id: string; application_id: string; token: string; type: number; member?: {user: {id: string}; permissions?: string}; user?: {id: string}; data?: {name: string; options?: Option[]}};
type Subscription = {user_id: string; webhook: string; cities: string; countries: string; club_ids: string; paused: number};
const simple = {
  ping: "Check whether the tracker bot is online", help: "Show tracker commands", version: "Show tracker version",
  health: "Check polling and notification health", wallet: "Show the pool wallet count", pending: "Show pending pool departures",
  stats: "Show tracker statistics", mysettings: "Show your notification settings", list: "Show your watchlist",
  status: "Show your watchlist and service status", watchall: "Watch all locations", pause: "Pause your alerts", resume: "Resume your alerts",
  unregister: "Remove your alert registration", country_list: "List your watched countries", club_list: "List watched club IDs",
  refresh: "Request a pool check (server managers only)", rebuild: "Refresh current ownership (server managers only)",
  poollog: "Show recent recorded transfers", export_history: "Download transfer history as CSV",
};
const argumentsByName: Record<string, [string, string, string]> = {
  register: ["webhook", "Discord channel webhook URL", "Register your channel for alerts"],
  add: ["city", "City name", "Watch a city"], remove: ["city", "City name", "Stop watching a city"],
  country: ["country", "Country name as shown by MFL", "Watch a country"], country_remove: ["country", "Country name", "Stop watching a country"],
  clubid: ["id", "Club ID", "Watch a club ID"], remove_clubid: ["id", "Club ID", "Stop watching a club ID"],
  club: ["id", "Club ID", "Look up current club ownership"], search: ["query", "City, country, or club ID", "Search the pool wallet"],
  history: ["city", "City name", "Look up transfer history for a city"], manager: ["name", "Manager name", "Look up transfers for a manager"],
};
export const commands = [
  ...Object.entries(simple).map(([name, description]) => ({name, description, type: 1})),
  ...Object.entries(argumentsByName).map(([name, [key, description, label]]) => ({name, description: label, type: 1, options: [{name: key, description, type: 3, required: true, max_length: name === "register" ? 250 : 150}]})),
  {name: "recent", description: "Show recent location transfers", type: 1, options: [{name: "limit", description: "Number of transfers", type: 4, min_value: 1, max_value: 20}]},
];

async function pool(env: Env): Promise<Pool> {
  const row = await env.DB.prepare("SELECT state_json FROM tracker WHERE id = 1").first<{state_json: string}>();
  return row ? JSON.parse(row.state_json) : {};
}

function settingText(sub: Subscription | null) {
  if (!sub) return "You are not registered. Use /register with a channel webhook, then /watchall or /add.";
  return `Paused: ${!!sub.paused}\nCities: ${JSON.parse(sub.cities).join(", ") || "none"}\nCountries: ${JSON.parse(sub.countries).join(", ") || "none"}\nClub IDs: ${JSON.parse(sub.club_ids).join(", ") || "none"}`;
}

export async function commandReply(interaction: Interaction, env: Env): Promise<{content: string; csv?: string}> {
  const name = interaction.data?.name ?? "";
  const user = interaction.member?.user.id ?? interaction.user?.id;
  if (!user) return {content: "Could not identify the requesting user."};
  const options = Object.fromEntries((interaction.data?.options ?? []).map(option => [option.name, option.value]));
  const value = String(Object.values(options)[0] ?? "").trim();
  const reply = (content: string) => ({content: content.slice(0, 1950)});
  if (name === "ping") return reply("MFL Tracker is online on Cloudflare.");
  if (name === "version") return reply("MFL Tracker — Cloudflare edition 2");
  if (name === "help") return reply("**Watchlists**\n/register, /unregister, /mysettings, /watchall, /add, /remove, /list, /pause, /resume, /country, /country_remove, /country_list, /clubid, /remove_clubid, /club_list\n**Pool**\n/wallet, /search, /club, /pending\n**History**\n/recent, /history, /manager, /poollog, /export_history\n**Health**\n/ping, /health, /stats, /status, /refresh, /rebuild, /version\nReplies are private. Register a webhook and choose locations to receive your own alerts.");
  if (name === "register") {
    const url = webhookUrl(value);
    const result = await fetch(url, {redirect: "manual", signal: AbortSignal.timeout(8000)});
    await result.body?.cancel();
    if (!result.ok) return reply(`Discord rejected the webhook (HTTP ${result.status}).`);
    await env.DB.prepare("INSERT INTO subscribers(user_id, webhook) VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE SET webhook = excluded.webhook").bind(user, url.toString()).run();
    return reply("Registered. Use /watchall to watch all locations, or /add, /country, and /clubid to select a watchlist.");
  }
  if (name === "unregister") {
    await env.DB.batch([env.DB.prepare("DELETE FROM subscribers WHERE user_id = ?").bind(user), env.DB.prepare("UPDATE notifications SET state = 'cancelled' WHERE source_kind = 'subscriber' AND source_id = ? AND state = 'pending'").bind(user)]);
    return reply("Your registration and watchlist have been removed.");
  }
  const sub = await env.DB.prepare("SELECT * FROM subscribers WHERE user_id = ?").bind(user).first<Subscription>();
  if (["mysettings", "list", "status"].includes(name)) return reply(settingText(sub));
  if (["watchall", "pause", "resume", "add", "remove", "country", "country_remove", "clubid", "remove_clubid", "country_list", "club_list"].includes(name)) {
    if (!sub) return reply(settingText(sub));
    if (name === "pause" || name === "resume") {
      await env.DB.prepare("UPDATE subscribers SET paused = ? WHERE user_id = ?").bind(Number(name === "pause"), user).run();
      return reply(name === "pause" ? "Your alerts are paused." : "Your alerts are resumed.");
    }
    if (name === "watchall") {
      await env.DB.prepare("UPDATE subscribers SET cities = '[\"*\"]', paused = 0 WHERE user_id = ?").bind(user).run();
      return reply("You are watching all locations.");
    }
    const field = name.startsWith("country") ? "countries" : name.includes("club") ? "club_ids" : "cities";
    const values: string[] = JSON.parse(sub[field]);
    if (name.endsWith("_list")) return reply(values.join(", ") || "None watched.");
    if (field === "club_ids" && !/^\d+$/.test(value)) return reply("Club IDs must contain digits only.");
    const removing = name.includes("remove");
    const next = values.filter(item => item.toLowerCase() !== value.toLowerCase());
    if (!removing) next.push(value);
    // Column name comes only from the fixed mapping above; values remain bound.
    await env.DB.prepare(`UPDATE subscribers SET ${field} = ? WHERE user_id = ?`).bind(JSON.stringify(next), user).run();
    return reply(`${removing ? "Removed" : "Added"}: ${value}`);
  }
  if (["wallet", "search", "pending"].includes(name)) {
    const clubs = Object.values(await pool(env));
    if (name === "wallet") return reply(`Pool wallet contains **${clubs.filter(club => !club.missingSince).length}** locations.`);
    const matches = name === "pending" ? clubs.filter(club => club.missingSince) : clubs.filter(club => !club.missingSince && `${club.city} ${club.country} ${club.id}`.toLowerCase().includes(value.toLowerCase()));
    return reply(matches.length ? `${matches.length} results (showing up to 20):\n` + matches.slice(0, 20).map(club => `${club.city}, ${club.country} — ${club.id}`).join("\n") : "No matching locations.");
  }
  if (name === "club") {
    if (!/^\d+$/.test(value)) return reply("Club IDs must contain digits only.");
    const result = await fetch(`https://api.playmfl.com/clubs/${value}`, {headers, redirect: "manual", signal: AbortSignal.timeout(12000)});
    if (!result.ok) {await result.body?.cancel(); return reply(`MFL lookup failed (HTTP ${result.status}).`);}
    const club = JSON.parse(await readBounded(result));
    return reply(`**Club ${value}**\n${club.city}, ${club.country}\nOwner: ${club.ownedBy?.name ?? "Unknown"}\nWallet: ${club.ownedBy?.walletAddress ?? "Unknown"}\nStatus: ${club.status}`);
  }
  if (["health", "stats"].includes(name)) {
    const row = await env.DB.prepare("SELECT pool_count, pending_count, last_success, last_error FROM tracker WHERE id = 1").first();
    const count = await env.DB.prepare("SELECT COUNT(*) AS count FROM transfers").first<{count: number}>();
    return reply(`Pool: ${row?.pool_count}\nPending: ${row?.pending_count}\nLast successful poll: ${row?.last_success ?? "Never"}\nLast error: ${row?.last_error ?? "None"}\nTransfers recorded: ${count?.count ?? 0}`);
  }
  if (["refresh", "rebuild"].includes(name)) {
    const permissions = BigInt(interaction.member?.permissions ?? "0");
    if (!(permissions & 32n) && !(permissions & 8n)) return reply("Manage Server permission is required.");
    const {runPoll} = await import("./tracker");
    const result = await runPoll(env);
    return reply(result.skipped ? "A poll is already running or ran recently." : result.ok ? "Pool check completed. Ownership is resolved directly; no leaderboard cache is needed." : `Poll failed: ${result.error}`);
  }
  if (["recent", "history", "manager", "poollog", "export_history"].includes(name)) {
    const limit = name === "export_history" ? 1000 : Math.min(20, Math.max(1, Number(options.limit ?? 10)));
    const column = name === "history" ? "city" : name === "manager" ? "manager" : null;
    const sql = `SELECT detected_at, club_id, city, country, manager, wallet, club_name FROM transfers ${column ? `WHERE ${column} LIKE ?` : ""} ORDER BY detected_at DESC LIMIT ?`;
    const query = env.DB.prepare(sql);
    const rows = await (column ? query.bind(`%${value}%`, limit) : query.bind(limit)).all<Record<string, string>>();
    if (name === "export_history") {
      const keys = ["detected_at", "club_id", "city", "country", "manager", "wallet", "club_name"];
      const cell = (value: string) => '"' + (/^[=+@-]/.test(value) ? "'" : "") + value.replaceAll('"', '""') + '"';
      return {content: `Latest ${rows.results.length} transfers.`, csv: [keys.join(","), ...rows.results.map(row => keys.map(key => cell(String(row[key] ?? ""))).join(","))].join("\n")};
    }
    return reply(rows.results.length ? rows.results.map(row => `${row.detected_at} | ${row.city}, ${row.country} | ${row.manager} | ${row.club_id}`).join("\n") : "No transfers recorded yet.");
  }
  return reply("Unknown command. Use /help.");
}

export async function verifyDiscordSignature(body: string, signature: string, timestamp: string, publicKey: string): Promise<boolean> {
  if (!/^[0-9a-f]{128}$/i.test(signature) || !/^[0-9a-f]{64}$/i.test(publicKey) || !/^\d+$/.test(timestamp) || Math.abs(Date.now() / 1000 - Number(timestamp)) > 300) return false;
  try {
    const bytes = (hex: string) => Uint8Array.from(hex.match(/../g) ?? [], value => parseInt(value, 16));
    const key = await crypto.subtle.importKey("raw", bytes(publicKey), {name: "Ed25519"}, false, ["verify"]);
    return await crypto.subtle.verify("Ed25519", key, bytes(signature), new TextEncoder().encode(timestamp + body));
  } catch {return false;}
}

export async function handleInteraction(request: Request, env: Env, ctx: ExecutionContext) {
  if (!env.DISCORD_PUBLIC_KEY) return new Response("Bot setup is incomplete", {status: 503});
  const body = await request.text();
  const signature = request.headers.get("X-Signature-Ed25519") ?? "";
  const timestamp = request.headers.get("X-Signature-Timestamp") ?? "";
  if (!await verifyDiscordSignature(body, signature, timestamp, env.DISCORD_PUBLIC_KEY)) return new Response("Invalid signature", {status: 401});
  const interaction = JSON.parse(body) as Interaction;
  if (interaction.application_id !== env.DISCORD_APPLICATION_ID) return new Response("Wrong application", {status: 401});
  if (interaction.type === 1) return Response.json({type: 1});
  if (interaction.type !== 2) return Response.json({type: 4, data: {content: "Unsupported interaction", flags: 64}});
  ctx.waitUntil((async () => {
    let result: {content: string; csv?: string};
    try {result = await commandReply(interaction, env);} catch {result = {content: "Command failed. Check the supplied values and try again."};}
    const data = {content: result.content, allowed_mentions: {parse: []}};
    const form = new FormData();
    form.set("payload_json", JSON.stringify(data));
    if (result.csv) form.set("files[0]", new Blob([result.csv], {type: "text/csv"}), "mfl-transfers.csv");
    try {
      const response = await fetch(`https://discord.com/api/v10/webhooks/${interaction.application_id}/${interaction.token}/messages/@original`, {
        method: "PATCH", body: form, signal: AbortSignal.timeout(10000), redirect: "manual",
      });
      await response.body?.cancel();
      if (!response.ok) console.error(JSON.stringify({event: "command_reply_failed", status: response.status}));
    } catch {console.error(JSON.stringify({event: "command_reply_failed"}));}
  })());
  return Response.json({type: 5, data: {flags: 64}});
}

export async function registerCommands(env: Env) {
  const botToken: unknown = Reflect.get(env, "DISCORD_BOT_TOKEN");
  if (!env.DISCORD_APPLICATION_ID || typeof botToken !== "string" || !botToken) return {ok: false, error: "Bot credentials are not configured"};
  const result = await fetch(`https://discord.com/api/v10/applications/${env.DISCORD_APPLICATION_ID}/commands`, {
    method: "PUT", headers: {"Authorization": `Bot ${botToken}`, "Content-Type": "application/json"},
    body: JSON.stringify(commands), signal: AbortSignal.timeout(12000), redirect: "manual",
  });
  await result.body?.cancel();
  if (result.ok) await env.DB.prepare("INSERT OR REPLACE INTO service_settings(key, value) VALUES('commands_registered', ?)").bind(new Date().toISOString()).run();
  return {ok: result.ok, status: result.status, count: commands.length};
}
