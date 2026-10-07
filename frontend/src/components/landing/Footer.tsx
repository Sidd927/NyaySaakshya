import React from 'react';
import { ExternalLink } from 'lucide-react';
import { BrandLogo } from '../common/BrandLogo';
import { FOOTER, SAMPLE_REPORT_LINK } from './copy';
import { SAMPLE_REPORT } from './reportSample';
import { LANDING_SECTIONS, scrollToSection, scrollToTop } from './sections';

/** Quiet page end: the name, what the tool is, where the sample report is, and the page's own sections. */
export const Footer: React.FC = () => (
  <footer className="sms-foot">
    <div className="sms-foot__inner">
      <div className="sms-foot__id">
        <BrandLogo variant="lockup" size="md" />
        <p className="sms-foot__scope">{FOOTER.scope}</p>
        <p className="sms-foot__note">{FOOTER.note}</p>
      </div>

      <nav className="sms-foot__col" aria-labelledby="sms-foot-nav">
        <h2 id="sms-foot-nav" className="sms-foot__h">{FOOTER.navLabel}</h2>
        <ul className="sms-foot__list">
          {LANDING_SECTIONS.map((section) => (
            <li key={section.id}>
              <a
                className="sms-foot__link"
                href={`#${section.id}`}
                onClick={(event) => { event.preventDefault(); scrollToSection(section.id); }}
              >
                {section.label}
              </a>
            </li>
          ))}
          <li>
            <a
              className="sms-foot__link"
              href="#top"
              onClick={(event) => { event.preventDefault(); scrollToTop(); }}
            >
              {FOOTER.top}
            </a>
          </li>
        </ul>
      </nav>

      <div className="sms-foot__col">
        <h2 className="sms-foot__h">{FOOTER.reportTitle}</h2>
        <a
          className="sms-foot__link sms-foot__link--ext"
          href={`${import.meta.env.BASE_URL}${SAMPLE_REPORT.href}`}
          target="_blank"
          rel="noopener noreferrer"
        >
          <span>{SAMPLE_REPORT_LINK.label}</span>
          <ExternalLink size={14} aria-hidden="true" />
        </a>
        <p className="sms-foot__fine">{SAMPLE_REPORT_LINK.note}</p>
      </div>
    </div>
  </footer>
);
