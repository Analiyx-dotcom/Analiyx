import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '../components/ui/dialog';
import { ArrowLeft, User, Shield, Loader2, Eye, EyeOff } from 'lucide-react';
import { toast } from '../hooks/use-toast';
import api from '../services/api';

const Settings = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [phone, setPhone] = useState('');
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [showCurrentPw, setShowCurrentPw] = useState(false);
  const [showNewPw, setShowNewPw] = useState(false);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) { navigate('/login'); return; }
        const res = await api.get('/auth/me');
        const u = res.data;
        setUser(u);
        const nameParts = (u.name || '').split(' ');
        setFirstName(nameParts[0] || '');
        setLastName(nameParts.slice(1).join(' ') || '');
        setPhone(u.phone || '');
      } catch { navigate('/login'); }
      finally { setIsLoading(false); }
    };
    fetchUser();
  }, [navigate]);

  const handleSaveProfile = async () => {
    setIsSaving(true);
    try {
      await api.put('/auth/profile', { first_name: firstName, last_name: lastName, phone });
      toast({ title: 'Profile Updated', description: 'Your profile has been saved.' });
    } catch (err) {
      toast({ title: 'Error', description: err.response?.data?.detail || 'Failed to update.', variant: 'destructive' });
    } finally { setIsSaving(false); }
  };

  const handleChangePassword = async () => {
    if (newPassword !== confirmPassword) {
      toast({ title: 'Error', description: 'New passwords do not match.', variant: 'destructive' });
      return;
    }
    if (newPassword.length < 6) {
      toast({ title: 'Error', description: 'Password must be at least 6 characters.', variant: 'destructive' });
      return;
    }
    setIsChangingPassword(true);
    try {
      await api.put('/auth/change-password', { current_password: currentPassword, new_password: newPassword });
      toast({ title: 'Password Changed', description: 'Your password has been updated.' });
      setShowPasswordModal(false);
      setCurrentPassword(''); setNewPassword(''); setConfirmPassword('');
    } catch (err) {
      toast({ title: 'Error', description: err.response?.data?.detail || 'Failed to change password.', variant: 'destructive' });
    } finally { setIsChangingPassword(false); }
  };

  if (isLoading) return <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-purple-400" /></div>;

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white">
      {/* Header */}
      <div className="border-b border-gray-800 bg-[#0d0d14]">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center gap-4">
          <Button variant="ghost" size="sm" onClick={() => navigate('/dashboard')} className="text-gray-400 hover:text-white" data-testid="settings-back-btn">
            <ArrowLeft className="w-4 h-4 mr-2" /> Back to Dashboard
          </Button>
        </div>
      </div>

      {/* Page Content */}
      <div className="max-w-6xl mx-auto px-6 py-10">
        <h1 className="text-4xl font-bold text-white mb-2" data-testid="settings-heading">Settings</h1>
        <p className="text-gray-400 mb-10">Manage your account settings and preferences</p>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Personal Information */}
          <Card className="bg-[#12121a] border border-gray-800/60 rounded-2xl">
            <CardHeader className="pb-1">
              <CardTitle className="text-white text-lg flex items-center gap-2"><User className="w-5 h-5 text-purple-400" /> Personal Information</CardTitle>
              <p className="text-gray-500 text-sm mt-1">Update your personal details and how others see you on the platform</p>
            </CardHeader>
            <CardContent className="space-y-5 pt-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className="text-gray-300 text-sm">First Name</Label>
                  <Input value={firstName} onChange={(e) => setFirstName(e.target.value)} className="bg-[#1a1a24] border-gray-700/60 text-white h-11 rounded-lg" data-testid="settings-first-name" />
                </div>
                <div className="space-y-2">
                  <Label className="text-gray-300 text-sm">Last Name</Label>
                  <Input value={lastName} onChange={(e) => setLastName(e.target.value)} className="bg-[#1a1a24] border-gray-700/60 text-white h-11 rounded-lg" data-testid="settings-last-name" />
                </div>
              </div>
              <div className="space-y-2">
                <Label className="text-gray-300 text-sm">Email</Label>
                <Input value={user?.email || ''} disabled className="bg-[#1a1a24] border-gray-700/60 text-gray-400 h-11 rounded-lg cursor-not-allowed" data-testid="settings-email" />
              </div>
              <div className="space-y-2">
                <Label className="text-gray-300 text-sm">Phone Number</Label>
                <Input value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="Enter your phone number (e.g., +1234567890)" className="bg-[#1a1a24] border-gray-700/60 text-white placeholder:text-gray-600 h-11 rounded-lg" data-testid="settings-phone" />
              </div>
              <Button onClick={handleSaveProfile} disabled={isSaving} className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 h-10 px-6 rounded-lg" data-testid="settings-save-btn">
                {isSaving ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
                Save Changes
              </Button>
            </CardContent>
          </Card>

          {/* Account Security */}
          <Card className="bg-[#12121a] border border-gray-800/60 rounded-2xl h-fit">
            <CardHeader className="pb-1">
              <CardTitle className="text-white text-lg flex items-center gap-2"><Shield className="w-5 h-5 text-purple-400" /> Account Security</CardTitle>
              <p className="text-gray-500 text-sm mt-1">Manage your password and account security settings</p>
            </CardHeader>
            <CardContent className="pt-4">
              <div className="bg-[#1a1a24] rounded-xl p-4 flex items-center justify-between border border-gray-700/40">
                <span className="text-white font-medium">Password</span>
                <Button variant="outline" onClick={() => setShowPasswordModal(true)} className="bg-[#0a0a0f] border-gray-600 text-white hover:bg-gray-800 h-9 rounded-lg" data-testid="settings-change-password-btn">
                  Change Password
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Change Password Modal */}
      <Dialog open={showPasswordModal} onOpenChange={setShowPasswordModal}>
        <DialogContent className="bg-[#12121a] border-gray-800 text-white max-w-md">
          <DialogHeader>
            <DialogTitle className="text-lg font-bold">Change Password</DialogTitle>
            <DialogDescription className="text-gray-400">Enter your current password and choose a new one</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div className="space-y-2">
              <Label className="text-gray-300 text-sm">Current Password</Label>
              <div className="relative">
                <Input type={showCurrentPw ? 'text' : 'password'} value={currentPassword} onChange={(e) => setCurrentPassword(e.target.value)} className="bg-[#1a1a24] border-gray-700 text-white h-11 pr-10" data-testid="current-password-input" />
                <button type="button" onClick={() => setShowCurrentPw(!showCurrentPw)} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300">{showCurrentPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}</button>
              </div>
            </div>
            <div className="space-y-2">
              <Label className="text-gray-300 text-sm">New Password</Label>
              <div className="relative">
                <Input type={showNewPw ? 'text' : 'password'} value={newPassword} onChange={(e) => setNewPassword(e.target.value)} className="bg-[#1a1a24] border-gray-700 text-white h-11 pr-10" data-testid="new-password-input" />
                <button type="button" onClick={() => setShowNewPw(!showNewPw)} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300">{showNewPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}</button>
              </div>
            </div>
            <div className="space-y-2">
              <Label className="text-gray-300 text-sm">Confirm New Password</Label>
              <Input type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} className="bg-[#1a1a24] border-gray-700 text-white h-11" data-testid="confirm-password-input" />
            </div>
            <Button onClick={handleChangePassword} disabled={isChangingPassword || !currentPassword || !newPassword} className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 h-10" data-testid="submit-password-change-btn">
              {isChangingPassword ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
              Update Password
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Settings;
