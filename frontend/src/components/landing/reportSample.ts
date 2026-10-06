/**
 * Facts about the committed sample report (public/samples/..., a byte-for-byte copy of
 * demo/i18n-samples/deepdive_cross_session_control_endpoint.both.html). The values are those
 * printed in that file's masthead and contents; they are checked against the file when the
 * landing is verified. The capture and assessment ID equal the hero fixture's, because the same
 * capture always produces the same assessment ID.
 */
export const SAMPLE_REPORT = {
  href: 'samples/deepdive_cross_session_control_endpoint.both.html',
  title: 'Cryptographic Security Posture Assessment',
  assessmentId: '09532eed458ad3a6',
  captureSha256: '97b2b61aa870b74861c606e604f3ecf6f77d8818241817bd22beb814f3dcbe83',
  analysedIso: '2026-10-03T06:00:26Z',
  posture: 'CRITICAL',
  scoreText: '22.15 / 100',
  coverage: '100.0% (12 of 12 sessions assessed)',
  contents: [
    'Executive summary',
    'Assessment scope',
    'Overall security posture',
    'Evidence coverage',
    'Protocol posture',
    'Prioritised findings',
    'Detailed findings',
    'Standards basis',
    'Remediation guidance',
    'AI / ML transparency',
    'Abstentions and observability limits',
    'Assessment limitations',
    'Evidence and provenance',
    'Methodology',
  ],
} as const;
