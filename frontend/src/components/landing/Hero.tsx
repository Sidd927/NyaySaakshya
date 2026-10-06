import React, { useMemo } from 'react';
import { FIXTURES } from '../../fixtures';
import { BrandLogo } from '../common/BrandLogo';
import { BinaryWaterfall } from '../home/BinaryWaterfall';
import { enterApplication } from '../home/openIngestion';
import { HERO_COPY } from './copy';
import { EvidenceRecord } from './EvidenceRecord';
import { buildSampleRecord } from './recordData';

/**
 * Landing hero. Order of attention: the Devanagari wordmark, the Latin name, the Marathi
 * statement, one English sentence, one action, then a real evidence record. The record is
 * a bundled fixture and the rain is made of its SHA-256, so what falls is what is shown.
 */
export const Hero: React.FC = () => {
  const record = useMemo(() => buildSampleRecord(FIXTURES.deepdive_cross_session_control_endpoint), []);

  return (
    <section className="sms-gate sms-hero" id="sms-hero" aria-labelledby="sms-hero-title">
      <BinaryWaterfall glyphSource={record?.captureSha256} />
      <div className="sms-gate__vignette" aria-hidden="true" />
      <div className="sms-gate__bloom" aria-hidden="true" />
      <div className="sms-hero__inner">
        <div className="sms-hero__copy">
          <BrandLogo variant="lockup" size="display" as="h1" id="sms-hero-title" />
          <div className="sms-hero__rule" aria-hidden="true" />
          <p className="sms-hero__statement sms-mr" lang="mr">{HERO_COPY.statement.mr}</p>
          <p className="sms-hero__explainer">{HERO_COPY.explainer.en}</p>
          <button type="button" className="sms-cta sms-hero__cta" onClick={enterApplication}>
            {HERO_COPY.cta.en}
          </button>
        </div>
        {record && <EvidenceRecord record={record} />}
      </div>
    </section>
  );
};
