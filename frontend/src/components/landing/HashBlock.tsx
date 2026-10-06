import React from 'react';

interface HashBlockProps {
  /** The complete SHA-256 (or any hex digest). Never truncated. */
  value: string;
  className?: string;
}

/**
 * A full hash that stays readable and copyable at any width. It is cut into 8-character
 * groups that wrap four to a line (two lines for SHA-256). The groups are plain inline
 * spans separated by CSS spacing and <wbr> break points, not spaces, so selecting and copying yields the exact
 * 64-character value with no gaps or line breaks, and a screen reader reads it group by group.
 */
export const HashBlock: React.FC<HashBlockProps> = ({ value, className = '' }) => {
  const groups = value.match(/.{1,8}/g) ?? [];
  return (
    <code className={`sms-hash ${className}`.trim()} translate="no">
      {groups.map((group, index) => (
        <React.Fragment key={index}>
          <span className="sms-hash__group">{group}</span>
          <wbr />
        </React.Fragment>
      ))}
    </code>
  );
};
