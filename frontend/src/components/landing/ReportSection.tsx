import React from 'react';
import { ExternalLink } from 'lucide-react';
import { PosturePill } from '../common/PosturePill';
import {
  REPORT_DETERMINISM_NOTE, REPORT_DRAFT_EN_EXTRA, REPORT_FACTS, REPORT_FORMATS, REPORT_LANGUAGE_LABELS,
  REPORT_STANDFIRST, SAMPLE_REPORT_LINK, SECTION_STATEMENTS, SECTION_TITLES,
} from './copy';
import { HashBlock } from './HashBlock';
import { formatAnalysisTime } from './recordData';
import { SAMPLE_REPORT } from './reportSample';
import { Section, SectionHead } from './Section';

/**
 * The report as the last link of the chain. The preview is the sample report's own masthead and
 * contents (checked against the file), not a drawing, and the link opens that file unchanged.
 */
export const ReportSection: React.FC = () => {
  const when = formatAnalysisTime(SAMPLE_REPORT.analysedIso);
  return (
    <Section id="landing-reports" navigable>
      <SectionHead sectionId="landing-reports" title={SECTION_TITLES.report} standfirst={REPORT_STANDFIRST} />
      <div className="sms-rep__split">
        <figure className="sms-samplereport" aria-label="Structure of the sample report">
          <figcaption className="sms-samplereport__caption">From the sample report</figcaption>
          <div className="sms-samplereport__page">
            <p className="sms-samplereport__brand">NyaySaakshya</p>
            <p className="sms-samplereport__subject">{SAMPLE_REPORT.title}</p>
            <dl className="sms-samplereport__fields">
              <div><dt>Assessment</dt><dd><code translate="no">{SAMPLE_REPORT.assessmentId}</code></dd></div>
              <div className="sms-samplereport__field--stack"><dt>Capture</dt><dd><HashBlock value={SAMPLE_REPORT.captureSha256} /></dd></div>
              <div><dt>Analysed</dt><dd>{when ? `${when.ist} (${when.utc})` : SAMPLE_REPORT.analysedIso}</dd></div>
              <div>
                <dt>Overall posture</dt>
                <dd><span className="sms-samplereport__posture"><PosturePill band={SAMPLE_REPORT.posture} size="sm" /><span className="sms-samplereport__score">{SAMPLE_REPORT.scoreText}</span></span></dd>
              </div>
              <div><dt>Evidence coverage</dt><dd>{SAMPLE_REPORT.coverage}</dd></div>
            </dl>
            <ol className="sms-samplereport__contents">
              {SAMPLE_REPORT.contents.map((name) => <li key={name}>{name}</li>)}
            </ol>
          </div>
        </figure>

        <div className="sms-rep__main">
          <dl className="sms-rep__facts">
            {REPORT_FACTS.map((fact) => (
              <div className="sms-rep__fact" key={fact.term}>
                <dt>{fact.term}</dt>
                <dd>{fact.text}</dd>
              </div>
            ))}
          </dl>
          <p className="sms-rep__determinism">{REPORT_DETERMINISM_NOTE}</p>

          <dl className="sms-formats">
            {REPORT_FORMATS.map((format) => {
              const label = format.lang ? REPORT_LANGUAGE_LABELS[format.lang] : null;
              return (
                <div className="sms-formats__row" key={format.id}>
                  <dt className="sms-formats__name">
                    <span>{format.name}</span>
                    {label && <span className="sms-formats__lang sms-mr" lang="mr" title={label.en}>{label.mr}</span>}
                  </dt>
                  <dd>{format.text}</dd>
                </div>
              );
            })}
          </dl>

          <div className="sms-draft" role="note">
            <p className="sms-draft__mr sms-mr" lang="mr">{SECTION_STATEMENTS.reportDraft.mr}</p>
            <p className="sms-draft__en">{SECTION_STATEMENTS.reportDraft.en} {REPORT_DRAFT_EN_EXTRA}</p>
          </div>

          <a
            className="sms-link-btn"
            href={`${import.meta.env.BASE_URL}${SAMPLE_REPORT.href}`}
            target="_blank"
            rel="noopener noreferrer"
          >
            <span>{SAMPLE_REPORT_LINK.label}</span>
            <ExternalLink size={16} aria-hidden="true" />
          </a>
          <p className="sms-link-note">{SAMPLE_REPORT_LINK.note}</p>
        </div>
      </div>
    </Section>
  );
};
