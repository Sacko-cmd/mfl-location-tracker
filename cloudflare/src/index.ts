import {handleInteraction, registerCommands} from "./bot";
import {testAlert, flushNotifications} from "./discord";
import {timingSafeEqual} from "node:crypto";
import {diagnostics} from "./diagnostics";
import {runPoll, status} from "./tracker";

function authorized(request: Request, env: Env) {
  if (!env.ADMIN_TOKEN) return false;
  const supplied = new TextEncoder().encode(request.headers.get("Authorization") ?? "");
  const expected = new TextEncoder().encode(`Bearer ${env.ADMIN_TOKEN}`);
  return supplied.length === expected.length && timingSafeEqual(supplied, expected);
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (url.pathname === "/interactions" && request.method === "POST") return handleInteraction(request, env, ctx);
    if (url.pathname === "/setup-discord" && request.method === "POST") {
      if (!authorized(request, env)) return new Response("Unauthorized", {status: 401});
      return Response.json(await registerCommands(env));
    }
    if (request.method === "POST" && url.pathname === "/verify-webhook") {
      if (!authorized(request, env)) return new Response("Unauthorized", {status: 401});
      if (!env.DISCORD_WEBHOOK_URL) return Response.json({configured: false}, {status: 400});
      const webhook = new URL(env.DISCORD_WEBHOOK_URL);
      if (webhook.protocol !== "https:" || webhook.hostname !== "discord.com" || !webhook.pathname.startsWith("/api/webhooks/")) {
        return Response.json({valid: false}, {status: 400});
      }
      const result = await fetch(webhook, {redirect: "manual", signal: AbortSignal.timeout(10000)});
      await result.body?.cancel();
      return Response.json({valid: result.ok, status: result.status}, {headers: {"Cache-Control": "no-store"}});
    }
    if (request.method === "POST" && url.pathname === "/test-alert") {
      if (!authorized(request, env)) return new Response("Unauthorized", {status: 401});
      return Response.json(await testAlert(env), {headers: {"Cache-Control": "no-store"}});
    }
    if (request.method === "POST" && url.pathname === "/poll") {
      if (!authorized(request, env)) return new Response("Unauthorized", {status: 401});
      return Response.json(await runPoll(env), {headers: {"Cache-Control": "no-store"}});
    }
    if (request.method !== "GET") return new Response("Method not allowed", {status: 405});
    try {
      if (["/", "/status", "/health"].includes(url.pathname)) {
        return Response.json(await status(env), {headers: {"Cache-Control": "no-store"}});
      }
      if (url.pathname === "/diagnostics") {
        const cacheKey = new Request(`${url.origin}/diagnostics-v1`);
        const cached = await caches.default.match(cacheKey);
        if (cached) return cached;
        const response = Response.json(await diagnostics(), {headers: {"Cache-Control": "public, max-age=60"}});
        ctx.waitUntil(caches.default.put(cacheKey, response.clone()));
        return response;
      }
      return new Response("Not found", {status: 404});
    } catch {
      return Response.json({status: "error", message: "Storage unavailable"}, {status: 503});
    }
  },
  async scheduled(_controller, env) {
    await runPoll(env);
    await flushNotifications(env);
  },
} satisfies ExportedHandler<Env>;
