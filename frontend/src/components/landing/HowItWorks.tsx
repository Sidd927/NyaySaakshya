import React from 'react';
import { EvidenceBadge } from '../common/EvidenceBadge';
import { PosturePill } from '../common/PosturePill';
import { SeverityBadge } from '../common/SeverityBadge';
import { FileName } from './FileName';
import { HOW_STANDFIRST, HOW_STEPS, SECTION_TITLES } from './copy';
import type { SampleRecord } from './recordData';
import { Section, SectionHead } from './Section';
import { useRevealOnce } from './useRevealOnce';

const shortHash = (hash: string) => `${hash.slice(0, 8)}…${hash.slice(-8)}`;

/** What the sample record shows at each step. Only fixture values; no record, no proof. */
const Proof: React.FC<{ stepId: string; record: SampleRecord }> = ({ stepId, record }) => {
  switch (stepId) {
    case 'upload':
      return (
        <>
          <FileName name={record.fileName} className="sms-how__mono" />
          <code className="sms-how__mono" translate="no" title={record.captureSha256}>{shortHash(record.captureSha256)}</code>
        </>
      );
    case 'analyse':
      return (
        <>
          <span className="sms-how__strong">{record.sessionsAssessed} of {record.sessionsTotal} sessions assessed</span>
          <span className="sms-how__muted">{record.analysedIst}</span>
        </>
      );
    case 'evidence':
      return (
        <>
          <span className="sms-how__badges">
            {record.observations.map((o) => <EvidenceBadge key={o.state} state={o.state} count={o.count} size="sm" />)}
          </span>
          <span className="sms-how__finding">
            <SeverityBadge severity={record.finding.severity} size="sm" />
            <span className="sms-how__strong">{record.finding.title}</span>
          </span>
        </>
      );
    case 'posture':
      return (
        <span className="sms-how__posture">
          <PosturePill band={record.posture.band} size="md" />
          <span className="sms-how__score">{record.posture.scoreText}</span>
        </span>
      );
    case 'report':
      return (
        <>
          <code className="sms-how__mono" translate="no">{record.assessmentId}</code>
          <span className="sms-how__muted">Assessment ID</span>
        </>
      );
    default:
      return null;
  }
};

/**
 * The five real steps as one traceable line. The line is drawn once as it scrolls into view,
 * step by step, because it is the one thing on the page that moves: evidence flowing on.
 */
export const HowItWorks: React.FC<{ record: SampleRecord | null }> = ({ record }) => {
  const [ref, reveal] = useRevealOnce<HTMLOListElement>();
  return (
    <Section id="landing-how" navigable>
      <SectionHead sectionId="landing-how" title={SECTION_TITLES.how} standfirst={HOW_STANDFIRST} />
      <ol className="sms-how__list" ref={ref} data-reveal={reveal}>
        {HOW_STEPS.map((step, index) => (
          <li className="sms-how__step" key={step.id}>
            <span className="sms-how__num" aria-hidden="true">{String(index + 1).padStart(2, '0')}</span>
            <div className="sms-how__body">
              <div>
                <h3 className="sms-how__title">{step.title}</h3>
                <p className="sms-how__text">{step.text}</p>
              </div>
              {record && (
                <div className="sms-how__proof">
                  <Proof stepId={step.id} record={record} />
                </div>
              )}
            </div>
          </li>
        ))}
      </ol>
    </Section>
  );
};
