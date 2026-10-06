import React from 'react';
import { SCOPE_GROUPS, SCOPE_STANDFIRST, SECTION_TITLES } from './copy';
import { Section, SectionHead } from './Section';

/** Scope and security as a specification sheet: three ruled columns, nothing claimed beyond the README. */
export const ScopeSection: React.FC = () => (
  <Section id="landing-scope" navigable>
    <SectionHead sectionId="landing-scope" title={SECTION_TITLES.scope} standfirst={SCOPE_STANDFIRST} />
    <div className="sms-scope__sheet">
      {SCOPE_GROUPS.map((group) => (
        <div className="sms-scope__group" key={group.id}>
          <h3 className="sms-scope__title">{group.title}</h3>
          <ul className="sms-scope__lines">
            {group.lines.map((line) => <li key={line}>{line}</li>)}
          </ul>
        </div>
      ))}
    </div>
  </Section>
);
