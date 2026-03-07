import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Sparkles, ArrowLeft } from 'lucide-react';
import { toast } from '../hooks/use-toast';

const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [emailSent, setEmailSent] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    // TODO: Integrate with backend API for password reset
    setTimeout(() => {
      setEmailSent(true);
      toast({
        title: 'Reset link sent!',
        description: 'Check your email for password reset instructions.',
      });
      setIsLoading(false);
    }, 1500);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 flex items-center justify-center px-4">
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-pink-600/10 rounded-full blur-3xl"></div>
      </div>

      <Card className="w-full max-w-md bg-gray-900/50 border-gray-800 backdrop-blur-sm relative z-10">
        <CardHeader className="space-y-1 text-center">
          <Link to="/" className="flex items-center justify-center space-x-2 mb-4">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <span className="text-2xl font-bold text-white">Analiyx</span>
          </Link>
          <CardTitle className="text-2xl text-white">
            {emailSent ? 'Check your email' : 'Reset password'}
          </CardTitle>
          <CardDescription className="text-gray-400">
            {emailSent 
              ? "We've sent password reset instructions to your email"
              : "Enter your email and we'll send you reset instructions"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {!emailSent ? (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email" className="text-gray-300">Email</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  placeholder="name@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="bg-gray-800 border-gray-700 text-white placeholder:text-gray-500"
                />
              </div>
              <Button
                type="submit"
                className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white"
                disabled={isLoading}
              >
                {isLoading ? 'Sending...' : 'Send reset link'}
              </Button>
            </form>
          ) : (
            <div className="space-y-4">
              <div className="bg-green-900/20 border border-green-700 rounded-lg p-4">
                <p className="text-green-400 text-sm text-center">
                  ✓ Reset instructions sent to <strong>{email}</strong>
                </p>
              </div>
              <Button
                onClick={() => setEmailSent(false)}
                variant="outline"
                className="w-full border-gray-700 text-gray-300 hover:bg-gray-800"
              >
                Resend email
              </Button>
            </div>
          )}

          <div className="mt-6 text-center">
            <Link 
              to="/login" 
              className="text-purple-400 hover:text-purple-300 text-sm font-semibold inline-flex items-center space-x-2"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back to login</span>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ForgotPassword;
