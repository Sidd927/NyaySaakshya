import React from 'react';

interface BrandLogoProps {
  variant?: 'mark' | 'compact' | 'full';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  showSubtitle?: boolean;
  className?: string;
  onClick?: () => void;
}

export const BrandLogo: React.FC<BrandLogoProps> = ({
  variant = 'compact',
  size = 'md',
  showSubtitle = false,
  className = '',
  onClick,
}) => {
  // Dimension mapping for mark
  const markDimensions: Record<string, { width: number; height: number; iconSize: number }> = {
    sm: { width: 22, height: 22, iconSize: 22 },
    md: { width: 28, height: 28, iconSize: 28 },
    lg: { width: 38, height: 38, iconSize: 38 },
    xl: { width: 52, height: 52, iconSize: 52 },
  };

  const currentDim = markDimensions[size] || markDimensions.md;

  // Decorative: the product name is rendered as text next to it (or the variant is mark-only
  // and the surrounding control carries the accessible name).
  const markSvg = (
    <img
      src={`${import.meta.env.BASE_URL}branding/logo.svg`}
      width={currentDim.width}
      height={currentDim.height}
      alt=""
      aria-hidden="true"
      className="sms-brand-logo__svg"
      style={{ borderRadius: 6 }}
      decoding="async"
    />
  );

  if (variant === 'mark') {
    return (
      <div
        className={`sms-brand-logo sms-brand-logo--mark sms-brand-logo--${size} ${className}`}
        onClick={onClick}
        role={onClick ? 'button' : undefined}
        tabIndex={onClick ? 0 : undefined}
      >
        {markSvg}
      </div>
    );
  }

  return (
    <div
      className={`sms-brand-logo sms-brand-logo--${variant} sms-brand-logo--${size} ${className}`}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      style={{ display: 'inline-flex', alignItems: 'center', gap: size === 'sm' ? 8 : 10, cursor: onClick ? 'pointer' : 'default' }}
    >
      <div className="sms-brand-logo__mark-wrap">
        {markSvg}
      </div>
      <div className="sms-brand-logo__text-wrap" style={{ display: 'flex', flexDirection: 'column', lineHeight: 1 }}>
        <div className="sms-brand-logo__wordmark" style={{ display: 'flex', alignItems: 'baseline', letterSpacing: '-0.02em' }}>
          <span style={{ fontWeight: 700, color: 'var(--sms-text-primary, #f8fafc)', fontSize: size === 'sm' ? '0.875rem' : size === 'lg' ? '1.25rem' : size === 'xl' ? '1.5rem' : '1rem' }}>
            Nyay
          </span>
          <span style={{ fontWeight: 600, color: 'var(--sms-brand-cyan, #00d2ff)', fontSize: size === 'sm' ? '0.875rem' : size === 'lg' ? '1.25rem' : size === 'xl' ? '1.5rem' : '1rem' }}>
            Saakshya
          </span>
        </div>
        {(showSubtitle || variant === 'full') && (
          <span
            className="sms-brand-logo__subtitle"
            style={{
              fontSize: size === 'sm' ? '0.625rem' : '0.6875rem',
              fontWeight: 600,
              letterSpacing: '0.1em',
              textTransform: 'uppercase',
              color: 'var(--sms-text-muted, #64748b)',
              marginTop: 3,
            }}
          >
            Forensic Cryptographic Engine
          </span>
        )}
      </div>
    </div>
  );
};
