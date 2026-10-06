import React from 'react';
import type { CopyEntry } from './copy';

const titleId = (sectionId: string) => `${sectionId}-title`;

interface SectionProps {
  id: string;
  /** Appears in the navbar: carries data-landing-section, which turns its link on. */
  navigable?: boolean;
  className?: string;
  children: React.ReactNode;
}

/** A landing section. Labelled by its heading; focusable by the navbar so focus follows a link. */
export const Section: React.FC<SectionProps> = ({ id, navigable = false, className = '', children }) => (
  <section
    id={id}
    data-landing-section={navigable ? '' : undefined}
    aria-labelledby={titleId(id)}
    className={`sms-sec ${className}`.trim()}
  >
    {children}
  </section>
);

interface SectionHeadProps {
  sectionId: string;
  title: CopyEntry;
  /** A Marathi narrative line under the heading. */
  statement?: CopyEntry;
  standfirst?: string;
}

/**
 * Heading anatomy shared by every section, as in the hero lockup: a short gold rule, the
 * Marathi heading in display type, the English title beneath it, then plain English for the
 * detail. The rule is the same hairline as the hero's, here marking where a section begins.
 */
export const SectionHead: React.FC<SectionHeadProps> = ({ sectionId, title, statement, standfirst }) => (
  <header className="sms-sec__head">
    <div className="sms-sec__rule" aria-hidden="true" />
    <h2 id={titleId(sectionId)} className="sms-sec__title">
      <span className="sms-sec__h-mr sms-mr" lang="mr">{title.mr}</span>{' '}
      <span className="sms-sec__h-en" lang="en">{title.en}</span>
    </h2>
    {statement?.mr && <p className="sms-sec__statement sms-mr" lang="mr">{statement.mr}</p>}
    {standfirst && <p className="sms-sec__standfirst">{standfirst}</p>}
  </header>
);
