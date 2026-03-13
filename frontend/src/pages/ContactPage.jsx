import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Sparkles, ArrowLeft, Mail, Phone, MapPin, Send, CheckCircle } from 'lucide-react';
import { toast } from '../hooks/use-toast';

const ContactPage = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    company: '',
    phone: '',
    message: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const API_URL = process.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${API_URL}/api/contact`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      const data = await response.json();
      if (data.success) {
        setSubmitted(true);
        toast({ title: 'Message sent!', description: 'We will get back to you soon.' });
      } else {
        throw new Error(data.detail || 'Failed to send');
      }
    } catch (error) {
      toast({ title: 'Failed to send', description: 'Please try again or email us directly.', variant: 'destructive' });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950">
      {/* Nav */}
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

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <Link to="/" className="inline-flex items-center text-purple-400 hover:text-purple-300 mb-8">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Home
        </Link>

        <div className="grid lg:grid-cols-2 gap-12">
          {/* Left - Info */}
          <div>
            <h1 className="text-4xl font-bold text-white mb-4">Get in Touch</h1>
            <p className="text-gray-400 text-lg mb-8">
              Have a question or want a demo? Fill out the form and our team will get back to you within 24 hours.
            </p>

            <div className="space-y-6">
              <div className="flex items-start space-x-4">
                <div className="p-3 bg-purple-900/20 rounded-lg">
                  <Mail className="w-5 h-5 text-purple-400" />
                </div>
                <div>
                  <p className="text-white font-medium">Email</p>
                  <a href="mailto:techmeliora@gmail.com" className="text-gray-400 hover:text-purple-400">techmeliora@gmail.com</a>
                </div>
              </div>
              <div className="flex items-start space-x-4">
                <div className="p-3 bg-purple-900/20 rounded-lg">
                  <Phone className="w-5 h-5 text-purple-400" />
                </div>
                <div>
                  <p className="text-white font-medium">Phone</p>
                  <p className="text-gray-400">Available on request</p>
                </div>
              </div>
              <div className="flex items-start space-x-4">
                <div className="p-3 bg-purple-900/20 rounded-lg">
                  <MapPin className="w-5 h-5 text-purple-400" />
                </div>
                <div>
                  <p className="text-white font-medium">Location</p>
                  <p className="text-gray-400">India</p>
                </div>
              </div>
            </div>
          </div>

          {/* Right - Form */}
          <Card className="bg-gray-900/50 border-gray-800 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-white">{submitted ? 'Thank You!' : 'Send us a message'}</CardTitle>
              <CardDescription className="text-gray-400">
                {submitted ? 'We have received your message and will respond soon.' : 'Fill in the details below and we will reach out to you.'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {submitted ? (
                <div className="text-center py-8">
                  <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
                  <p className="text-white text-lg font-medium mb-2">Message Sent Successfully!</p>
                  <p className="text-gray-400 mb-6">Our team will contact you at {formData.email}</p>
                  <Button onClick={() => { setSubmitted(false); setFormData({ name: '', email: '', company: '', phone: '', message: '' }); }} variant="outline" className="border-gray-700 text-gray-300">
                    Send Another Message
                  </Button>
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-4" data-testid="contact-form">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label className="text-gray-300">Full Name *</Label>
                      <Input name="name" value={formData.name} onChange={handleChange} required placeholder="Your name" className="bg-gray-800 border-gray-700 text-white placeholder:text-gray-500" data-testid="contact-name-input" />
                    </div>
                    <div className="space-y-2">
                      <Label className="text-gray-300">Email *</Label>
                      <Input name="email" type="email" value={formData.email} onChange={handleChange} required placeholder="you@company.com" className="bg-gray-800 border-gray-700 text-white placeholder:text-gray-500" data-testid="contact-email-input" />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label className="text-gray-300">Company</Label>
                      <Input name="company" value={formData.company} onChange={handleChange} placeholder="Company name" className="bg-gray-800 border-gray-700 text-white placeholder:text-gray-500" />
                    </div>
                    <div className="space-y-2">
                      <Label className="text-gray-300">Phone</Label>
                      <Input name="phone" value={formData.phone} onChange={handleChange} placeholder="+91 XXXXX XXXXX" className="bg-gray-800 border-gray-700 text-white placeholder:text-gray-500" />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label className="text-gray-300">Message *</Label>
                    <textarea name="message" value={formData.message} onChange={handleChange} required placeholder="Tell us about your data needs..." rows={4} className="w-full rounded-md bg-gray-800 border border-gray-700 text-white placeholder:text-gray-500 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500" data-testid="contact-message-input" />
                  </div>
                  <Button type="submit" disabled={isSubmitting} className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white" data-testid="contact-submit-button">
                    {isSubmitting ? 'Sending...' : <><Send className="w-4 h-4 mr-2" /> Send Message</>}
                  </Button>
                </form>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default ContactPage;
