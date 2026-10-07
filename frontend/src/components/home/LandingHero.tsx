import { useEffect } from 'react';
import { Footer } from '../landing/Footer';
import { Hero } from '../landing/Hero';
import { LandingNav } from '../landing/LandingNav';
import { scrollToSection } from '../landing/sections';
import { Story } from '../landing/Story';

/** The landing page: navigation, the hero, then the story from the problem to the scope, the closing action, and the footer. */
export const LandingHero: React.FC = () => {
  // The shell's skip link targets #main-content, which on the landing also contains the navbar,
  // so following it skipped nothing (and left a #hash in the URL). Here it goes to the hero,
  // the first element of <main>, so the next Tab stop is the page's first action.
  useEffect(() => {
    const skip = document.querySelector<HTMLAnchorElement>('.skip-link');
    if (!skip) return;
    const onSkip = (event: Event) => {
      event.preventDefault();
      scrollToSection('sms-hero');
    };
    skip.addEventListener('click', onSkip);
    return () => skip.removeEventListener('click', onSkip);
  }, []);

  return (
    <div className="sms-landing">
      <LandingNav />
      <main className="sms-landing__main">
        <Hero />
        <Story />
      </main>
      <Footer />
    </div>
  );
};
