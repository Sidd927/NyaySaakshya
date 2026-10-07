import React from 'react';
import { enterApplication } from '../home/openIngestion';
import { CLOSING, HERO_COPY } from './copy';
import { Section, SectionHead } from './Section';

/**
 * The end of the line. The chain the page has described, capture to report, is drawn once more in
 * short, with the capture emphasised because it is where the reader begins. The action is the same
 * one as in the navbar and hero: same label, same transition.
 */
export const Closing: React.FC = () => (
  <Section id="landing-start" className="sms-close">
    <SectionHead sectionId="landing-start" title={CLOSING.title} standfirst={CLOSING.standfirst} />
    <ol className="sms-close__chain" aria-label={CLOSING.chainLabel}>
      {CLOSING.chain.map((step, index) => (
        <li key={step} className={index === 0 ? 'sms-close__step sms-close__step--first' : 'sms-close__step'}>{step}</li>
      ))}
    </ol>
    <button type="button" className="sms-cta sms-close__cta" onClick={enterApplication}>
      {HERO_COPY.cta.en}
    </button>
    <p className="sms-close__caution">{CLOSING.caution}</p>
  </Section>
);
