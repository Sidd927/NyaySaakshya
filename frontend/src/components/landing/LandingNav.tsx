import React, { useEffect, useId, useRef, useState } from 'react';
import { Menu, X } from 'lucide-react';
import { BrandLogo } from '../common/BrandLogo';
import { enterApplication } from '../home/openIngestion';
import { HERO_COPY } from './copy';
import { LANDING_SECTIONS, scrollToSection, scrollToTop } from './sections';

/** Below this width the links collapse into a disclosure menu (keep in sync with landing-nav.css). */
const MENU_QUERY = '(max-width: 879px)';

/**
 * Landing navbar: brand, section links, the primary action. Links to sections that are not on
 * the page are hidden by CSS, so there are no dead links; with no sections the menu button is
 * hidden too. On narrow screens the links and the action live in a disclosure panel.
 */
export const LandingNav: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState<string | null>(null);
  const headerRef = useRef<HTMLElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const panelId = useId();

  // Which section the reader is in. Marks the link with aria-current.
  useEffect(() => {
    const root = headerRef.current?.closest<HTMLElement>('.sms-landing') ?? null;
    const targets = LANDING_SECTIONS.map((s) => document.getElementById(s.id)).filter((el): el is HTMLElement => !!el);
    if (!root || targets.length === 0 || typeof IntersectionObserver === 'undefined') return;
    const visible = new Set<string>();
    // The reading band: from just under the bar to 45% of the way down the viewport. The
    // section with the most area inside it is the one being read.
    const current = () => {
      const box = root.getBoundingClientRect();
      const top = box.top + 72;
      const bottom = box.top + box.height * 0.45;
      let best: string | null = null;
      let bestOverlap = 0;
      for (const section of LANDING_SECTIONS) {
        if (!visible.has(section.id)) continue;
        const rect = document.getElementById(section.id)?.getBoundingClientRect();
        if (!rect) continue;
        const overlap = Math.min(rect.bottom, bottom) - Math.max(rect.top, top);
        if (overlap > bestOverlap) {
          bestOverlap = overlap;
          best = section.id;
        }
      }
      return best;
    };
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) visible.add(entry.target.id);
          else visible.delete(entry.target.id);
        }
        setActive(current());
      },
      { root, rootMargin: '-72px 0px -55% 0px', threshold: [0, 0.1, 0.25, 0.5, 0.75, 1] },
    );
    targets.forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, []);

  // Close on Escape (returning focus to the button), on a press outside, and when the menu
  // stops being the layout (window widened).
  useEffect(() => {
    if (!open) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key !== 'Escape') return;
      const inside = headerRef.current?.contains(document.activeElement);
      setOpen(false);
      if (inside) buttonRef.current?.focus();
    };
    const onPress = (event: PointerEvent) => {
      if (!headerRef.current?.contains(event.target as Node)) setOpen(false);
    };
    const media = window.matchMedia(MENU_QUERY);
    const onWide = () => { if (!media.matches) setOpen(false); };
    document.addEventListener('keydown', onKey);
    document.addEventListener('pointerdown', onPress);
    media.addEventListener('change', onWide);
    return () => {
      document.removeEventListener('keydown', onKey);
      document.removeEventListener('pointerdown', onPress);
      media.removeEventListener('change', onWide);
    };
  }, [open]);

  const goTo = (id: string) => (event: React.MouseEvent) => {
    event.preventDefault();
    setOpen(false);
    scrollToSection(id);
  };

  const upload = () => {
    setOpen(false);
    enterApplication();
  };

  return (
    <header className="sms-nav" ref={headerRef}>
      <div className="sms-nav__inner">
        <a
          className="sms-nav__brand"
          href="#sms-hero"
          aria-label="NyaySaakshya, back to the top"
          onClick={(event) => { event.preventDefault(); setOpen(false); scrollToTop(); }}
        >
          <BrandLogo variant="wordmark" />
        </a>

        <button
          ref={buttonRef}
          type="button"
          className="sms-nav__menu-btn"
          aria-expanded={open}
          aria-controls={panelId}
          onClick={() => setOpen((v) => !v)}
        >
          {open ? <X size={18} aria-hidden="true" /> : <Menu size={18} aria-hidden="true" />}
          <span>Menu</span>
        </button>

        <div id={panelId} className="sms-nav__panel" data-open={open}>
          <nav aria-label="Sections">
            <ul className="sms-nav__links">
              {LANDING_SECTIONS.map((section) => (
                <li key={section.id} data-target={section.id}>
                  <a
                    href={`#${section.id}`}
                    aria-current={active === section.id ? 'location' : undefined}
                    onClick={goTo(section.id)}
                  >
                    {section.label}
                  </a>
                </li>
              ))}
            </ul>
          </nav>
          <button type="button" className="sms-cta sms-nav__cta sms-nav__cta--panel" onClick={upload}>
            {HERO_COPY.cta.en}
          </button>
        </div>

        <button type="button" className="sms-cta sms-nav__cta sms-nav__cta--bar" onClick={upload}>
          {HERO_COPY.cta.en}
        </button>
      </div>
    </header>
  );
};
