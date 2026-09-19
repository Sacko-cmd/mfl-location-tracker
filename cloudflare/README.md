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
are sent from a durable outbox; failed sends are retried on subsequent successful
polls. Discord delivery is at least once: a crash after Discord accepts a message
but before the database update can produce a duplicate. With no webhook configured,
transfers are recorded as `not_configured` and are not backfilled automatically.

## Scope

Location tracking and the shared Discord webhook are active. The Python Discord
prefix-command bot, per-user registrations/watchlists, and marketplace monitor
backend are not part of this port. The existing Render service and extension URL
are unchanged. Do not run two active location-alert services against the same
webhook unless duplicate alerts are acceptable. The Render owner should disable
its location polling after this replacement is accepted.

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

Status responses never reveal the webhook or administrative token. Real Discord
alert delivery is verified only when a transfer is detected and `delivery` becomes
`sent`; validating a webhook alone does not prove a message was delivered.
