import React from 'react';
import { Button } from './ui/button';
import { useNavigate } from 'react-router-dom';
import { Sparkles, Play, BarChart3, TrendingUp, PieChart, Activity } from 'lucide-react';

const Hero = () => {
  const navigate = useNavigate();

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-b from-gray-950 via-gray-900 to-gray-950">
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-pink-600/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
        <div className="inline-flex items-center space-x-2 px-4 py-2 bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-full mb-8 hover:border-purple-500 transition-all duration-300 cursor-pointer group">
          <Play className="w-4 h-4 text-purple-400 group-hover:text-purple-300" />
          <span className="text-sm text-gray-300">Watch Analiyx in action on YouTube!</span>
        </div>

        <div className="flex justify-center space-x-4 mb-6">
          <Sparkles className="w-6 h-6 text-purple-400 animate-pulse" />
          <Sparkles className="w-5 h-5 text-pink-400 animate-pulse" style={{ animationDelay: '0.3s' }} />
          <Sparkles className="w-6 h-6 text-purple-400 animate-pulse" style={{ animationDelay: '0.6s' }} />
          <Sparkles className="w-5 h-5 text-pink-400 animate-pulse" style={{ animationDelay: '0.9s' }} />
        </div>

        <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold text-white mb-6 leading-tight">
          <span className="block mb-2">Big Data for</span>
          <span className="block bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
            Small Teams
          </span>
        </h1>

        <h2 className="text-lg md:text-xl font-semibold text-gray-300 mb-6">
          No-Code Data Platform, For Your Lean Team
        </h2>

        <p className="text-base text-gray-400 max-w-3xl mx-auto mb-10">
          Connect raw data in seconds. Get realtime insights, discover opportunities and automate operations with AI tailored to your business.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-4 mb-4">
          <Button 
            size="lg"
            className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white text-lg px-8 py-6 shadow-2xl shadow-purple-500/30 transform hover:scale-105 transition-all duration-200"
            onClick={() => navigate('/signup')}
            data-testid="hero-get-started-button"
          >
            Try for Free
          </Button>
        </div>
        <p className="text-sm text-gray-500">14-day free trial. No credit card required.</p>

        {/* Dashboard Preview */}
        <div className="mt-16 relative group">
          <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl blur-2xl opacity-20 group-hover:opacity-30 transition-opacity duration-300"></div>
          <div className="relative bg-gray-900 rounded-2xl border border-gray-800 p-3 shadow-2xl transform group-hover:scale-[1.01] transition-transform duration-300">
            <div className="bg-gray-950 rounded-xl overflow-hidden">
              {/* Fake dashboard header */}
              <div className="bg-gray-900 border-b border-gray-800 px-6 py-3 flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-6 h-6 bg-gradient-to-br from-purple-500 to-pink-500 rounded flex items-center justify-center">
                    <Sparkles className="w-3 h-3 text-white" />
                  </div>
                  <span className="text-sm font-semibold text-white">Analiyx Dashboard</span>
                </div>
                <div className="flex space-x-2">
                  <div className="w-3 h-3 rounded-full bg-red-500/60"></div>
                  <div className="w-3 h-3 rounded-full bg-yellow-500/60"></div>
                  <div className="w-3 h-3 rounded-full bg-green-500/60"></div>
                </div>
              </div>
              {/* Stats row */}
              <div className="p-6">
                <div className="grid grid-cols-4 gap-4 mb-6">
                  {[
                    { label: 'Total Revenue', value: '₹4,56,789', icon: TrendingUp, color: 'text-green-400', bg: 'bg-green-900/20' },
                    { label: 'Active Users', value: '2,547', icon: Activity, color: 'text-blue-400', bg: 'bg-blue-900/20' },
                    { label: 'Conversions', value: '1,234', icon: PieChart, color: 'text-purple-400', bg: 'bg-purple-900/20' },
                    { label: 'Data Sources', value: '12', icon: BarChart3, color: 'text-pink-400', bg: 'bg-pink-900/20' },
                  ].map((stat, i) => (
                    <div key={i} className="bg-gray-900 rounded-lg p-4 border border-gray-800">
                      <div className="flex items-center space-x-2 mb-2">
                        <div className={`p-1.5 rounded ${stat.bg}`}>
                          <stat.icon className={`w-3.5 h-3.5 ${stat.color}`} />
                        </div>
                        <span className="text-xs text-gray-500">{stat.label}</span>
                      </div>
                      <p className="text-lg font-bold text-white">{stat.value}</p>
                    </div>
                  ))}
                </div>
                {/* Chart area */}
                <div className="grid grid-cols-3 gap-4">
                  <div className="col-span-2 bg-gray-900 rounded-lg p-4 border border-gray-800">
                    <p className="text-xs text-gray-500 mb-3">Revenue Trend</p>
                    <div className="flex items-end space-x-2 h-32">
                      {[40, 55, 45, 60, 75, 65, 80, 90, 85, 95, 88, 100].map((h, i) => (
                        <div key={i} className="flex-1 bg-gradient-to-t from-purple-600 to-pink-500 rounded-t opacity-70 hover:opacity-100 transition-opacity" style={{ height: `${h}%` }}></div>
                      ))}
                    </div>
                  </div>
                  <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
                    <p className="text-xs text-gray-500 mb-3">Sources</p>
                    <div className="space-y-3">
                      {[
                        { name: 'Google Ads', pct: 35, color: 'bg-blue-500' },
                        { name: 'Meta Ads', pct: 28, color: 'bg-indigo-500' },
                        { name: 'Excel', pct: 22, color: 'bg-green-500' },
                        { name: 'Zoho', pct: 15, color: 'bg-red-500' },
                      ].map((s, i) => (
                        <div key={i}>
                          <div className="flex justify-between text-xs mb-1">
                            <span className="text-gray-400">{s.name}</span>
                            <span className="text-gray-500">{s.pct}%</span>
                          </div>
                          <div className="w-full bg-gray-800 rounded-full h-1.5">
                            <div className={`${s.color} h-1.5 rounded-full`} style={{ width: `${s.pct}%` }}></div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
