import React from 'react';
import { howItWorks } from '../mock/mockData';
import { Card, CardContent } from './ui/card';
import { Plug, Sparkles, TrendingUp } from 'lucide-react';

const iconMap = {
  plug: Plug,
  sparkles: Sparkles,
  'trending-up': TrendingUp
};

const HowItWorks = () => {
  return (
    <section id="features" className="py-20 bg-gray-950">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-white mb-4">How it works</h2>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {howItWorks.map((item) => {
            const Icon = iconMap[item.icon];
            return (
              <Card
                key={item.step}
                className="bg-gray-900/50 border-gray-800 backdrop-blur-sm hover:border-purple-500/50 transition-all duration-300 transform hover:scale-105 group"
              >
                <CardContent className="p-8 text-center">
                  <div className="mb-6">
                    <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-purple-600 to-pink-600 rounded-2xl shadow-lg shadow-purple-500/30 group-hover:shadow-purple-500/50 transition-shadow duration-300">
                      <Icon className="w-8 h-8 text-white" />
                    </div>
                  </div>
                  <div className="text-purple-400 font-bold text-lg mb-3">{item.step}</div>
                  <h3 className="text-xl font-bold text-white mb-4">{item.title}</h3>
                  <p className="text-gray-400 leading-relaxed">{item.description}</p>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default HowItWorks;