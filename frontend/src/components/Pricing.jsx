import React from 'react';
import { Button } from './ui/button';
import { CheckCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const plans = [
  {
    name: 'Starter',
    price: '500',
    period: '/month',
    description: 'Perfect for small teams getting started with data analytics.',
    features: ['4 Data Source Connections', 'AI Visibility (1/month)', '100 Credits/month', 'Email Support', '1 Workspace'],
    cta: 'Start Free Trial',
    popular: false,
  },
  {
    name: 'Business Pro',
    price: '800',
    period: '/month',
    description: 'For growing businesses that need advanced analytics and more integrations.',
    features: ['Unlimited Data Sources', 'Advanced AI Analytics', '1,000 Credits/month', 'Priority Support', '10 Workspaces', 'Slack Integration', 'Report Downloads'],
    cta: 'Start Free Trial',
    popular: true,
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    period: '',
    description: 'For large organizations with custom data requirements.',
    features: ['Everything in Business Pro', 'Custom Integrations', 'Unlimited Credits', 'Dedicated Account Manager', 'Custom AI Models', 'SLA & Uptime Guarantee', 'On-premise Option'],
    cta: 'Talk to Sales',
    popular: false,
  },
];

const Pricing = () => {
  const navigate = useNavigate();

  return (
    <section id="pricing" className="py-20 bg-gray-950">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">Simple, transparent pricing</h2>
          <p className="text-base text-gray-400 max-w-2xl mx-auto">14-day free trial on all plans. No credit card required.</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {plans.map((plan, index) => (
            <div key={index} className={`relative rounded-2xl p-8 border transition-all duration-300 ${plan.popular ? 'bg-gradient-to-b from-purple-900/30 to-gray-900 border-purple-500 shadow-xl shadow-purple-500/20 scale-105' : 'bg-gray-900 border-gray-800 hover:border-gray-700'}`}>
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-gradient-to-r from-purple-600 to-pink-600 text-white text-sm font-medium px-4 py-1 rounded-full">Most Popular</div>
              )}
              <h3 className="text-xl font-bold text-white mb-2">{plan.name}</h3>
              <p className="text-gray-400 text-sm mb-6">{plan.description}</p>
              <div className="mb-8">
                <span className="text-4xl font-bold text-white">{plan.price === 'Custom' ? '' : '₹'}{plan.price}</span>
                <span className="text-gray-400">{plan.period}</span>
              </div>
              <ul className="space-y-3 mb-8">
                {plan.features.map((feature, i) => (
                  <li key={i} className="flex items-center space-x-3">
                    <CheckCircle className="w-5 h-5 text-purple-400 flex-shrink-0" />
                    <span className="text-gray-300 text-sm">{feature}</span>
                  </li>
                ))}
              </ul>
              <Button
                className={`w-full ${plan.popular ? 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white' : 'bg-gray-800 hover:bg-gray-700 text-white border border-gray-700'}`}
                onClick={() => plan.price === 'Custom' ? navigate('/contact') : navigate('/signup')}
                data-testid={`pricing-cta-${plan.name.toLowerCase().replace(' ', '-')}`}
              >
                {plan.cta}
              </Button>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Pricing;
