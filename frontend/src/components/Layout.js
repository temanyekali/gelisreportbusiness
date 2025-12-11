import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { getUser, clearAuth } from '../utils/auth';
import { Button } from './ui/button';
import {
  Building2, Home, ShoppingCart, DollarSign, Users, Bell,
  Settings, LogOut, Menu, X, FileText, Activity, Gift, Heart, Wrench
} from 'lucide-react';
import { Badge } from './ui/badge';

export default function Layout({ children }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [user, setUser] = useState(null);

  useEffect(() => {
    const userData = getUser();
    setUser(userData);
  }, []);

  const handleLogout = () => {
    clearAuth();
    navigate('/login');
  };

  // Strict permission matrix
  const navItems = [
    { path: '/dashboard', icon: Home, label: 'Dashboard', role: [1, 2, 3, 4, 5, 6, 7] },
    { path: '/businesses', icon: Building2, label: 'Bisnis', role: [1, 2] },
    { path: '/orders', icon: ShoppingCart, label: 'Pesanan', role: [1, 2, 5, 6] },
    { path: '/teknisi', icon: Wrench, label: 'Pekerjaan Teknisi', role: [1, 2, 5, 7] },
    { path: '/accounting', icon: DollarSign, label: 'Akunting', role: [1, 2, 3] },
    { path: '/users', icon: Users, label: 'Pengguna', role: [1, 2] },
    { path: '/reports', icon: FileText, label: 'Laporan', role: [1, 2, 3, 5, 6] },
    { path: '/loyalty', icon: Gift, label: 'Program Loyalitas', role: [1, 2] },
    { path: '/csr', icon: Heart, label: 'Program CSR', role: [1, 2] },
    { path: '/activity-logs', icon: Activity, label: 'Log Aktivitas', role: [1, 2] },
    { path: '/settings', icon: Settings, label: 'Pengaturan', role: [1] },
  ];

  const filteredNavItems = navItems.filter(item => {
    if (!item.role) return true;
    if (Array.isArray(item.role)) return item.role.includes(user?.role_id);
    return item.role === user?.role_id;
  });

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Sidebar */}
      <aside
        className={`fixed left-0 top-0 h-full bg-white border-r border-slate-200 transition-all duration-300 z-40 ${
          sidebarOpen ? 'w-64' : 'w-20'
        }`}
      >
        <div className="p-6 border-b border-slate-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-slate-900 rounded-lg flex items-center justify-center">
                <Building2 className="w-6 h-6 text-white" />
              </div>
              {sidebarOpen && <span className="text-xl font-bold text-slate-900">GELIS</span>}
            </div>
          </div>
        </div>

        <nav className="p-4">
          {filteredNavItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center space-x-3 px-4 py-3 rounded-lg mb-1 transition-all ${
                  isActive
                    ? 'bg-slate-900 text-white'
                    : 'text-slate-600 hover:bg-slate-100'
                }`}
                data-testid={`nav-${item.label.toLowerCase().replace(' ', '-')}`}
              >
                <Icon className="w-5 h-5 flex-shrink-0" />
                {sidebarOpen && <span className="font-medium">{item.label}</span>}
              </Link>
            );
          })}
        </nav>
      </aside>

      {/* Main Content */}
      <div className={`transition-all duration-300 ${
        sidebarOpen ? 'ml-64' : 'ml-20'
      }`}>
        {/* Top Bar */}
        <header className="bg-white border-b border-slate-200 sticky top-0 z-30">
          <div className="px-6 py-4 flex items-center justify-between">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setSidebarOpen(!sidebarOpen)}
              data-testid="toggle-sidebar-button"
            >
              {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </Button>

            <div className="flex items-center space-x-4">
              <Button variant="ghost" size="icon" data-testid="notifications-button">
                <Bell className="w-5 h-5" />
              </Button>

              <div className="flex items-center space-x-3 pl-4 border-l border-slate-200">
                <div className="text-right">
                  <p className="text-sm font-medium text-slate-900">{user?.full_name}</p>
                  <p className="text-xs text-slate-500">{user?.role_name}</p>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={handleLogout}
                  data-testid="logout-button"
                >
                  <LogOut className="w-5 h-5" />
                </Button>
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
