import React from 'react';
import { Link } from 'react-router-dom';
import { Sparkles } from 'lucide-react';
import { Button } from './ui/button';
import { useNavigate } from 'react-router-dom';

const Footer = () => {
  const navigate = useNavigate();

  return (
    <footer className="bg-gray-950 border-t border-gray-800">
      {/* CTA Section */}
      <div className="bg-gradient-to-br from-purple-900/20 to-pink-900/20 border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Ready to make your data work for you?
          </h2>
          <p className="text-gray-400 text-lg mb-8 max-w-2xl mx-auto">
            Book a free consultation and we will help you get setup
          </p>
          <Button
            size="lg"
            className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white text-lg px-8 py-6 shadow-xl shadow-purple-500/30"
            onClick={() => navigate('/signup')}
          >
            Talk to us
          </Button>
        </div>
      </div>

      {/* Footer Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="col-span-1">
            <Link to="/" className="flex items-center space-x-2 mb-4">
              <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-white">Analiyx</span>
            </Link>
            <p className="text-gray-500 text-sm">
              Big Data for Small Teams. No-code data platform powered by AI.
            </p>
          </div>

          {/* Product */}
          <div>
            <h4 className="text-white font-semibold mb-4">Product</h4>
            <ul className="space-y-2">
              <li><a href="#features" className="text-gray-500 hover:text-white transition-colors duration-200 text-sm">Features</a></li>
              <li><a href="#integrations" className="text-gray-500 hover:text-white transition-colors duration-200 text-sm">Integrations</a></li>
              <li><a href="#pricing" className="text-gray-500 hover:text-white transition-colors duration-200 text-sm">Pricing</a></li>
            </ul>
          </div>

          {/* Company */}
          <div>
            <h4 className="text-white font-semibold mb-4">Company</h4>
            <ul className="space-y-2">
              <li><Link to="/" className="text-gray-500 hover:text-white transition-colors duration-200 text-sm">About</Link></li>
              <li><Link to="/" className="text-gray-500 hover:text-white transition-colors duration-200 text-sm">Blog</Link></li>
              <li><Link to="/" className="text-gray-500 hover:text-white transition-colors duration-200 text-sm">Careers</Link></li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h4 className="text-white font-semibold mb-4">Legal</h4>
            <ul className="space-y-2">
              <li><Link to="/" className="text-gray-500 hover:text-white transition-colors duration-200 text-sm">Privacy Policy</Link></li>
              <li><Link to="/" className="text-gray-500 hover:text-white transition-colors duration-200 text-sm">Terms of Service</Link></li>
              <li><Link to="/" className="text-gray-500 hover:text-white transition-colors duration-200 text-sm">Cookie Policy</Link></li>
            </ul>
          </div>
        </div>

        <div className="border-t border-gray-800 mt-12 pt-8 text-center text-gray-500 text-sm">
          <p>&copy; {new Date().getFullYear()} Papermap. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;