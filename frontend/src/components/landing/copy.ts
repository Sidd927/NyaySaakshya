/**
 * Landing page strings. Marathi is a DRAFT from the redesign brief: it has not been
 * reviewed by a native speaker (needsReview), the same discipline as the report catalogue.
 * Add Marathi here, never inline, and keep the flag until a person has checked it.
 */
export interface CopyEntry {
  id: string;
  en: string;
  mr?: string;
  needsReview: boolean;
}

export const HERO_COPY = {
  statement: {
    id: 'hero.statement',
    en: 'Understand what the evidence says before it goes to a specialist.',
    mr: 'तज्ज्ञांकडे जाण्यापूर्वी, पुरावा काय सांगतो हे समजून घ्या.',
    needsReview: true,
  },
  explainer: {
    id: 'hero.explainer',
    en: 'First-pass triage of email-traffic evidence. Every finding traces back to the packets, the rule and the standard behind it.',
    needsReview: false,
  },
  cta: {
    id: 'hero.cta',
    en: 'Upload a capture',
    needsReview: false,
  },
  sample: {
    id: 'record.sample',
    en: 'Sample record from a lab-generated capture',
    mr: 'प्रयोगशाळेत तयार केलेल्या कॅप्चरचा नमुना',
    needsReview: true,
  },
} satisfies Record<string, CopyEntry>;

/**
 * Landing sections below the hero. English is written from facts in README.md (the engine's
 * scope and limits) and from the bundled fixtures; nothing here states a statistic or a
 * capability the repository does not document. Marathi is DRAFT (needsReview), same as above.
 */

export const SECTION_TITLES = {
  problem: { id: 'section.problem.heading', en: 'The problem', mr: 'तक्रारी जास्त, तपासणी करणारे तज्ज्ञ कमी.', needsReview: true },
  how: { id: 'section.how.heading', en: 'How it works', mr: 'फाइल अपलोड करा. विश्लेषण आपोआप होते.', needsReview: true },
  evidence: { id: 'section.evidence.heading', en: 'What the evidence shows', mr: 'पुरावा काय सांगतो, आणि काय सांगू शकत नाही.', needsReview: true },
  limits: { id: 'section.limits.heading', en: 'What it does not do', mr: 'ही प्रणाली काय करत नाही.', needsReview: true },
  report: { id: 'section.report.heading', en: 'The report', mr: 'प्रत्येक अहवालावर हॅश आणि वेळेची नोंद.', needsReview: true },
  scope: { id: 'section.scope.heading', en: 'Scope and security', mr: 'ही प्रणाली फक्त फाइल वाचते; कोणत्याही सर्व्हरशी जोडली जात नाही.', needsReview: true },
} satisfies Record<string, CopyEntry>;

/** Marathi narrative lines (one per section that has one). */
export const SECTION_STATEMENTS = {
  problem: {
    id: 'section.problem.statement',
    en: 'Evidence waits for a specialist, and the time to recover it keeps running out.',
    mr: 'पुरावा तज्ज्ञाची वाट पाहत असतो, आणि तो मिळवण्याची वेळ निघून जात असते.',
    needsReview: true,
  },
  evidenceCallout: {
    id: 'section.evidence.callout',
    en: 'Not observable does not mean invalid.',
    mr: 'पाहता येत नाही याचा अर्थ ते चुकीचे आहे असा नाही.',
    needsReview: true,
  },
  limits: {
    id: 'section.limits.statement',
    en: 'What does not appear in the evidence, this system does not state.',
    mr: 'जे पुराव्यात दिसत नाही, ते ही प्रणाली सांगत नाही.',
    needsReview: true,
  },
  reportDraft: {
    id: 'section.report.draftNotice',
    en: 'Marathi reports are a machine draft that no person has reviewed. The English report is authoritative.',
    mr: 'मराठी अहवाल हा यंत्राने तयार केलेला मसुदा आहे; अद्याप कोणीही तपासलेला नाही. इंग्रजी अहवाल प्रमाण मानावा.',
    needsReview: true,
  },
} satisfies Record<string, CopyEntry>;

/** Language labels shown beside the report formats (the same labels the Report tab's toggle uses). */
export const REPORT_LANGUAGE_LABELS = {
  mr: { id: 'section.report.lang.mr', en: 'Marathi', mr: 'मराठी', needsReview: true },
  both: { id: 'section.report.lang.both', en: 'Marathi and English', mr: 'मराठी + English', needsReview: true },
} satisfies Record<string, CopyEntry>;

