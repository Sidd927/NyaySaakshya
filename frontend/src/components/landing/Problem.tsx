import React from 'react';
import { PROBLEM_CLOSING, PROBLEM_ROWS, SECTION_STATEMENTS, SECTION_TITLES } from './copy';
import { Section, SectionHead } from './Section';

/** The problem, set as a ruled case memo: four plain statements, no figures, no cards. */
export const Problem: React.FC = () => (
  <Section id="landing-problem">
    <div className="sms-sec__split">
      <SectionHead sectionId="landing-problem" title={SECTION_TITLES.problem} statement={SECTION_STATEMENTS.problem} />
      <div className="sms-problem__memo">
        <dl className="sms-problem__rows">
          {PROBLEM_ROWS.map((row) => (
            <div className="sms-problem__row" key={row.term}>
              <dt>{row.term}</dt>
              <dd>{row.text}</dd>
            </div>
          ))}
        </dl>
        <p className="sms-problem__closing">{PROBLEM_CLOSING}</p>
      </div>
    </div>
  </Section>
);
