import { Hero } from '../landing/Hero';
import { LandingNav } from '../landing/LandingNav';

/** The landing page: navigation, then the hero. Further sections follow the hero (phase 4). */
export const LandingHero: React.FC = () => {
  return (
    <div className="sms-landing">
      <LandingNav />
      <Hero />
    </div>
  );
};
