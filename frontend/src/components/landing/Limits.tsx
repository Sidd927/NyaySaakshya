import React from 'react';
import { LIMITS, LIMITS_STANDFIRST, SECTION_STATEMENTS, SECTION_TITLES } from './copy';
import { Section, SectionHead } from './Section';

/** The boundaries of the method, stated plainly: a statement and its reason, ruled, no apology. */
export const Limits: React.FC = () => (
  <Section id="landing-limits" navigable>
    <SectionHead sectionId="landing-limits" title={SECTION_TITLES.limits} statement={SECTION_STATEMENTS.limits} standfirst={LIMITS_STANDFIRST} />
    <ul className="sms-limits">
      {LIMITS.map((item) => (
        <li className="sms-limits__item" key={item.id}>
          <p className="sms-limits__statement">{item.statement}</p>
          <p className="sms-limits__reason">{item.reason}</p>
        </li>
      ))}
    </ul>
  </Section>
);
