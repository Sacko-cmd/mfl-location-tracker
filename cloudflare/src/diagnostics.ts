export const headers = {
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
  "Accept": "application/json",
  "Origin": "https://app.playmfl.com",
  "Referer": "https://app.playmfl.com/",
};

const endpoints = {
  pool: "https://api.playmfl.com/clubs?walletAddress=0xf45dfaa6233fae44",
  leaderboard: "https://api.playmfl.com/leaderboards/users/global?sort=nbMflPoints&sortOrder=DESC&limit=20&offset=0",
  club: "https://api.playmfl.com/clubs/35",
  marketplace: "https://api.playmfl.com/listings?limit=1&type=CLUB&status=AVAILABLE&view=full",
};

export async function readBounded(response: Response): Promise<string> {
  if (!response.body) return "";
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let size = 0;
  let text = "";
  try {
    while (true) {
      const {done, value} = await reader.read();
      if (done) break;
      size += value.byteLength;
      if (size > 4 * 1024 * 1024) throw new Error("Response exceeds diagnostic limit");
      text += decoder.decode(value, {stream: true});
    }
    return text + decoder.decode();
  } finally {
    await reader.cancel();
  }
}

async function probe(name: string, url: string) {
  const start = Date.now();
  try {
    const response = await fetch(url, {
      headers, redirect: "manual", signal: AbortSignal.timeout(20000),
    });
    const body = await readBounded(response);
    let count: number | null = null;
    let validJson = false;
    try {
      const data = JSON.parse(body);
      validJson = true;
      count = Array.isArray(data) ? data.length : Array.isArray(data?.users) ? data.users.length : null;
    } catch { /* Report HTML challenges without treating them as API data. */ }
    return {
      name, status: response.status, ok: response.ok && validJson,
      content_type: response.headers.get("content-type"),
      server: response.headers.get("server"),
      mitigation: response.headers.get("cf-mitigated"),
      ray: response.headers.get("cf-ray"),
      count, valid_json: validJson,
      error_title: response.ok ? null : body.match(/<title>([^<]{0,200})<\/title>/i)?.[1] ?? null,
      elapsed_ms: Date.now() - start,
    };
  } catch (error) {
    return {name, ok: false, error: error instanceof Error ? error.message : "Request failed", elapsed_ms: Date.now() - start};
  }
}

export async function diagnostics() {
  const results = await Promise.all(Object.entries(endpoints).map(([name, endpoint]) => probe(name, endpoint)));
  return {checked_at: new Date().toISOString(), all_ok: results.every(result => result.ok), results};
}
