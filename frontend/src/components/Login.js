import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../utils/api';
import { setAuth } from '../utils/auth';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card } from './ui/card';
import { toast } from 'sonner';
import { Building2 } from 'lucide-react';

export default function Login() {
  const navigate = useNavigate();
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await api.post('/auth/login', { identifier, password });
      setAuth(response.data.access_token, response.data.user);
      toast.success('Login berhasil!');
      navigate('/dashboard');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Login gagal');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center p-3 md:p-4">
      <Card className="w-full max-w-md p-6 md:p-8 shadow-lg" data-testid="login-card">
        <div className="flex flex-col items-center mb-6 md:mb-8">
          <div className="w-14 h-14 md:w-16 md:h-16 bg-slate-900 rounded-xl flex items-center justify-center mb-3 md:mb-4">
            <Building2 className="w-7 h-7 md:w-8 md:h-8 text-white" />
          </div>
          <h1 className="text-2xl md:text-3xl font-bold text-slate-900 tracking-tight">GELIS</h1>
          <p className="text-xs md:text-sm text-slate-700 font-medium mt-2 text-center">Gerbang Elektronik Layanan Informasi Sistem</p>
          <p className="text-xs text-slate-500 mt-1 text-center">Platform Terpadu Monitoring Operasional Multi-Bisnis</p>
        </div>

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Username atau Email</label>
            <Input
              type="text"
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              placeholder="Masukkan username atau email"
              required
              data-testid="login-identifier-input"
              className="w-full min-h-[44px]"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Password</label>
            <Input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Masukkan password"
              required
              data-testid="login-password-input"
              className="w-full min-h-[44px]"
            />
          </div>

          <Button
            type="submit"
            disabled={loading}
            className="w-full bg-slate-900 hover:bg-slate-800 transition-all active:scale-95 min-h-[44px]"
            data-testid="login-submit-button"
          >
            {loading ? 'Memproses...' : 'Masuk'}
          </Button>
        </form>

        <div className="mt-4 md:mt-6 p-3 md:p-4 bg-slate-50 border border-slate-200 rounded-lg">
          <p className="text-xs text-slate-600 mb-3 leading-relaxed">
            GELIS mengkonsolidasi aliran informasi dari berbagai unit usaha (PPOB, PLN, Travel, PDAM, Inventory) 
            ke dalam dashboard terpusat dengan visualisasi real-time.
          </p>
          <div className="pt-3 border-t border-slate-200">
            <p className="text-sm text-slate-900 font-medium">Demo Credentials:</p>
            <p className="text-xs md:text-sm text-slate-700 mt-1">Username: <code className="bg-slate-100 px-2 py-0.5 rounded text-xs">owner</code></p>
            <p className="text-xs md:text-sm text-slate-700">Password: <code className="bg-slate-100 px-2 py-0.5 rounded text-xs">owner123</code></p>
          </div>
        </div>
      </Card>
    </div>
  );
}
