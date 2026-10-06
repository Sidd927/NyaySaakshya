import type { FixtureData } from '../../fixtures';

/**
 * The hero's sample record, read from a bundled real-pipeline fixture. Every value below
 * is copied or derived (never typed by hand); if a field is missing the record is not built
 * and the hero omits the card rather than showing an invented number.
 */
export interface SampleRecord {
  fileName: string;
  captureSha256: string;
  sessionsTotal: number;
  sessionsAssessed: number;
  analysedIst: string;
  analysedUtc: string;
  observations: Array<{ state: string; count: number }>;
  finding: {
    title: string;
    severity: string;
    affectedSessions: number;
    frame: number | null;
    ruleId: string | null;
    moreFindings: number;
  };
  posture: {
    band: string;
    scoreText: string;
    startingValue: number;
    totalPenalty: number;
    issueGroups: number;
  };
  assessmentId: string;
  limitation: string | null;
}

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
const pad = (n: number) => String(n).padStart(2, '0');
const isStr = (v: unknown): v is string => typeof v === 'string' && v.length > 0;
const isNum = (v: unknown): v is number => typeof v === 'number' && Number.isFinite(v);

/**
 * India Standard Time is UTC+05:30 with no daylight saving, so a fixed offset is exact.
 * Done by arithmetic, not Intl, so the text is identical in every browser and locale.
 */
export function formatAnalysisTime(iso: string): { ist: string; utc: string } | null {
  const t = Date.parse(iso);
  if (Number.isNaN(t)) return null;
  const u = new Date(t);
  const i = new Date(t + 330 * 60_000);
  const clock = (d: Date) => `${pad(d.getUTCHours())}:${pad(d.getUTCMinutes())}:${pad(d.getUTCSeconds())}`;
  const date = (d: Date) => `${d.getUTCDate()} ${MONTHS[d.getUTCMonth()]} ${d.getUTCFullYear()}`;
  const sameDay = date(u) === date(i);
  return {
    ist: `${date(i)}, ${clock(i)} IST`,
    utc: `${sameDay ? '' : `${date(u)}, `}${clock(u)} UTC`,
  };
}

const OBSERVATION_ORDER = ['OBSERVED', 'AMBIGUOUS', 'UNKNOWN'];

export function buildSampleRecord(fixture: FixtureData | undefined): SampleRecord | null {
  if (!fixture) return null;
  const { run, assessment, dashboard } = fixture;
  const posture = dashboard?.posture;
  const identity = dashboard?.identity;
  const coverage = dashboard?.coverage;
  const top = dashboard?.findings?.[0];

  const captureSha256 = assessment?.capture_id;
  const when = formatAnalysisTime(identity?.generated_at ?? run?.created_at);
  if (
    !isStr(run?.source_filename) || !isStr(captureSha256) || !/^[0-9a-f]{64}$/.test(captureSha256) ||
    !when || !isStr(identity?.assessment_id) || !top || !isStr(top.title) || !isStr(top.severity) ||
    !isNum(top.affected_sessions) || !isStr(posture?.value) || !isStr(posture?.score_text) ||
    !isNum(posture?.starting_value) || !isNum(posture?.total_penalty) || !Array.isArray(posture?.components) ||
    !isNum(coverage?.sessions_total) || !isNum(coverage?.sessions_assessed)
  ) {
    return null;
  }

  const counts: Record<string, unknown> = coverage.observation_counts ?? {};
  const observations = OBSERVATION_ORDER
    .filter((state) => isNum(counts[state]))
    .map((state) => ({ state, count: counts[state] as number }));

  return {
    fileName: run.source_filename,
    captureSha256,
    sessionsTotal: coverage.sessions_total,
    sessionsAssessed: coverage.sessions_assessed,
    analysedIst: when.ist,
    analysedUtc: when.utc,
    observations,
    finding: {
      title: top.title,
      severity: top.severity,
      affectedSessions: top.affected_sessions,
      frame: Array.isArray(top.frames) && isNum(top.frames[0]) ? top.frames[0] : null,
      ruleId: Array.isArray(top.source_rule_ids) && isStr(top.source_rule_ids[0]) ? top.source_rule_ids[0] : null,
      moreFindings: Math.max(0, (dashboard.findings?.length ?? 1) - 1),
    },
    posture: {
      band: posture.value,
      scoreText: posture.score_text,
      startingValue: posture.starting_value,
      totalPenalty: posture.total_penalty,
      issueGroups: posture.components.length,
    },
    assessmentId: identity.assessment_id,
    limitation: isStr(dashboard.limitations?.[0]) ? dashboard.limitations[0] : null,
  };
}

/**
 * Evidence section's worked example: one real session that carries several evidence states at
 * once (scene_b_certificate_honesty). Every value is read from the fixture; a missing field
 * drops its row, and no row is ever invented.
 */
export interface HonestyExample {
  fileName: string;
  posture: { band: string; scoreText: string };
  rows: Array<{ label: string; state: string; value: string; basis: string; frame: number | null }>;
  certificateWhy: string | null;
}

const EXAMPLE_FIELDS: Array<{ key: string; label: string }> = [
  { key: 'tls_negotiated_version', label: 'TLS version' },
  { key: 'tls_forward_secrecy', label: 'Forward secrecy' },
  { key: 'tls_certificate_chain', label: 'Certificate chain' },
];

export function buildHonestyExample(fixture: FixtureData | undefined): HonestyExample | null {
  if (!fixture) return null;
  const posture = fixture.dashboard?.posture;
  const evidence = fixture.sessions?.items?.[0]?.evidence;
  if (!isStr(fixture.run?.source_filename) || !isStr(posture?.value) || !isStr(posture?.score_text) || !evidence) return null;

  const rows = EXAMPLE_FIELDS.flatMap(({ key, label }) => {
    const field = evidence[key];
    if (!field || !isStr(field.state) || !isStr(field.basis)) return [];
    const value = field.value === null || field.value === undefined ? 'none' : String(field.value);
    const frame = Array.isArray(field.frames) && isNum(field.frames[0]) ? field.frames[0] : null;
    return [{ label, state: field.state, value, basis: field.basis, frame }];
  });
  if (rows.length === 0) return null;

  const why = fixture.dashboard?.abstentions?.find((a: { reason?: string }) => a?.reason === 'NOT_OBSERVABLE')?.why;
  return {
    fileName: fixture.run.source_filename,
    posture: { band: posture.value, scoreText: posture.score_text },
    rows,
    certificateWhy: isStr(why) ? why : null,
  };
}
