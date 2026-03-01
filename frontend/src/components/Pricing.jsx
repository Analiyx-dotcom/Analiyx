import React from 'react';
import { pricingPlans } from '../mock/mockData';
import { Card, CardContent, CardHeader } from './ui/card';
import { Button } from './ui/button';
import { Check } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const Pricing = () => {
  const navigate = useNavigate();

  return (
    <section id="pricing" className="py-20 bg-gray-950">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <p className="text-purple-400 text-sm font-semibold uppercase tracking-wider mb-2">Pricing</p>
          <h2 className="text-4xl font-bold text-white mb-4">
            Choose the plan that works best for your business
          </h2>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {pricingPlans.map((plan) => (
            <Card
              key={plan.id}
              className={`relative ${
                plan.highlighted
                  ? 'bg-gradient-to-br from-purple-900/50 to-pink-900/50 border-purple-500 shadow-2xl shadow-purple-500/20 scale-105'
                  : 'bg-gray-900/50 border-gray-800'
              } backdrop-blur-sm hover:scale-105 transition-all duration-300`}
            >
              {plan.highlighted && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <span className="bg-gradient-to-r from-purple-600 to-pink-600 text-white text-xs font-bold px-4 py-1 rounded-full shadow-lg">
                    RECOMMENDED
                  </span>
                </div>
              )}
              
              <CardHeader className="text-center pb-4">
                <h3 className="text-2xl font-bold text-white mb-2">{plan.name}</h3>
                <p className="text-gray-400 text-sm mb-4">{plan.description}</p>
                <div className="border-t border-gray-800 pt-4">
                  <div className="flex items-baseline justify-center">
                    {typeof plan.price === 'number' ? (
                      <>
                        <span className="text-4xl font-bold text-white">${plan.price}</span>
                        <span className="text-gray-400 ml-2">/ {plan.period}</span>
                      </>
                    ) : (
                      <span className="text-4xl font-bold text-white">{plan.price}</span>
                    )}
                  </div>
                </div>
              </CardHeader>

              <CardContent className="space-y-4">
                <div className="border-t border-gray-800 pt-6">
                  <ul className="space-y-3 mb-6">
                    {plan.features.map((feature, index) => (
                      <li key={index} className="flex items-start space-x-3">
                        <Check className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                        <span className="text-gray-300 text-sm">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <Button
                  className={`w-full ${
                    plan.highlighted
                      ? 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white shadow-lg'
                      : 'bg-gray-800 hover:bg-gray-700 text-white border border-gray-700'
                  }`}
                  onClick={() => navigate('/signup')}
                >
                  Get Started
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Pricing;