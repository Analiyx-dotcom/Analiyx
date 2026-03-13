import React, { useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Sparkles, ArrowLeft } from 'lucide-react';

const LegalPage = () => {
  const location = useLocation();

  useEffect(() => {
    if (location.hash) {
      const el = document.getElementById(location.hash.replace('#', ''));
      if (el) el.scrollIntoView({ behavior: 'smooth' });
    }
  }, [location]);

  return (
    <div className="min-h-screen bg-gray-950">
      <nav className="bg-gray-950/80 backdrop-blur-lg border-b border-gray-800 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center h-16">
          <Link to="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-white">Analiyx</span>
          </Link>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <Link to="/" className="inline-flex items-center text-purple-400 hover:text-purple-300 mb-8">
          <ArrowLeft className="w-4 h-4 mr-2" /> Back to Home
        </Link>

        <h1 className="text-4xl font-bold text-white mb-12">Legal Information</h1>

        {/* Privacy Policy */}
        <section id="privacy" className="mb-16">
          <h2 className="text-2xl font-bold text-white mb-6 pb-3 border-b border-gray-800">Privacy Policy</h2>
          <div className="prose prose-invert max-w-none space-y-4 text-gray-400">
            <p><strong className="text-gray-200">Last updated:</strong> March 2026</p>
            <p>Analiyx ("we", "our", "us") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our platform.</p>
            <h3 className="text-lg font-semibold text-gray-200 mt-6">Information We Collect</h3>
            <ul className="list-disc pl-6 space-y-2">
              <li>Personal information (name, email, phone number) provided during registration</li>
              <li>Company and business data connected through integrations</li>
              <li>Usage data and analytics about how you interact with our platform</li>
              <li>Payment information processed through our secure payment partners</li>
            </ul>
            <h3 className="text-lg font-semibold text-gray-200 mt-6">How We Use Your Information</h3>
            <ul className="list-disc pl-6 space-y-2">
              <li>To provide and maintain our services</li>
              <li>To process your transactions and manage subscriptions</li>
              <li>To send you service-related notifications</li>
              <li>To improve our platform and develop new features</li>
            </ul>
            <h3 className="text-lg font-semibold text-gray-200 mt-6">Data Security</h3>
            <p>We implement industry-standard security measures to protect your data. All data transmissions are encrypted using SSL/TLS protocols. Your connected data sources credentials are stored in encrypted format.</p>
            <h3 className="text-lg font-semibold text-gray-200 mt-6">Contact</h3>
            <p>For privacy concerns, contact us at <a href="mailto:techmeliora@gmail.com" className="text-purple-400 hover:text-purple-300">techmeliora@gmail.com</a></p>
          </div>
        </section>

        {/* Terms of Service */}
        <section id="terms" className="mb-16">
          <h2 className="text-2xl font-bold text-white mb-6 pb-3 border-b border-gray-800">Terms of Service</h2>
          <div className="prose prose-invert max-w-none space-y-4 text-gray-400">
            <p><strong className="text-gray-200">Last updated:</strong> March 2026</p>
            <p>By accessing and using Analiyx, you agree to be bound by these Terms of Service.</p>
            <h3 className="text-lg font-semibold text-gray-200 mt-6">Account Terms</h3>
            <ul className="list-disc pl-6 space-y-2">
              <li>You must provide accurate and complete registration information</li>
              <li>You are responsible for maintaining the security of your account credentials</li>
              <li>You may not use the service for any illegal or unauthorized purpose</li>
              <li>One person or legal entity may maintain no more than one free account</li>
            </ul>
            <h3 className="text-lg font-semibold text-gray-200 mt-6">Service Usage</h3>
            <ul className="list-disc pl-6 space-y-2">
              <li>Free trial accounts are provided for evaluation purposes with a limited duration</li>
              <li>Paid plans are billed in Indian Rupees (INR) on a monthly basis</li>
              <li>We reserve the right to modify or discontinue features with reasonable notice</li>
              <li>API usage is subject to rate limits based on your subscription plan</li>
            </ul>
            <h3 className="text-lg font-semibold text-gray-200 mt-6">Cancellation & Refunds</h3>
            <p>You may cancel your subscription at any time. Refund requests are handled on a case-by-case basis. Contact <a href="mailto:techmeliora@gmail.com" className="text-purple-400 hover:text-purple-300">techmeliora@gmail.com</a> for refund inquiries.</p>
          </div>
        </section>

        {/* Cookie Policy */}
        <section id="cookies" className="mb-16">
          <h2 className="text-2xl font-bold text-white mb-6 pb-3 border-b border-gray-800">Cookie Policy</h2>
          <div className="prose prose-invert max-w-none space-y-4 text-gray-400">
            <p><strong className="text-gray-200">Last updated:</strong> March 2026</p>
            <p>Analiyx uses cookies and similar tracking technologies to improve your browsing experience and analyze platform usage.</p>
            <h3 className="text-lg font-semibold text-gray-200 mt-6">Types of Cookies We Use</h3>
            <ul className="list-disc pl-6 space-y-2">
              <li><strong className="text-gray-200">Essential Cookies:</strong> Required for authentication and core functionality</li>
              <li><strong className="text-gray-200">Analytics Cookies:</strong> Help us understand how users interact with our platform</li>
              <li><strong className="text-gray-200">Preference Cookies:</strong> Remember your settings and preferences</li>
            </ul>
            <p>You can control cookie settings through your browser preferences. Disabling essential cookies may affect platform functionality.</p>
          </div>
        </section>
      </div>
    </div>
  );
};

export default LegalPage;
