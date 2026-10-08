import React from 'react';
import { ArrowRight, GitCompare } from 'lucide-react';
import type { DashboardViewModel, SessionEvidence } from '../../../api/types';

interface CrossSessionPreviewCardProps {
  dashboard: DashboardViewModel;
  sessions: SessionEvidence[];
  onOpenCrossSession: (streamKey?: string) => void;
}

export const CrossSessionPreviewCard: React.FC<CrossSessionPreviewCardProps> = ({
  dashboard,
  sessions,
  onOpenCrossSession,
}) => {
  // Check if there are cross-session deviation findings
  const csFinding = dashboard.findings.find(
    (f) => f.source_rule_ids?.some((r) => r.startsWith('CS-')) || f.dimension === 'cross_session' || f.title.toLowerCase().includes('deviation')
  );

  // The "subject vs control" comparison below states a STARTTLS difference between two
  // endpoints. That is a claim only a cross-session deviation finding makes, so without one
  // there is nothing to show; two client addresses alone are not a comparison.
  if (!csFinding) {
    return null;
  }

  // Subject = the client of the session the finding names; control = another client address
  // seen in the capture. Neither is guessed: an address that cannot be derived shows as a dash.
  const clientIps = Array.from(new Set(sessions.map((s) => s.client.ip).filter(Boolean))) as string[];
  const subjectIp = sessions.find((s) => s.stream_key === csFinding.stream_key)?.client.ip ?? null;
  const controlIp = clientIps.find((ip) => ip !== subjectIp) ?? null;

  return (
    <div className="sms-context-card" aria-label="Cross-Session Baseline Comparison">
      <div className="sms-context-card__head">
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <GitCompare size={13} style={{ color: 'var(--sms-brand-cyan)' }} aria-hidden="true" />
          <span className="sms-label">Cross-Session Baseline</span>
        </div>
        <span className="sms-mono sms-badge sms-badge--muted">Pairwise Analysis</span>
      </div>

      <div className="sms-context-card__body sms-stack sms-stack--tight">
        <div className="sms-cs-comparison">
          <div className="sms-cs-comparison__item">
            <span className="sms-label" style={{ fontSize: '10px' }}>Subject Endpoint</span>
            <span className="sms-mono" style={{ color: 'var(--ds-sev-critical-text)', fontWeight: 600 }}>
              {subjectIp ?? '—'}
            </span>
            <span className="sms-badge sms-badge--muted" style={{ marginTop: '2px', alignSelf: 'flex-start' }}>
              STARTTLS: NOT OBSERVED
            </span>
          </div>

          <div className="sms-cs-comparison__vs" aria-hidden="true">
            vs
          </div>

          <div className="sms-cs-comparison__item">
            <span className="sms-label" style={{ fontSize: '10px' }}>Control Endpoint</span>
            <span className="sms-mono" style={{ color: 'var(--ds-sev-low-text)', fontWeight: 600 }}>
              {controlIp ?? '—'}
            </span>
            <span className="sms-badge sms-badge--muted" style={{ marginTop: '2px', alignSelf: 'flex-start' }}>
              STARTTLS: OBSERVED
            </span>
          </div>
        </div>

        {csFinding && (
          <p className="sms-prose sms-text-xs" style={{ margin: '4px 0 0 0', color: 'var(--sms-text-secondary)' }}>
            Deviation supported by rule <strong className="sms-mono" style={{ color: 'var(--ds-sev-high-text)' }}>{csFinding.source_rule_ids?.[0] || 'CS-STARTTLS-001'}</strong>. This is a difference from the endpoint's own history, not proof of stripping.
          </p>
        )}

        <button
          type="button"
          className="sms-link"
          style={{ marginTop: '6px', alignSelf: 'flex-start', display: 'inline-flex', alignItems: 'center', gap: '4px' }}
          onClick={() => onOpenCrossSession()}
        >
          Investigate cross-session matrix <ArrowRight size={11} aria-hidden="true" />
        </button>
      </div>
    </div>
  );
};
