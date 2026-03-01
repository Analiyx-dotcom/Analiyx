import React from 'react';
import Navbar from '../components/Navbar';
import Hero from '../components/Hero';
import TrustedBrands from '../components/TrustedBrands';
import Testimonials from '../components/Testimonials';
import HowItWorks from '../components/HowItWorks';
import Integrations from '../components/Integrations';
import Pricing from '../components/Pricing';
import Footer from '../components/Footer';

const LandingPage = () => {
  return (
    <div className="min-h-screen bg-gray-950">
      <Navbar />
      <Hero />
      <TrustedBrands />
      <Testimonials />
      <HowItWorks />
      <Integrations />
      <Pricing />
      <Footer />
    </div>
  );
};

export default LandingPage;