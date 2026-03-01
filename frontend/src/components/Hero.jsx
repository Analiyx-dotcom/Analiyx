import React from 'react';
import { Button } from './ui/button';
import { useNavigate } from 'react-router-dom';
import { Sparkles, Play } from 'lucide-react';

const Hero = () => {
  const navigate = useNavigate();

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-b from-gray-950 via-gray-900 to-gray-950">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-pink-600/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
          <Sparkles className="w-8 h-8 text-purple-500/20 absolute top-20 left-10 animate-pulse" />
          <Sparkles className="w-6 h-6 text-pink-500/20 absolute top-40 right-20 animate-pulse" style={{ animationDelay: '0.5s' }} />
          <Sparkles className="w-10 h-10 text-purple-500/20 absolute bottom-20 left-32 animate-pulse" style={{ animationDelay: '1.5s' }} />
          <Sparkles className="w-7 h-7 text-pink-500/20 absolute bottom-40 right-40 animate-pulse" style={{ animationDelay: '2s' }} />
        </div>
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
        {/* YouTube Badge */}
        <div className="inline-flex items-center space-x-2 px-4 py-2 bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-full mb-8 hover:border-purple-500 transition-all duration-300 cursor-pointer group">
          <Play className="w-4 h-4 text-purple-400 group-hover:text-purple-300" />
          <span className="text-sm text-gray-300">Watch Papermap in action on YouTube!</span>
        </div>

        {/* Sparkles decoration */}
        <div className="flex justify-center space-x-4 mb-6">
          <Sparkles className="w-6 h-6 text-purple-400 animate-pulse" />
          <Sparkles className="w-5 h-5 text-pink-400 animate-pulse" style={{ animationDelay: '0.3s' }} />
          <Sparkles className="w-6 h-6 text-purple-400 animate-pulse" style={{ animationDelay: '0.6s' }} />
          <Sparkles className="w-5 h-5 text-pink-400 animate-pulse" style={{ animationDelay: '0.9s' }} />
        </div>

        {/* Main heading */}
        <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold text-white mb-6 leading-tight">
          <span className="block mb-2">Big Data for</span>
          <span className="block bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
            Small Teams
          </span>
        </h1>

        {/* Subheading */}
        <h2 className="text-2xl sm:text-3xl lg:text-4xl font-semibold text-gray-300 mb-6">
          No-Code Data Platform, For Your Lean Team
        </h2>

        {/* Description */}
        <p className="text-lg text-gray-400 max-w-3xl mx-auto mb-10">
          Connect raw data in seconds. Get realtime insights, discover opportunities and automate operations with AI tailored to your business.
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-4 mb-4">
          <Button 
            size="lg"
            className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white text-lg px-8 py-6 shadow-2xl shadow-purple-500/30 transform hover:scale-105 transition-all duration-200"
            onClick={() => navigate('/signup')}
          >
            Get Started Now
          </Button>
        </div>
        <p className="text-sm text-gray-500">No credit card required</p>

        {/* Dashboard Preview */}
        <div className="mt-16 relative group">
          <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl blur-2xl opacity-20 group-hover:opacity-30 transition-opacity duration-300"></div>
          <div className="relative bg-gray-900 rounded-2xl border border-gray-800 p-2 shadow-2xl transform group-hover:scale-[1.02] transition-transform duration-300">
            <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-8 border border-gray-700">
              <div className="aspect-video bg-gray-950 rounded-lg flex items-center justify-center border border-gray-800">
                <div className="text-center">
                  <Sparkles className="w-16 h-16 text-purple-500 mx-auto mb-4 animate-pulse" />
                  <p className="text-gray-400">Dashboard Preview</p>
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