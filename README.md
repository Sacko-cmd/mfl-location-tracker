# mfl-location-tracker

Tracks MFL location NFTs leaving a central Flowty wallet, matches the city to an MFL manager wallet scan, and sends Discord alerts for watched locations.

## How it works

1. **Flowty poll** — every 60 seconds, reads NFTs in the central wallet from Flowty.
2. **Change detection** — compares the current list to `ownership.json` and finds locations that disappeared from the wallet.
3. **MFL match** — scans MFL manager wallets (from the global leaderboard cache) to find who now owns that city.
4. **Watchlist filter** — only alerts for cities/countries/club IDs in `watchlist.json` (defaults to watch all cities).
5. **Discord alert** — sends a rich embed via `DISCORD_WEBHOOK_URL`.
6. **Optional bot** — if `DISCORD_TOKEN` is set, `/ping` and `/history` commands are also available.

On Render, a small Flask app keeps the service alive and exposes `/health`.

## Render setup

### 1. Push these fixes to GitHub

Commit and push the updated repo to `Sacko-cmd/mfl-location-tracker`.

### 2. Create the web service

In [Render](https://render.com):

1. **New → Web Service**
2. Connect the GitHub repo
3. Use these settings:

| Setting | Value |
| --- | --- |
| Root Directory | *(leave blank)* |
| Environment | `Python 3` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `python app.py` |
| Health Check Path | `/health` |

Or deploy from the blueprint file at `render.yaml` in the repo root.

### 3. Environment variables

Add these in Render → Environment:

| Variable | Required | Purpose |
| --- | --- | --- |
| `DISCORD_WEBHOOK_URL` | **Yes** (for alerts) | Discord channel webhook URL |
| `DISCORD_TOKEN` | No | Enables `/ping` and `/history` bot commands |
| `PORT` | No | Set automatically by Render |

#### Create a Discord webhook

1. Open your Discord server → channel settings → **Integrations** → **Webhooks**
2. Create a webhook and copy the URL
3. Paste it as `DISCORD_WEBHOOK_URL` in Render

#### Optional Discord bot token

Only needed if you want slash/prefix commands. Create a bot in the [Discord Developer Portal](https://discord.com/developers/applications), enable **Message Content Intent** if needed, invite it to your server, and set `DISCORD_TOKEN`.

### 4. Deploy and verify

After deploy:

1. Open `https://your-service.onrender.com/` — should show `MFL Tracker Running`
2. Open `https://your-service.onrender.com/health` — should return JSON with `"status": "ok"`
3. Check Render logs for:
   - `Starting MFL tracker...`
   - `Wallet refresh complete.`
   - `Starting scheduler...`

The first wallet cache build can take a few minutes while it paginates the MFL leaderboard.

## Local run

```bash
cd mfl-location-tracker
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python app.py
```

Visit `http://localhost:10000/health`.

## Watchlist

`watchlist.json` is created automatically with:

```json
{
  "cities": ["*"],
  "countries": [],
  "club_ids": [],
  "paused": false
}
```

Use `"*"` in `cities` to watch all locations, or replace with specific city names.

## Marketplace monitors (Chrome extension)

The `extension/` folder is the MFL Marketplace Monitor UI. It talks to the same Render service as the location tracker (`/monitors` API).

1. Load `extension/` as an unpacked Chrome extension (`chrome://extensions`)
2. The server URL is pre-set to `https://mfl-location-tracker.onrender.com`
3. Add monitors from MFL marketplace tabs as before — alerts go to your Discord webhook

Each Chrome install is limited to **5 monitors** at a time. Delete one before adding another.

After deploying this merged service, **suspend the old `mflmarketnotifictions` Render service** so you are not billed two free-tier instance hour pools.

## Notes for Render free tier

- One web service runs both the location tracker and marketplace polling (~720 instance hours/month).
- Local JSON/SQLite files reset when the service restarts or redeploys.
- On restart, the tracker re-seeds ownership state on the next poll without sending false alerts.
- For long-term history across restarts, you'd eventually want Render persistent disk or an external database.
