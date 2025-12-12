import React, { useState, useEffect } from 'react';
import { api } from '../utils/api';
import { getUser } from '../utils/auth';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Switch } from './ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from './ui/alert-dialog';
import { 
  Settings as SettingsIcon, Building2, Bell, Mail, Database, 
  Shield, Trash2, Download, Upload, Globe, DollarSign, Clock, 
  Smartphone, AlertTriangle, Check, X
} from 'lucide-react';
import { toast } from 'sonner';

export default function Settings() {
  const currentUser = getUser();
  const isOwner = currentUser?.role_id === 1;
  
  const [loading, setLoading] = useState(false);
  const [settings, setSettings] = useState({
    company_name: 'PT. GELIS Indonesia',
    company_address: 'Jl. Contoh No. 123, Jakarta Selatan',
    company_phone: '021-12345678',
    company_email: 'info@gelis.com',
    company_website: 'https://gelis.com',
    company_logo: '',
    
    // System Settings
    timezone: 'Asia/Jakarta',
    language: 'id',
    currency: 'IDR',
    date_format: 'DD/MM/YYYY',
    time_format: '24h',
    
    // Notification Settings
    email_notifications: true,
    email_host: 'smtp.gmail.com',
    email_port: '587',
    email_username: '',
    email_password: '',
    whatsapp_notifications: false,
    whatsapp_api_url: '',
    whatsapp_api_key: '',
    push_notifications: true,
    
    // Data Settings
    is_mock_data: true,
    data_retention_days: 365,
    auto_backup: false,
    backup_frequency: 'daily',
    
    // Security Settings
    session_timeout: 43200,
    password_expiry_days: 90,
    max_login_attempts: 5,
    two_factor_auth: false,
  });

  const [activeTab, setActiveTab] = useState('company');
  const [stats, setStats] = useState({
    total_users: 0,
    total_orders: 0,
    total_transactions: 0,
    total_reports: 0,
    database_size: '0 MB',
    last_backup: null
  });

  useEffect(() => {
    fetchSettings();
    fetchStats();
  }, []);

  const fetchSettings = async () => {
    try {
      const response = await api.get('/settings/all');
      if (response.data) {
        setSettings(prev => ({ ...prev, ...response.data }));
      }
    } catch (error) {
      console.error('Error fetching settings:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const [usersRes, ordersRes, transactionsRes, reportsRes] = await Promise.all([
        api.get('/users').catch(() => ({ data: [] })),
        api.get('/orders').catch(() => ({ data: [] })),
        api.get('/accounting').catch(() => ({ data: [] })),
        api.get('/reports/loket-daily').catch(() => ({ data: [] }))
      ]);
      
      setStats({
        total_users: usersRes.data.length,
        total_orders: ordersRes.data.length,
        total_transactions: transactionsRes.data.length,
        total_reports: reportsRes.data.length,
        database_size: '~25 MB',
        last_backup: null
      });
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const handleSaveSettings = async (section) => {
    setLoading(true);
    try {
      await api.put('/settings/bulk', { settings, section });
      toast.success('Pengaturan berhasil disimpan!');
      fetchSettings();
    } catch (error) {
      toast.error('Gagal menyimpan pengaturan');
    } finally {
      setLoading(false);
    }
  };

  const handleClearMockData = async () => {
    if (!isOwner) {
      toast.error('Hanya Owner yang dapat menghapus data mockup');
      return;
    }
    
    setLoading(true);
    try {
      await api.post('/data/clear-mock');
      toast.success('Data mockup berhasil dihapus! Aplikasi sekarang menggunakan data real.');
      setSettings(prev => ({ ...prev, is_mock_data: false }));
      fetchStats();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Gagal menghapus data mockup');
    } finally {
      setLoading(false);
    }
  };

  const handleBackupDatabase = async () => {
    setLoading(true);
    try {
      const response = await api.post('/data/backup');
      toast.success('Backup database berhasil dibuat!');
      
      // Download backup file
      const blob = new Blob([JSON.stringify(response.data)], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `gelis-backup-${new Date().toISOString().split('T')[0]}.json`;
      a.click();
    } catch (error) {
      toast.error('Gagal membuat backup');
    } finally {
      setLoading(false);
    }
  };

  const handleTestEmail = async () => {
    setLoading(true);
    try {
      await api.post('/settings/test-email', {
        to: settings.company_email,
        subject: 'Test Email dari GELIS',
        body: 'Ini adalah test email dari sistem GELIS.'
      });
      toast.success('Email test berhasil dikirim!');
    } catch (error) {
      toast.error('Gagal mengirim email test');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4 md:space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl md:text-3xl lg:text-4xl font-bold text-slate-900 tracking-tight mb-1 md:mb-2">
          Pengaturan Sistem
        </h1>
        <p className="text-sm md:text-base text-slate-600">
          Kelola konfigurasi dan preferensi sistem GELIS
        </p>
      </div>

      {/* Warning if Mock Data */}
      {settings.is_mock_data && (
        <Card className="p-4 md:p-6 border-orange-200 bg-orange-50">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-orange-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="text-sm md:text-base font-semibold text-orange-900 mb-1">
                Mode Simulasi Aktif
              </h3>
              <p className="text-xs md:text-sm text-orange-700 mb-3">
                Aplikasi saat ini menggunakan data mockup untuk simulasi. Semua data (users, orders, transactions, reports) 
                adalah data contoh. Klik tombol di bawah untuk menghapus semua data mockup dan mulai menggunakan data real.
              </p>
              {isOwner && (
                <AlertDialog>
                  <AlertDialogTrigger asChild>
                    <Button variant="outline" size="sm" className="bg-white border-orange-300 text-orange-700 hover:bg-orange-100">
                      <Trash2 className="w-4 h-4 mr-2" />
                      Hapus Data Mockup & Mulai Data Real
                    </Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>Hapus Semua Data Mockup?</AlertDialogTitle>
                      <AlertDialogDescription className="space-y-2">
                        <p>Tindakan ini akan menghapus semua data mockup:</p>
                        <ul className="list-disc list-inside space-y-1 text-sm">
                          <li>Semua user kecuali owner dan admin</li>
                          <li>Semua orders dan work orders</li>
                          <li>Semua transaksi keuangan</li>
                          <li>Semua laporan harian (loket & kasir)</li>
                          <li>Semua program loyalty dan CSR</li>
                        </ul>
                        <p className="font-semibold text-red-600 mt-3">
                          ⚠️ Tindakan ini tidak dapat dibatalkan! Pastikan Anda sudah backup data jika diperlukan.
                        </p>
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>Batal</AlertDialogCancel>
                      <AlertDialogAction onClick={handleClearMockData} className="bg-red-600 hover:bg-red-700">
                        Ya, Hapus Semua Data Mockup
                      </AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              )}
            </div>
          </div>
        </Card>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 md:gap-4">
        <Card className="p-3 md:p-4">
          <div className="text-xs md:text-sm text-slate-500 mb-1">Total Users</div>
          <div className="text-xl md:text-2xl font-bold text-slate-900">{stats.total_users}</div>
        </Card>
        <Card className="p-3 md:p-4">
          <div className="text-xs md:text-sm text-slate-500 mb-1">Total Orders</div>
          <div className="text-xl md:text-2xl font-bold text-slate-900">{stats.total_orders}</div>
        </Card>
        <Card className="p-3 md:p-4">
          <div className="text-xs md:text-sm text-slate-500 mb-1">Transactions</div>
          <div className="text-xl md:text-2xl font-bold text-slate-900">{stats.total_transactions}</div>
        </Card>
        <Card className="p-3 md:p-4">
          <div className="text-xs md:text-sm text-slate-500 mb-1">Reports</div>
          <div className="text-xl md:text-2xl font-bold text-slate-900">{stats.total_reports}</div>
        </Card>
        <Card className="p-3 md:p-4">
          <div className="text-xs md:text-sm text-slate-500 mb-1">DB Size</div>
          <div className="text-lg md:text-xl font-bold text-slate-900">{stats.database_size}</div>
        </Card>
        <Card className="p-3 md:p-4">
          <div className="text-xs md:text-sm text-slate-500 mb-1">Last Backup</div>
          <div className="text-xs md:text-sm font-medium text-slate-700">
            {stats.last_backup || 'Never'}
          </div>
        </Card>
      </div>

      {/* Settings Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <div className="overflow-x-auto -mx-3 md:mx-0">
          <TabsList className="inline-flex md:grid w-full md:grid-cols-5 min-w-max md:min-w-0">
            <TabsTrigger value="company" className="whitespace-nowrap px-3 md:px-4">
              <Building2 className="w-4 h-4 mr-2" />
              <span className="hidden sm:inline">Perusahaan</span>
            </TabsTrigger>
            <TabsTrigger value="system" className="whitespace-nowrap px-3 md:px-4">
              <SettingsIcon className="w-4 h-4 mr-2" />
              <span className="hidden sm:inline">Sistem</span>
            </TabsTrigger>
            <TabsTrigger value="notifications" className="whitespace-nowrap px-3 md:px-4">
              <Bell className="w-4 h-4 mr-2" />
              <span className="hidden sm:inline">Notifikasi</span>
            </TabsTrigger>
            <TabsTrigger value="data" className="whitespace-nowrap px-3 md:px-4">
              <Database className="w-4 h-4 mr-2" />
              <span className="hidden sm:inline">Data</span>
            </TabsTrigger>
            <TabsTrigger value="security" className="whitespace-nowrap px-3 md:px-4">
              <Shield className="w-4 h-4 mr-2" />
              <span className="hidden sm:inline">Keamanan</span>
            </TabsTrigger>
          </TabsList>
        </div>

        {/* Company Settings */}
        <TabsContent value="company" className="space-y-4 mt-4 md:mt-6">
          <Card className="p-4 md:p-6">
            <h2 className="text-lg md:text-xl font-semibold text-slate-900 mb-4 flex items-center gap-2">
              <Building2 className="w-5 h-5" />
              Informasi Perusahaan
            </h2>
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label>Nama Perusahaan</Label>
                  <Input
                    value={settings.company_name}
                    onChange={(e) => setSettings({...settings, company_name: e.target.value})}
                    className="min-h-[44px]"
                  />
                </div>
                <div>
                  <Label>Email Perusahaan</Label>
                  <Input
                    type="email"
                    value={settings.company_email}
                    onChange={(e) => setSettings({...settings, company_email: e.target.value})}
                    className="min-h-[44px]"
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label>Telepon</Label>
                  <Input
                    value={settings.company_phone}
                    onChange={(e) => setSettings({...settings, company_phone: e.target.value})}
                    className="min-h-[44px]"
                  />
                </div>
                <div>
                  <Label>Website</Label>
                  <Input
                    value={settings.company_website}
                    onChange={(e) => setSettings({...settings, company_website: e.target.value})}
                    className="min-h-[44px]"
                  />
                </div>
              </div>
              
              <div>
                <Label>Alamat</Label>
                <Textarea
                  value={settings.company_address}
                  onChange={(e) => setSettings({...settings, company_address: e.target.value})}
                  rows={3}
                  className="min-h-[88px]"
                />
              </div>
              
              <Button onClick={() => handleSaveSettings('company')} disabled={loading} className="min-h-[44px]">
                <Check className="w-4 h-4 mr-2" />
                Simpan Perubahan
              </Button>
            </div>
          </Card>
        </TabsContent>

        {/* System Settings */}
        <TabsContent value="system" className="space-y-4 mt-4 md:mt-6">
          <Card className="p-4 md:p-6">
            <h2 className="text-lg md:text-xl font-semibold text-slate-900 mb-4 flex items-center gap-2">
              <Globe className="w-5 h-5" />
              Pengaturan Regional
            </h2>
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <Label>Zona Waktu</Label>
                  <Select value={settings.timezone} onValueChange={(val) => setSettings({...settings, timezone: val})}>
                    <SelectTrigger className="min-h-[44px]">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Asia/Jakarta">WIB (Jakarta)</SelectItem>
                      <SelectItem value="Asia/Makassar">WITA (Makassar)</SelectItem>
                      <SelectItem value="Asia/Jayapura">WIT (Jayapura)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <Label>Bahasa</Label>
                  <Select value={settings.language} onValueChange={(val) => setSettings({...settings, language: val})}>
                    <SelectTrigger className="min-h-[44px]">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="id">Bahasa Indonesia</SelectItem>
                      <SelectItem value="en">English</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <Label>Mata Uang</Label>
                  <Select value={settings.currency} onValueChange={(val) => setSettings({...settings, currency: val})}>
                    <SelectTrigger className="min-h-[44px]">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="IDR">IDR (Rupiah)</SelectItem>
                      <SelectItem value="USD">USD (Dollar)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label>Format Tanggal</Label>
                  <Select value={settings.date_format} onValueChange={(val) => setSettings({...settings, date_format: val})}>
                    <SelectTrigger className="min-h-[44px]">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="DD/MM/YYYY">DD/MM/YYYY</SelectItem>
                      <SelectItem value="MM/DD/YYYY">MM/DD/YYYY</SelectItem>
                      <SelectItem value="YYYY-MM-DD">YYYY-MM-DD</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <Label>Format Waktu</Label>
                  <Select value={settings.time_format} onValueChange={(val) => setSettings({...settings, time_format: val})}>
                    <SelectTrigger className="min-h-[44px]">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="24h">24 Jam (13:00)</SelectItem>
                      <SelectItem value="12h">12 Jam (1:00 PM)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <Button onClick={() => handleSaveSettings('system')} disabled={loading} className="min-h-[44px]">
                <Check className="w-4 h-4 mr-2" />
                Simpan Perubahan
              </Button>
            </div>
          </Card>
        </TabsContent>

        {/* Notification Settings */}
        <TabsContent value="notifications" className="space-y-4 mt-4 md:mt-6">
          <Card className="p-4 md:p-6">
            <h2 className="text-lg md:text-xl font-semibold text-slate-900 mb-4 flex items-center gap-2">
              <Mail className="w-5 h-5" />
              Email Notifications
            </h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label>Aktifkan Notifikasi Email</Label>
                  <p className="text-xs md:text-sm text-slate-500 mt-1">Kirim notifikasi penting via email</p>
                </div>
                <Switch
                  checked={settings.email_notifications}
                  onCheckedChange={(val) => setSettings({...settings, email_notifications: val})}
                />
              </div>
              
              {settings.email_notifications && (
                <>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label>SMTP Host</Label>
                      <Input
                        value={settings.email_host}
                        onChange={(e) => setSettings({...settings, email_host: e.target.value})}
                        placeholder="smtp.gmail.com"
                        className="min-h-[44px]"
                      />
                    </div>
                    <div>
                      <Label>SMTP Port</Label>
                      <Input
                        value={settings.email_port}
                        onChange={(e) => setSettings({...settings, email_port: e.target.value})}
                        placeholder="587"
                        className="min-h-[44px]"
                      />
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label>SMTP Username</Label>
                      <Input
                        value={settings.email_username}
                        onChange={(e) => setSettings({...settings, email_username: e.target.value})}
                        placeholder="your-email@gmail.com"
                        className="min-h-[44px]"
                      />
                    </div>
                    <div>
                      <Label>SMTP Password</Label>
                      <Input
                        type="password"
                        value={settings.email_password}
                        onChange={(e) => setSettings({...settings, email_password: e.target.value})}
                        placeholder="••••••••"
                        className="min-h-[44px]"
                      />
                    </div>
                  </div>
                  
                  <Button variant="outline" onClick={handleTestEmail} disabled={loading} className="min-h-[44px]">
                    <Mail className="w-4 h-4 mr-2" />
                    Test Kirim Email
                  </Button>
                </>
              )}
              
              <Button onClick={() => handleSaveSettings('notifications')} disabled={loading} className="min-h-[44px]">
                <Check className="w-4 h-4 mr-2" />
                Simpan Perubahan
              </Button>
            </div>
          </Card>

          <Card className="p-4 md:p-6">
            <h2 className="text-lg md:text-xl font-semibold text-slate-900 mb-4 flex items-center gap-2">
              <Smartphone className="w-5 h-5" />
              WhatsApp Notifications
            </h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label>Aktifkan Notifikasi WhatsApp</Label>
                  <p className="text-xs md:text-sm text-slate-500 mt-1">Kirim notifikasi via WhatsApp Business API</p>
                </div>
                <Switch
                  checked={settings.whatsapp_notifications}
                  onCheckedChange={(val) => setSettings({...settings, whatsapp_notifications: val})}
                />
              </div>
              
              {settings.whatsapp_notifications && (
                <div className="space-y-4">
                  <div>
                    <Label>WhatsApp API URL</Label>
                    <Input
                      value={settings.whatsapp_api_url}
                      onChange={(e) => setSettings({...settings, whatsapp_api_url: e.target.value})}
                      placeholder="https://api.whatsapp.com/..."
                      className="min-h-[44px]"
                    />
                  </div>
                  <div>
                    <Label>WhatsApp API Key</Label>
                    <Input
                      type="password"
                      value={settings.whatsapp_api_key}
                      onChange={(e) => setSettings({...settings, whatsapp_api_key: e.target.value})}
                      placeholder="••••••••••••••••"
                      className="min-h-[44px]"
                    />
                  </div>
                </div>
              )}
              
              <Button onClick={() => handleSaveSettings('notifications')} disabled={loading} className="min-h-[44px]">
                <Check className="w-4 h-4 mr-2" />
                Simpan Perubahan
              </Button>
            </div>
          </Card>

          <Card className="p-4 md:p-6">
            <h2 className="text-lg md:text-xl font-semibold text-slate-900 mb-4 flex items-center gap-2">
              <Bell className="w-5 h-5" />
              Push Notifications
            </h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label>Aktifkan Push Notifications</Label>
                  <p className="text-xs md:text-sm text-slate-500 mt-1">Notifikasi real-time di browser</p>
                </div>
                <Switch
                  checked={settings.push_notifications}
                  onCheckedChange={(val) => setSettings({...settings, push_notifications: val})}
                />
              </div>
              
              <Button onClick={() => handleSaveSettings('notifications')} disabled={loading} className="min-h-[44px]">
                <Check className="w-4 h-4 mr-2" />
                Simpan Perubahan
              </Button>
            </div>
          </Card>
        </TabsContent>

        {/* Data Management */}
        <TabsContent value="data" className="space-y-4 mt-4 md:mt-6">
          <Card className="p-4 md:p-6">
            <h2 className="text-lg md:text-xl font-semibold text-slate-900 mb-4 flex items-center gap-2">
              <Database className="w-5 h-5" />
              Manajemen Data
            </h2>
            <div className="space-y-4">
              <div className="p-4 bg-slate-50 rounded-lg border border-slate-200">
                <div className="flex items-start gap-3 mb-3">
                  <Database className="w-5 h-5 text-slate-600 flex-shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <h3 className="text-sm md:text-base font-semibold text-slate-900 mb-1">Backup Database</h3>
                    <p className="text-xs md:text-sm text-slate-600 mb-3">
                      Export semua data ke file JSON untuk backup atau migrasi.
                    </p>
                    <Button variant="outline" onClick={handleBackupDatabase} disabled={loading} className="min-h-[44px]">
                      <Download className="w-4 h-4 mr-2" />
                      Download Backup Sekarang
                    </Button>
                  </div>
                </div>
              </div>

              <div className="p-4 bg-slate-50 rounded-lg border border-slate-200">
                <div className="flex items-start gap-3">
                  <Upload className="w-5 h-5 text-slate-600 flex-shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <h3 className="text-sm md:text-base font-semibold text-slate-900 mb-1">Restore Database</h3>
                    <p className="text-xs md:text-sm text-slate-600 mb-3">
                      Restore data dari file backup JSON.
                    </p>
                    <Button variant="outline" disabled className="min-h-[44px]">
                      <Upload className="w-4 h-4 mr-2" />
                      Upload Backup File
                    </Button>
                  </div>
                </div>
              </div>

              <div>
                <Label>Data Retention (Hari)</Label>
                <Input
                  type="number"
                  value={settings.data_retention_days}
                  onChange={(e) => setSettings({...settings, data_retention_days: parseInt(e.target.value)})}
                  className="min-h-[44px]"
                />
                <p className="text-xs text-slate-500 mt-1">
                  Log aktivitas dan data lama akan dihapus otomatis setelah periode ini
                </p>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label>Auto Backup</Label>
                  <p className="text-xs md:text-sm text-slate-500 mt-1">Backup otomatis database secara berkala</p>
                </div>
                <Switch
                  checked={settings.auto_backup}
                  onCheckedChange={(val) => setSettings({...settings, auto_backup: val})}
                />
              </div>

              {settings.auto_backup && (
                <div>
                  <Label>Frekuensi Backup</Label>
                  <Select value={settings.backup_frequency} onValueChange={(val) => setSettings({...settings, backup_frequency: val})}>
                    <SelectTrigger className="min-h-[44px]">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="hourly">Setiap Jam</SelectItem>
                      <SelectItem value="daily">Harian (Jam 02:00)</SelectItem>
                      <SelectItem value="weekly">Mingguan (Minggu 02:00)</SelectItem>
                      <SelectItem value="monthly">Bulanan (Tanggal 1, 02:00)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              )}

              <Button onClick={() => handleSaveSettings('data')} disabled={loading} className="min-h-[44px]">
                <Check className="w-4 h-4 mr-2" />
                Simpan Perubahan
              </Button>
            </div>
          </Card>
        </TabsContent>

        {/* Security Settings */}
        <TabsContent value="security" className="space-y-4 mt-4 md:mt-6">
          <Card className="p-4 md:p-6">
            <h2 className="text-lg md:text-xl font-semibold text-slate-900 mb-4 flex items-center gap-2">
              <Shield className="w-5 h-5" />
              Keamanan Sistem
            </h2>
            <div className="space-y-4">
              <div>
                <Label>Session Timeout (menit)</Label>
                <Input
                  type="number"
                  value={settings.session_timeout}
                  onChange={(e) => setSettings({...settings, session_timeout: parseInt(e.target.value)})}
                  className="min-h-[44px]"
                />
                <p className="text-xs text-slate-500 mt-1">
                  User akan otomatis logout setelah tidak aktif selama periode ini
                </p>
              </div>

              <div>
                <Label>Password Expiry (Hari)</Label>
                <Input
                  type="number"
                  value={settings.password_expiry_days}
                  onChange={(e) => setSettings({...settings, password_expiry_days: parseInt(e.target.value)})}
                  className="min-h-[44px]"
                />
                <p className="text-xs text-slate-500 mt-1">
                  User harus mengganti password setelah periode ini
                </p>
              </div>

              <div>
                <Label>Max Login Attempts</Label>
                <Input
                  type="number"
                  value={settings.max_login_attempts}
                  onChange={(e) => setSettings({...settings, max_login_attempts: parseInt(e.target.value)})}
                  className="min-h-[44px]"
                />
                <p className="text-xs text-slate-500 mt-1">
                  Account akan di-lock setelah gagal login sebanyak ini
                </p>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label>Two-Factor Authentication</Label>
                  <p className="text-xs md:text-sm text-slate-500 mt-1">Aktifkan 2FA untuk keamanan ekstra</p>
                </div>
                <Switch
                  checked={settings.two_factor_auth}
                  onCheckedChange={(val) => setSettings({...settings, two_factor_auth: val})}
                />
              </div>

              <Button onClick={() => handleSaveSettings('security')} disabled={loading} className="min-h-[44px]">
                <Check className="w-4 h-4 mr-2" />
                Simpan Perubahan
              </Button>
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
