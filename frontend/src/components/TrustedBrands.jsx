import React from 'react';
import { trustedBrands } from '../mock/mockData';

const TrustedBrands = () => {
  return (
    <section className="py-12 bg-gray-950 border-y border-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <p className="text-center text-gray-500 text-sm mb-8">
          Trusted by leading brands turning data chaos into strategic advantage
        </p>
        
        {/* Scrolling logos */}
        <div className="relative overflow-hidden">
          <div className="flex animate-scroll space-x-16">
            {[...trustedBrands, ...trustedBrands, ...trustedBrands, ...trustedBrands].map((brand, index) => (
              <div
                key={index}
                className="flex-shrink-0 h-12 px-8 flex items-center justify-center"
              >
                <div className="text-gray-600 font-semibold text-lg whitespace-nowrap hover:text-gray-400 transition-colors duration-200">
                  {brand}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes scroll {
          0% {
            transform: translateX(0);
          }
          100% {
            transform: translateX(-50%);
          }
        }
        .animate-scroll {
          animation: scroll 30s linear infinite;
        }
        .animate-scroll:hover {
          animation-play-state: paused;
        }
      `}</style>
    </section>
  );
};

export default TrustedBrands;