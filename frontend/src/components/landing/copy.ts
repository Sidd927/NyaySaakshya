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
