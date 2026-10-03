import React from 'react';
import type { ReportLanguage } from '../../../api/types';

interface Option {
  value: ReportLanguage;
  label: string;
  /** Language of the label itself, so a screen reader pronounces it correctly. */
  labelLang: string;
}

const OPTIONS: Option[] = [
  { value: 'en', label: 'English', labelLang: 'en' },
  { value: 'mr', label: 'मराठी', labelLang: 'mr' },
  { value: 'both', label: 'मराठी + English', labelLang: 'mr' },
];

interface Props {
  value: ReportLanguage;
  onChange: (next: ReportLanguage) => void;
  /** Translations are produced by the analysis service; without it only English is offered. */
  translationsAvailable: boolean;
  disabled?: boolean;
}

/** Segmented radio group for the language of the downloaded report. */
export const ReportLanguageToggle: React.FC<Props> = ({ value, onChange, translationsAvailable, disabled }) => {
  const enabled = OPTIONS.filter((o) => o.value === 'en' || translationsAvailable);

  const onKeyDown = (event: React.KeyboardEvent<HTMLButtonElement>) => {
    const step = event.key === 'ArrowRight' || event.key === 'ArrowDown' ? 1
      : event.key === 'ArrowLeft' || event.key === 'ArrowUp' ? -1 : 0;
    if (!step) return;
    event.preventDefault();
    const index = enabled.findIndex((o) => o.value === value);
    onChange(enabled[(index + step + enabled.length) % enabled.length].value);
  };

  return (
    <div className="sms-lang-toggle" role="radiogroup" aria-label="Report language">
      {OPTIONS.map((option) => {
        const unavailable = option.value !== 'en' && !translationsAvailable;
        const checked = option.value === value;
        return (
          <button
            key={option.value}
            type="button"
            role="radio"
            aria-checked={checked}
            tabIndex={checked ? 0 : -1}
            disabled={disabled || unavailable}
            className={`sms-lang-toggle__option${checked ? ' is-active' : ''}`}
            lang={option.labelLang}
            title={unavailable ? 'Translations need the analysis service' : undefined}
            onClick={() => onChange(option.value)}
            onKeyDown={onKeyDown}
          >
            {option.label}
          </button>
        );
      })}
    </div>
  );
};
