import React from 'react';
import { EvidenceBadge } from '../common/EvidenceBadge';
import { PosturePill } from '../common/PosturePill';
import { SeverityBadge } from '../common/SeverityBadge';
import { HERO_COPY } from './copy';
import { HashBlock } from './HashBlock';
import type { SampleRecord } from './recordData';

const money = (n: number) => n.toFixed(2);

/**
 * One real analysis, read top to bottom: capture, analysis, evidence, finding, posture,
 * report. Severity, posture and evidence-state rendering is the workbench's own components;
 * nothing here defines a status colour.
 */
export const EvidenceRecord: React.FC<{ record: SampleRecord }> = ({ record }) => {
  const { finding, posture } = record;
  const findingMeta = [
    `${finding.affectedSessions} of ${record.sessionsTotal} sessions`,
    finding.frame !== null ? `frame ${finding.frame}` : null,
    finding.ruleId ? `rule ${finding.ruleId}` : null,
  ].filter(Boolean).join(', ');

  return (
    <aside className="sms-record" aria-labelledby="sms-record-title">
      <header className="sms-record__head">
        <h2 id="sms-record-title" className="sms-record__title">{HERO_COPY.sample.en}</h2>
        <p className="sms-record__title-mr sms-mr" lang="mr">{HERO_COPY.sample.mr}</p>
      </header>

      <ol className="sms-record__flow">
        <li className="sms-record__row">
          <span className="sms-record__label">Capture</span>
          <div className="sms-record__value">
            <code className="sms-record__file" translate="no">
              {record.fileName.split('_').map((part, i, all) => (
                <React.Fragment key={i}>{part}{i < all.length - 1 ? <>_<wbr /></> : null}</React.Fragment>
              ))}
            </code>
            <HashBlock value={record.captureSha256} />
            <span className="sms-record__note">SHA-256 of the file</span>
          </div>
        </li>

        <li className="sms-record__row">
          <span className="sms-record__label">Analysis</span>
          <div className="sms-record__value">
            <span className="sms-record__strong">{record.analysedIst}</span>
            <span className="sms-record__note">
              {record.analysedUtc}. {record.sessionsAssessed} of {record.sessionsTotal} sessions assessed
            </span>
          </div>
        </li>

        {record.observations.length > 0 && (
          <li className="sms-record__row">
            <span className="sms-record__label">Evidence</span>
            <div className="sms-record__value">
              <span className="sms-record__badges">
                {record.observations.map((o) => (
                  <EvidenceBadge key={o.state} state={o.state} count={o.count} size="sm" />
                ))}
              </span>
              <span className="sms-record__note">Every fact carries a state</span>
            </div>
          </li>
        )}

        <li className="sms-record__row">
          <span className="sms-record__label">Finding</span>
          <div className="sms-record__value">
            <span className="sms-record__finding">
              <SeverityBadge severity={finding.severity} size="sm" />
              <span className="sms-record__strong">{finding.title}</span>
            </span>
            <span className="sms-record__note">
              {findingMeta}
              {finding.moreFindings > 0 ? `. ${finding.moreFindings} more ${finding.moreFindings === 1 ? 'finding' : 'findings'}` : ''}
            </span>
          </div>
        </li>

        <li className="sms-record__row">
          <span className="sms-record__label">Posture</span>
          <div className="sms-record__value">
            <span className="sms-record__posture">
              <PosturePill band={posture.band} size="md" />
              <span className="sms-record__score">{posture.scoreText}</span>
            </span>
            <span className="sms-record__note">
              {posture.startingValue} minus {money(posture.totalPenalty)}, from {posture.issueGroups} issue groups
            </span>
          </div>
        </li>

        <li className="sms-record__row">
          <span className="sms-record__label">Report</span>
          <div className="sms-record__value">
            <code className="sms-record__file" translate="no">{record.assessmentId}</code>
            <span className="sms-record__note">Assessment ID. JSON, HTML and PDF</span>
          </div>
        </li>
      </ol>

      {record.limitation && (
        <p className="sms-record__limit">
          <span className="sms-record__limit-label">Stated limit</span>
          {record.limitation}
        </p>
      )}
    </aside>
  );
};
