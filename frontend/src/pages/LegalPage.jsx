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

            <h3 className="text-lg font-semibold text-gray-200 mt-6">Introduction</h3>
            <p>This Privacy Policy explains how <em>Analiyx</em> collects, uses, and safeguards information when you use Analiyx Platform, including the website <a href="https://analiyx.com" className="text-purple-400 hover:text-purple-300">https://analiyx.com</a> and any associated services or subdomains.</p>
            <p>This policy applies only to data collected through our platform and services. By using the platform, you agree to the practices described in this policy.</p>

            <h3 className="text-lg font-semibold text-gray-200 mt-6">Information We Collect</h3>
            <p>We may collect information from you in several ways, including when you register for an account, interact with the platform, connect external tools, or contact us for support.</p>
            <p>Some system data may also be temporarily stored to maintain performance, improve reliability, or ensure smooth functionality while you are using the platform.</p>

            <h3 className="text-lg font-semibold text-gray-200 mt-6">Account Details</h3>
            <p>When you create or access an account on Analiyx, we may collect information such as:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Name</li>
              <li>Email address</li>
              <li>Company or organization name</li>
              <li>Profile details</li>
              <li>Login credentials</li>
            </ul>
            <p>This information allows us to manage user accounts, enable secure access, and assign appropriate permissions within workspaces.</p>

            <h3 className="text-lg font-semibold text-gray-200 mt-6">Platform Usage Data</h3>
            <p>While using Analiyx, you may upload or connect business-related information to generate analytics insights. This may include:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Business metrics</li>
              <li>Marketing data</li>
              <li>Reports and dashboards</li>
              <li>Platform-generated insights</li>
              <li>Metadata associated with analytics processes</li>
            </ul>
            <p>This information is processed only to provide the analytics functionality of the platform.</p>

            <h3 className="text-lg font-semibold text-gray-200 mt-6">System Analytics and Performance Monitoring</h3>
            <p>To improve reliability and usability, we may collect anonymous technical data such as system diagnostics and usage trends.</p>
            <p>This data helps us understand how users interact with the platform and allows us to enhance performance. It is <em>not used for advertising or behavioral profiling</em>.</p>

            <h3 className="text-lg font-semibold text-gray-200 mt-6">Information You Provide Directly</h3>
            <p>If you contact us through forms, support requests, feedback submissions, or other communication channels, we may collect the information you provide.</p>
            <p>This helps us respond to inquiries, provide technical support, and improve the overall service.</p>

            <h3 className="text-lg font-semibold text-gray-200 mt-6">External Data Integrations</h3>
            <p>The Analiyx platform may allow you to connect external services such as analytics tools, marketing platforms, spreadsheets, or databases.</p>
            <p>When these integrations are enabled, we only access the information necessary to generate analytics insights or dashboards requested by the user.</p>
            <p>Your connected data is <em>never sold, licensed, or used for unrelated purposes</em>.</p>

            <h3 className="text-lg font-semibold text-gray-200 mt-6">Automatically Collected Technical Information</h3>
            <p>Certain technical information may be gathered automatically when you interact with the platform, including:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Internet Protocol (IP) address</li>
              <li>Browser type and version</li>
              <li>Device information</li>
              <li>Platform interaction data</li>
            </ul>
            <p>Cookies or analytics tools may also be used to better understand system performance and user engagement.</p>

            <h3 className="text-lg font-semibold text-gray-200 mt-6">AI-Assisted Insights</h3>
            <p>Some features within Analiyx may use AI-assisted technologies to help generate analytics insights and summaries.</p>
            <p>These technologies process information only to deliver the requested functionality. The data processed through these features is <em>not used for advertising, resale, or training external AI systems</em>.</p>

            <h3 className="text-lg font-semibold text-gray-200 mt-6">How We Use Collected Information</h3>
            <p>The information collected may be used for purposes such as:</p>
            <p><strong className="text-gray-200">Operating the platform</strong></p>
            <ul className="list-disc pl-6 space-y-2">
              <li>User authentication</li>
              <li>Access control and permissions</li>
              <li>Workspace and dashboard management</li>
            </ul>
            <p><strong className="text-gray-200">Improving the service</strong></p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Monitoring system stability</li>
              <li>Enhancing platform features</li>
            </ul>
            <p><strong className="text-gray-200">Providing analytics insights</strong></p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Processing data to generate reports and insights</li>
            </ul>
            <p><strong className="text-gray-200">Communication</strong></p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Account notifications</li>
              <li>Support responses</li>
              <li>Service-related updates</li>
            </ul>
            <p>Users may also receive optional product announcements, which they can unsubscribe from at any time.</p>

            <h3 className="text-lg font-semibold text-gray-200 mt-6">Data Security and Storage</h3>
            <p>We take reasonable measures to protect user information. Data is stored on secure infrastructure and protected through encryption, access control policies, and monitoring systems.</p>
            <p>Workspaces are logically separated to maintain privacy and prevent unauthorized access.</p>
            <p>Although we follow industry-standard practices to secure data, no digital platform can guarantee absolute security.</p>

            <h3 className="text-lg font-semibold text-gray-200 mt-6">Data Retention</h3>
            <p>We retain information for as long as necessary to provide services to users or to meet legal and operational requirements.</p>
            <p>If an account remains inactive for an extended period, we may remove or anonymize associated data unless retention is required by law.</p>

            <h3 className="text-lg font-semibold text-gray-200 mt-6">Access or Deletion Requests</h3>
            <p>Users may request access to their stored data or request deletion by contacting us at: <a href="mailto:techmeliora@gmail.com" className="text-purple-400 hover:text-purple-300">techmeliora@gmail.com</a></p>
            <p>We will process such requests in accordance with applicable data protection regulations.</p>

            <h3 className="text-lg font-semibold text-gray-200 mt-6">Account Deactivation</h3>
            <p>If you would like to deactivate your account, please contact us at: <a href="mailto:techmeliora@gmail.com" className="text-purple-400 hover:text-purple-300">techmeliora@gmail.com</a></p>
            <p>Please note that certain shared content or collaborative records may remain accessible to other authorized users within a workspace.</p>

            <h3 className="text-lg font-semibold text-gray-200 mt-6">Policy Updates</h3>
            <p>From time to time, we may update this Privacy Policy to reflect improvements to our services or changes in legal requirements.</p>
            <p>Updates will be posted on this page, and continued use of the platform indicates acceptance of the updated policy.</p>

            <h3 className="text-lg font-semibold text-gray-200 mt-6">Contact Information</h3>
            <p>If you have any questions regarding this Privacy Policy or our data practices, please contact us:</p>
            <p>Email: <a href="mailto:techmeliora@gmail.com" className="text-purple-400 hover:text-purple-300">techmeliora@gmail.com</a></p>
            <p>Website: <a href="https://analiyx.com" className="text-purple-400 hover:text-purple-300">https://analiyx.com</a></p>
          </div>
        </section>

        {/* Terms of Service */}
        <section id="terms" className="mb-16">
          <h2 className="text-2xl font-bold text-white mb-6 pb-3 border-b border-gray-800">Terms of Service (Terms & Conditions)</h2>
          <div className="prose prose-invert max-w-none space-y-4 text-gray-400">

            <h3 className="text-lg font-semibold text-gray-200 mt-6">Introduction</h3>
            <p>Welcome to Analiyx. These Terms of Service govern your access to and use of the Analiyx platform, website, and related services available at <a href="https://analiyx.com" className="text-purple-400 hover:text-purple-300">https://analiyx.com</a></p>
            <p>By accessing or using the platform, you agree to comply with these terms.</p>

            <h3 className="text-lg font-semibold text-gray-200 mt-6">Use of the Platform</h3>
            <p>Users may access and use the platform solely for legitimate business analytics and reporting purposes.</p>
            <p>You agree not to:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Use the platform for unlawful activities</li>
              <li>Attempt to access systems or data without authorization</li>
              <li>Disrupt or interfere with the platform's functionality</li>
              <li>Reverse engineer or copy proprietary features of the platform</li>
            </ul>

            <h3 className="text-lg font-semibold text-gray-200 mt-6">Account Responsibilities</h3>
            <p>Users are responsible for maintaining the confidentiality of their login credentials.</p>
            <p>You agree to:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Provide accurate information during registration</li>
              <li>Notify us immediately if unauthorized access occurs</li>
              <li>Use the platform responsibly within your organization</li>
            </ul>

            <h3 className="text-lg font-semibold text-gray-200 mt-6">Data Ownership</h3>
            <p>All data uploaded or connected by users remains the property of the user or their organization.</p>
            <p>Analiyx does not claim ownership of your business data.</p>
            <p>We process data only to deliver analytics insights and platform functionality.</p>

            <h3 className="text-lg font-semibold text-gray-200 mt-6">AI-Powered Features</h3>
            <p>Some platform features may include AI-assisted analytics or automated insights.</p>
            <p>These features are designed to assist users in interpreting business data. Results should be considered informational and not a substitute for professional advice or strategic decision-making.</p>

            <h3 className="text-lg font-semibold text-gray-200 mt-6">Service Availability</h3>
            <p>We strive to maintain reliable service but cannot guarantee uninterrupted access at all times.</p>
            <p>Maintenance, updates, or technical issues may occasionally affect availability.</p>

            <h3 className="text-lg font-semibold text-gray-200 mt-6">Limitation of Liability</h3>
            <p>To the maximum extent permitted by law, Analiyx shall not be liable for:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Indirect or consequential damages</li>
              <li>Business losses resulting from reliance on analytics insights</li>
              <li>Data loss caused by external integrations or user actions</li>
            </ul>

            <h3 className="text-lg font-semibold text-gray-200 mt-6">Termination</h3>
            <p>We reserve the right to suspend or terminate accounts that violate these terms or misuse the platform.</p>
            <p>Users may discontinue use of the platform at any time.</p>

            <h3 className="text-lg font-semibold text-gray-200 mt-6">Changes to Terms</h3>
            <p>These Terms may be updated periodically. Continued use of the platform after updates constitutes acceptance of the revised terms.</p>
          </div>
        </section>

        {/* Cookie Policy */}
        <section id="cookies" className="mb-16">
          <h2 className="text-2xl font-bold text-white mb-6 pb-3 border-b border-gray-800">Cookie Policy</h2>
          <div className="prose prose-invert max-w-none space-y-4 text-gray-400">

            <h3 className="text-lg font-semibold text-gray-200 mt-6">Introduction</h3>
            <p>This Cookie Policy explains how Analiyx uses cookies and similar technologies when you visit <a href="https://analiyx.com" className="text-purple-400 hover:text-purple-300">https://analiyx.com</a></p>

            <h3 className="text-lg font-semibold text-gray-200 mt-6">What Are Cookies</h3>
            <p>Cookies are small data files stored on your device when you visit a website. They help websites remember information about your visit and improve the browsing experience.</p>

            <h3 className="text-lg font-semibold text-gray-200 mt-6">How We Use Cookies</h3>
            <p><strong className="text-gray-200">Essential Cookies</strong></p>
            <p>These cookies are required for core platform functionality, including login authentication and session management.</p>
            <p><strong className="text-gray-200">Analytics Cookies</strong></p>
            <p>We may use analytics tools to understand how visitors interact with the platform. This helps us improve performance and usability.</p>
            <p><strong className="text-gray-200">Preference Cookies</strong></p>
            <p>These cookies remember user preferences such as language or interface settings.</p>

            <h3 className="text-lg font-semibold text-gray-200 mt-6">Managing Cookies</h3>
            <p>Most web browsers allow you to control or disable cookies through browser settings.</p>
            <p>Please note that disabling certain cookies may affect platform functionality.</p>
          </div>
        </section>

        {/* AI Usage & Transparency Policy */}
        <section id="ai-policy" className="mb-16">
          <h2 className="text-2xl font-bold text-white mb-6 pb-3 border-b border-gray-800">AI Usage & Transparency Policy</h2>
          <div className="prose prose-invert max-w-none space-y-4 text-gray-400">

            <h3 className="text-lg font-semibold text-gray-200 mt-6">Overview</h3>
            <p>The Analiyx platform includes AI-assisted capabilities designed to help businesses interpret data, generate insights, and improve decision-making.</p>

            <h3 className="text-lg font-semibold text-gray-200 mt-6">Purpose of AI Features</h3>
            <p>AI tools within Analiyx may be used for:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Data interpretation</li>
              <li>Insight generation</li>
              <li>Business performance summaries</li>
              <li>Pattern detection in analytics data</li>
            </ul>

            <h3 className="text-lg font-semibold text-gray-200 mt-6">Data Handling</h3>
            <p>Data processed through AI features is used only to generate insights for the user.</p>
            <p>We do not use customer data to train external AI models or for advertising purposes.</p>

            <h3 className="text-lg font-semibold text-gray-200 mt-6">Responsible Use</h3>
            <p>AI-generated insights should be used as supportive information, not as the sole basis for critical financial, legal, or operational decisions.</p>
            <p>Users should independently review analytics results before taking business action.</p>

            <h3 className="text-lg font-semibold text-gray-200 mt-6">Continuous Improvement</h3>
            <p>We continuously refine AI capabilities to improve accuracy, performance, and usefulness while maintaining strong data protection standards.</p>
          </div>
        </section>
      </div>
    </div>
  );
};

export default LegalPage;
