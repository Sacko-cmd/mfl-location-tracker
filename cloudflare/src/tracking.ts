export interface Club {
  id: string;
  city: string;
  country: string;
  missingSince?: string;
  missingPolls?: number;
  lastLookup?: number;
}
export type Pool = Record<string, Club>;

export function parsePool(data: unknown): Pool {
  if (!Array.isArray(data)) throw new Error("Invalid pool response: expected an array");
  const pool: Pool = {};
  for (const item of data) {
    const club = item?.club;
    if (!club || !/^[0-9]+$/.test(String(club.id)) || typeof club.city !== "string" || typeof club.country !== "string") {
      throw new Error("Invalid club in pool response");
    }
    pool[String(club.id)] = {id: String(club.id), city: club.city, country: club.country};
  }
  return pool;
}

export function comparePools(previous: Pool, current: Pool, now: string) {
  const next: Pool = {...current};
  const missing: Club[] = [];
  for (const club of Object.values(previous)) {
    if (current[club.id]) continue;
    const ghost = {...club, missingSince: club.missingSince ?? now, missingPolls: (club.missingPolls ?? 0) + 1};
    next[club.id] = ghost;
    missing.push(ghost);
  }
  return {next, missing};
}
