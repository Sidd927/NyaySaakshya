import { ArrowRight } from 'lucide-react';
import { BrandLogo } from '../common/BrandLogo';
import { Hero } from '../landing/Hero';
import { enterApplication } from './openIngestion';

const LINKS = ['Product', 'How it Works', 'Security', 'Documentation'];

export const LandingHero: React.FC = () => {
  return (
    <div className="sms-landing">
      <header className="sms-gate__nav">
        <a className="sms-gate__brand" href="#sms-hero" onClick={(event) => event.preventDefault()}>
          <BrandLogo variant="compact" size="sm" />
        </a>
        <nav className="sms-gate__links" aria-label="Product">
          {LINKS.map((label) => (
            <a key={label} href="#sms-hero" onClick={(event) => event.preventDefault()}>{label}</a>
          ))}
        </nav>
        <button type="button" className="sms-gate__cta sms-gate__cta--nav" onClick={enterApplication}>
          Get Started
          <ArrowRight size={15} aria-hidden="true" />
        </button>
      </header>

      <Hero />
    </div>
  );
};
