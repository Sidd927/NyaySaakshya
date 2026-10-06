import React from 'react';

/**
 * A capture file name that may break after an underscore, never inside a word. The break points
 * add no characters, so selecting and copying still gives the exact name.
 */
export const FileName: React.FC<{ name: string; className?: string }> = ({ name, className }) => (
  <code className={className} translate="no">
    {name.split('_').map((part, i, all) => (
      <React.Fragment key={i}>{part}{i < all.length - 1 ? <>_<wbr /></> : null}</React.Fragment>
    ))}
  </code>
);
