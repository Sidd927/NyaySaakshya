/**
 * The landing page's navigable sections, in reading order.
 *
 * A section appears in the navbar only while an element with its id is on the page, so the
 * nav can never point at nothing. That check is pure CSS (landing-nav.css, :has()), which is
 * why the ids below are repeated there. A section element must carry:
 *
 *   id="<id below>"  data-landing-section
 *
 * and, ideally, a heading, because the link moves focus to the section.
 */
export interface LandingSection {
  id: string;
  label: string;
}

export const LANDING_SECTIONS: LandingSection[] = [
  { id: 'landing-how', label: 'How it works' },
  { id: 'landing-evidence', label: 'Evidence' },
  { id: 'landing-limits', label: 'Limits' },
  { id: 'landing-reports', label: 'Reports' },
  { id: 'landing-scope', label: 'Scope' },
];

const prefersReducedMotion = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches;

/**
 * Scroll the landing to a section without touching the URL. Hash navigation would fire the
 * app's popstate listeners and could disturb the ?view= routing, so links use this instead.
 * Focus moves to the section so keyboard and screen-reader users land where the page went.
 */
export function scrollToSection(id: string): boolean {
  const target = document.getElementById(id);
  if (!target) return false;
  target.scrollIntoView({ behavior: prefersReducedMotion() ? 'auto' : 'smooth', block: 'start' });
  if (!target.hasAttribute('tabindex')) target.setAttribute('tabindex', '-1');
  target.focus({ preventScroll: true });
  return true;
}

export function scrollToTop(): void {
  document.querySelector('.sms-landing')?.scrollTo({ top: 0, behavior: prefersReducedMotion() ? 'auto' : 'smooth' });
}
