import React from 'react';
import { EvidenceBadge } from '../common/EvidenceBadge';
import { PosturePill } from '../common/PosturePill';
import { FileName } from './FileName';
import {
  EVIDENCE_CALLOUT_BODY, EVIDENCE_EXAMPLE_NOTE, EVIDENCE_EXAMPLE_TITLE, EVIDENCE_STANDFIRST,
  EVIDENCE_STATE_MEANINGS, SECTION_STATEMENTS, SECTION_TITLES,
} from './copy';
import type { HonestyExample } from './recordData';
import { Section, SectionHead } from './Section';

/**
 * The six evidence states as a classification, with the workbench's own EvidenceBadge so the
 * border grammar (solid, dashed, dotted) and ink are exactly what an analyst will see. The worked
 * example is one real session that carries three of them at once.
 */
export const EvidenceStates: React.FC<{ example: HonestyExample | null }> = ({ example }) => (
  <Section id="landing-evidence" navigable>
    <SectionHead sectionId="landing-evidence" title={SECTION_TITLES.evidence} standfirst={EVIDENCE_STANDFIRST} />
    <div className="sms-ev__grid">
      <div className="sms-ev__main">
        <ul className="sms-states">
          {EVIDENCE_STATE_MEANINGS.map((row) => (
            <li className="sms-states__row" key={row.state} data-key={row.state === 'NOT_OBSERVABLE' ? 'true' : undefined}>
              <span className="sms-states__badge"><EvidenceBadge state={row.state} /></span>
              <p className="sms-states__text">{row.text}</p>
            </li>
          ))}
        </ul>
        <div className="sms-callout">
          <p className="sms-callout__en">{SECTION_STATEMENTS.evidenceCallout.en}</p>
          <p className="sms-callout__mr sms-mr" lang="mr">{SECTION_STATEMENTS.evidenceCallout.mr}</p>
          <p className="sms-callout__body">{EVIDENCE_CALLOUT_BODY}</p>
        </div>
      </div>

      {example && (
        <aside className="sms-example" aria-labelledby="sms-example-title">
          <header className="sms-example__head">
            <h3 id="sms-example-title" className="sms-example__title">{EVIDENCE_EXAMPLE_TITLE}</h3>
            <p className="sms-example__note">{EVIDENCE_EXAMPLE_NOTE}</p>
            <FileName name={example.fileName} className="sms-example__file" />
          </header>
          <ul className="sms-example__rows">
            {example.rows.map((row) => (
              <li className="sms-example__row" key={row.label}>
                <div className="sms-example__top">
                  <span className="sms-example__label">{row.label}</span>
                  <EvidenceBadge state={row.state} size="sm" />
                </div>
                <div className="sms-example__value">
                  <code translate="no">{row.value}</code>
                  {row.frame !== null && <span className="sms-example__frame">frame {row.frame}</span>}
                </div>
                {/* The engine's own words, verbatim: this box is labelled as such. */}
                <p className="sms-example__basis">{row.basis}</p>
              </li>
            ))}
          </ul>
          <footer className="sms-example__foot">
            <PosturePill band={example.posture.band} size="md" />
            <span className="sms-example__score">{example.posture.scoreText}</span>
            {example.certificateWhy && <p className="sms-example__why">{example.certificateWhy}</p>}
          </footer>
        </aside>
      )}
    </div>
  </Section>
);
