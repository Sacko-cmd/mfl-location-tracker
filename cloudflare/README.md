# Cloudflare location tracker

Live status: https://mfl-location-tracker-cloudflare.ricky-hyde-selling.workers.dev/status
API connectivity diagnostics: https://mfl-location-tracker-cloudflare.ricky-hyde-selling.workers.dev/diagnostics

This is a Cloudflare Workers port of the location-pool tracker, deployed separately
from the Python Render app. It polls once per minute and stores its baseline,
pending departures, transfer history, and notification outbox in Cloudflare D1.
It confirms three missing polls before looking up the club's current owner directly.
No leaderboard scan is required to resolve an owner.

The initial successful poll only seeds ownership. Malformed/failed pool responses
do not replace the baseline. Reappearance resets a departure's missing counter.
Failed owner lookups remain pending; at most ten are attempted per tick, with
rotation so failures do not indefinitely block other departures. Pending departures
older than six hours are dropped when processed, matching the Python app policy.
The scheduled handler uses a database lease and minimum interval to avoid counting
concurrent/duplicate invocations as separate missing polls.

Confirmed transfers and the updated baseline commit in one D1 batch. Notifications
are sent from a durable outbox; failed sends are retried with backoff on subsequent scheduled runs. Discord delivery is at least once: a crash after Discord accepts a message
but before the database update can produce a duplicate. With no webhook configured,
transfers are recorded as `not_configured` and are not backfilled automatically.

## Scope

Club licence departures from the central pool and the shared Discord webhook are
active. Player, club, and pack marketplace listing alerts are disabled and have no
scheduled poller or configuration routes in this Worker.

The port provides Discord slash commands for licence lookup, search, ownership,
history, recent purchases, pool/status queries, and personal licence watchlists.
These require a configured Discord application before becoming available; check
`discord_bot_commands` in live status. The original Python prefix bot is separate.
The Render owner should disable its location polling to avoid duplicate alerts.

### Discord application setup

Set `DISCORD_APPLICATION_ID` and `DISCORD_PUBLIC_KEY` in Wrangler configuration,
store the application's bot token with `wrangler secret put DISCORD_BOT_TOKEN`,
and deploy. Set the application's Interactions Endpoint URL to the Worker's
`/interactions` endpoint. Requests are verified using Discord's Ed25519 signature.
Call `POST /setup-discord` with the administrative bearer token to register slash
commands, then install the application in the intended Discord server.

Search commands include `/club`, `/search`, `/history`, `/manager`, `/recent`,
`/wallet`, `/pending`, `/stats`, `/poollog`, and `/export_history`. `/help` lists
available commands. Watchlist commands concern club licences only.

## Development and deployment

```sh
npm ci
npm run check
npm test
npx wrangler d1 migrations apply mfl-location-tracker-cloudflare --local
npx wrangler dev --test-scheduled
```

For local testing, create an ignored `.dev.vars` containing `ADMIN_TOKEN` and
`DISCORD_WEBHOOK_URL`. Use an empty webhook for tests that must not send alerts.

The production account, D1 binding, and cron are specified in `wrangler.jsonc`.
To deploy an update to the existing service:

```sh
npx wrangler d1 migrations apply mfl-location-tracker-cloudflare --remote
npx wrangler deploy --dry-run
npx wrangler deploy
```

The webhook and a random administrative token are Cloudflare secrets, not files
in this repository. Set/rotate them with `wrangler secret put DISCORD_WEBHOOK_URL`
and `wrangler secret put ADMIN_TOKEN`. Cron configuration can take several minutes
to propagate.

## Endpoints

- `GET /status` (also `/` and `/health`): stored poll status, pool/pending counts,
  notification configuration, and delivery counts. A successful poll within three
  minutes with no latest error reports healthy. HTTP 200 is liveness, so inspect
  `healthy` and `status` for operational health.
- `GET /diagnostics`: four fixed read-only MFL API probes, cached for 60 seconds.
  No caller-selected URLs or credentials are accepted.
- `POST /poll`: manually run a poll; requires `Authorization: Bearer <ADMIN_TOKEN>`.
- `POST /verify-webhook`: validate the configured webhook with a read-only Discord
  request; requires the same administrative authorization. It sends no message.

- `POST /test-alert`: idempotent setup test, requiring administrative authorization.
  A successful send records Discord's message ID and channel ID in D1.
- `POST /setup-discord`: register application commands; administrative authorization.
- `POST /interactions`: signature-verified Discord interaction endpoint.

Status responses never reveal webhook or administrative credentials. Delivery
requires Discord to acknowledge a saved message, and receipts are persisted.
A setup-test receipt proves connectivity; it does not represent a real purchase.