export const PROBLEM_ROWS: Array<{ term: string; text: string }> = [
  { term: 'Complaints', text: 'District and city cyber cells in Maharashtra receive more cyber-fraud complaints than they have forensic analysts to examine.' },
  { term: 'The queue', text: 'Evidence queues up waiting for a specialist.' },
  { term: 'The window', text: 'While it waits, the forensic window, the period in which evidence is still fresh and recoverable, keeps closing.' },
  { term: 'The first step', text: 'Triage: working out, quickly, what a piece of evidence does and does not establish. Today that step needs scarce expertise.' },
];

export const PROBLEM_CLOSING =
  'NyaySaakshya is built so that a non-specialist can take that first step: upload the evidence, read a ranked result with the proof behind each point, and put a timestamped, hash-verified report in the case file.';

export const HOW_STANDFIRST = 'The sample record above, taken one step at a time.';

export const HOW_STEPS: Array<{ id: string; title: string; text: string }> = [
  { id: 'upload', title: 'Upload a capture', text: 'A .pcap, .pcapng or .cap file. It is hashed with SHA-256 on arrival, and that hash is its identity from then on.' },
  { id: 'analyse', title: 'Passive local analysis', text: 'The file is parsed read-only with TShark, and its TCP streams are rebuilt into SMTP, IMAP and POP3 sessions, including STARTTLS and STLS upgrades. Nothing connects to a server.' },
  { id: 'evidence', title: 'Evidence and findings', text: 'Every fact is stored with an evidence state, a frame reference and its provenance. 19 versioned rules, each cited to an RFC or NIST publication, turn those facts into findings.' },
  { id: 'posture', title: 'Posture assessment', text: 'Findings are fused into one assessment: a score from 0 to 100, a band, coverage and prioritised remediation. Everything after this step reads the assessment and recomputes nothing.' },
  { id: 'report', title: 'Report', text: 'The same assessment is written out as JSON, HTML and PDF, carrying the capture hash and the time of analysis.' },
];

export const EVIDENCE_STANDFIRST =
  'Every fact in an assessment carries one of six states. The state says how much the capture actually establishes.';

export const EVIDENCE_STATE_MEANINGS: Array<{ state: string; text: string }> = [
  { state: 'OBSERVED', text: 'Directly present in the captured bytes.' },
  { state: 'INFERRED', text: 'Deduced from observed facts, with the basis recorded.' },
  { state: 'UNKNOWN', text: 'Not enough evidence to decide. It never improves a score.' },
  { state: 'AMBIGUOUS', text: 'The evidence supports more than one reading.' },
  { state: 'INCOMPLETE', text: 'The capture is cut off at the point that matters.' },
  { state: 'NOT_OBSERVABLE', text: 'Structurally impossible to see in a passive capture, such as a TLS 1.3 certificate (RFC 8446, section 2).' },
];

export const EVIDENCE_CALLOUT_BODY =
  'A certificate that encryption hides is reported as not observable, never as invalid. A capture that shows too little is reported as insufficient evidence, never as a good grade.';

export const EVIDENCE_EXAMPLE_TITLE = 'One capture, three states';
export const EVIDENCE_EXAMPLE_NOTE = 'A TLS 1.3 session from a lab-generated capture. The words beside each row are the engine\'s own.';

export const LIMITS_STANDFIRST =
  'Each limit is a boundary of the method, so a result never claims more than the capture shows.';

export const LIMITS: Array<{ id: string; statement: string; reason: string }> = [
  { id: 'content', statement: 'Does not read message content.', reason: 'Only the protocol exchange is analysed. Credential values are not extracted.' },
  { id: 'attribution', statement: 'Does not attribute an attack to a person.', reason: 'A capture alone cannot tell an attack from a server policy that produces the same bytes.' },
  { id: 'fraud', statement: 'Does not decide that fraud occurred.', reason: 'It tells an examiner what the captured traffic does and does not show.' },
  { id: 'custody', statement: 'Does not establish legal chain of custody.', reason: 'Hashes and provenance support traceability. They are not a chain-of-custody claim.' },
  { id: 'servers', statement: 'Does not connect to mail servers.', reason: 'It reads an uploaded file. There is no live capture and no probing.' },
  { id: 'decrypt', statement: 'Does not decrypt traffic.', reason: 'It needs no keys and no mailbox access. What encryption hides is reported as not observable.' },
];

export const REPORT_STANDFIRST = 'The last step of the chain: the assessment written out as a document that can go into a case file.';

