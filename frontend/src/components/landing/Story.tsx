import React, { useMemo } from 'react';
import { FIXTURES } from '../../fixtures';
import { EvidenceStates } from './EvidenceStates';
import { Closing } from './Closing';
import { HowItWorks } from './HowItWorks';
import { Limits } from './Limits';
import { Problem } from './Problem';
import { buildHonestyExample, buildSampleRecord } from './recordData';
import { ReportSection } from './ReportSection';
import { ScopeSection } from './ScopeSection';

/** Everything below the hero: one continuous line from the problem to the report and its limits. */
export const Story: React.FC = () => {
  const record = useMemo(() => buildSampleRecord(FIXTURES.deepdive_cross_session_control_endpoint), []);
  const example = useMemo(() => buildHonestyExample(FIXTURES.scene_b_certificate_honesty), []);
  return (
    <div className="sms-story">
      <div className="sms-story__inner">
        <Problem />
        <HowItWorks record={record} />
        <EvidenceStates example={example} />
        <Limits />
        <ReportSection />
        <ScopeSection />
        <Closing />
      </div>
    </div>
  );
};
