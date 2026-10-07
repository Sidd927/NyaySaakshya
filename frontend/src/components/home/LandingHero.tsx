import { Footer } from '../landing/Footer';
import { Hero } from '../landing/Hero';
import { LandingNav } from '../landing/LandingNav';
import { Story } from '../landing/Story';

/** The landing page: navigation, the hero, then the story from the problem to the scope, the closing action, and the footer. */
export const LandingHero: React.FC = () => {
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