export const REPORT_FACTS: Array<{ term: string; text: string }> = [
  { term: 'Capture identity', text: 'The SHA-256 of the uploaded file.' },
  { term: 'Analysis time', text: 'When the analysis ran, recorded in the report.' },
  { term: 'Assessment ID', text: 'Derived from the evidence, so the same capture and software versions give the same ID.' },
  { term: 'Deterministic bytes', text: 'A stored assessment always renders to the same report bytes, and each report carries its own hash.' },
];

export const REPORT_FORMATS: Array<{ id: string; name: string; text: string; lang?: 'mr' | 'both' }> = [
  { id: 'json', name: 'JSON', text: 'The structured assessment: score, band, coverage, findings with their evidence references, standards and limitations.' },
  { id: 'html', name: 'HTML', text: 'One standalone file with no script, CDN or webfont. It opens from disk and prints cleanly.' },
  { id: 'pdf', name: 'PDF', text: 'Composed from the same report model, not from the HTML. English only.' },
  { id: 'html-mr', name: 'HTML', text: 'The report in Marathi, opening with a short "how to read this report" section. Draft.', lang: 'mr' },
  { id: 'html-both', name: 'HTML', text: 'The Marathi report followed by the unmodified English original, in one file. Draft.', lang: 'both' },
];

export const REPORT_DETERMINISM_NOTE =
  'The sample capture was analysed on 24 Sep 2026 (the record at the top of this page) and again on 3 Oct 2026 (the sample report). Both runs produced assessment 09532eed458ad3a6.';

export const REPORT_DRAFT_EN_EXTRA = 'Every Marathi report says so at the top. PDF and JSON stay English.';

export const SAMPLE_REPORT_LINK = { label: 'Open the sample report', note: 'Marathi and English, Marathi draft. 125 KB, opens in a new tab.' };

export const SCOPE_STANDFIRST = 'It reads an uploaded file and nothing else.';

export const SCOPE_GROUPS: Array<{ id: string; title: string; lines: string[] }> = [
  {
    id: 'examines',
    title: 'What it examines',
    lines: [
      'SMTP, IMAP and POP3 captures, including implicit TLS (SMTPS, IMAPS, POP3S).',
      'TLS version, cipher suite, key exchange and forward secrecy.',
      'STARTTLS and STLS upgrade integrity: is encryption being skipped or stripped?',
      'Plaintext exposure and insecure configuration.',
      'X.509 properties where the handshake is in the clear (TLS 1.2 and earlier).',
    ],
  },
  {
    id: 'out-of-reach',
    title: 'What stays out of reach',
    lines: [
      'TLS 1.3 certificates are encrypted, so they are reported as not observable.',
      'Certificate chain trust and revocation are not assessed: a capture has no trust anchor and no OCSP or CRL access.',
      'Anything outside email protocols. It is not a general-purpose fraud detector.',
      'A capture too thin to show anything is reported as insufficient evidence, not as a good grade.',
    ],
  },
  {
    id: 'runs',
    title: 'How it runs',
    lines: [
      'Passive and offline. It reads the uploaded file and makes no outbound network calls from the analysis code.',
      'Hostile input is expected: TShark runs with an argument array under a timeout, upload size, concurrency and analysis time are limited, and HTML reports escape all content.',
      'Prototype for a single analyst. There is no authentication, so on a public instance analyse test captures only.',
      'An optional anomaly lane is off by default. It can only reorder findings within a severity tier and never changes a finding or the score. On the data tested it has shown no independent detection value.',
    ],
  },
];

/**
 * Closing call to action and footer. One new Marathi string (the closing heading, DRAFT); the
 * action keeps the single label and intent used in the navbar and hero (HERO_COPY.cta).
 */
export const CLOSING = {
  title: { id: 'section.close.heading', en: 'Start with the capture', mr: 'पुराव्यापासून विश्लेषणापर्यंत.', needsReview: true },
  standfirst: 'Upload a capture file. The analysis runs on its own, and every finding traces back to the packets behind it.',
  chainLabel: 'The chain from capture to report',
  chain: ['Capture', 'Analysis', 'Evidence', 'Finding', 'Posture', 'Report'],
  caution: 'There is no authentication. On a public instance, upload test captures only.',
} satisfies { title: CopyEntry; standfirst: string; chainLabel: string; chain: string[]; caution: string };

export const FOOTER = {
  scope: 'Forensic triage of email-traffic evidence: SMTP, IMAP and POP3 captures, analysed passively and offline.',
  note: 'A prototype for a single analyst. The English report is authoritative; the Marathi report is a machine draft that no person has reviewed.',
  navLabel: 'On this page',
  reportTitle: 'Sample report',
  top: 'Back to top',
};
