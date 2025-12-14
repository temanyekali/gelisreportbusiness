import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { getUser, clearAuth } from '../utils/auth';
import { Button } from './ui/button';
import {
  Building2, Home, ShoppingCart, DollarSign, Users,
  Settings, LogOut, Menu, X, FileText, Activity, Gift, Heart, Wrench
} from 'lucide-react';
import { Badge } from './ui/badge';

export default function Layout({ children }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false); // Default false for mobile-first
  const [user, setUser] = useState(null);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const userData = getUser();
    setUser(userData);
    
    // Check screen size
    const checkMobile = () => {
      const mobile = window.innerWidth < 768;
      setIsMobile(mobile);
      if (!mobile) {
        setSidebarOpen(true); // Auto-open on desktop
      }
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
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
    { path: '/reports', icon: FileText, label: 'Laporan Harian', role: [1, 2, 3, 5, 6] },
    { path: '/reports/executive', icon: FileText, label: 'Ringkasan Eksekutif', role: [1, 2, 3] },
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

  // Close sidebar when clicking outside on mobile
  useEffect(() => {
    if (!isMobile || !sidebarOpen) return;
    
    const handleClickOutside = (e) => {
      const sidebar = document.getElementById('mobile-sidebar');
      const menuButton = document.getElementById('menu-button');
      
      if (sidebar && !sidebar.contains(e.target) && !menuButton?.contains(e.target)) {
        setSidebarOpen(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isMobile, sidebarOpen]);

  // Get top 4 most important nav items for mobile bottom nav
  const mobileBottomNavItems = filteredNavItems.slice(0, 4);

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Mobile Overlay */}
      {isMobile && sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-30 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        id="mobile-sidebar"
        className={`fixed left-0 top-0 h-full bg-white border-r border-slate-200 transition-all duration-300 z-40 overflow-y-auto
          ${isMobile 
            ? (sidebarOpen ? 'translate-x-0 w-64' : '-translate-x-full w-64') 
            : (sidebarOpen ? 'w-64' : 'w-20')
          }`}
      >
        <div className="p-4 md:p-6 border-b border-slate-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-slate-900 rounded-lg flex items-center justify-center">
                <Building2 className="w-6 h-6 text-white" />
              </div>
              {(sidebarOpen || !isMobile) && <span className="text-xl font-bold text-slate-900">GELIS</span>}
            </div>
            {isMobile && sidebarOpen && (
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setSidebarOpen(false)}
              >
                <X className="w-5 h-5" />
              </Button>
            )}
          </div>
        </div>

        <nav className="p-3 md:p-4 pb-20 md:pb-4">
          {filteredNavItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => isMobile && setSidebarOpen(false)}
                className={`flex items-center space-x-3 px-4 py-3 rounded-lg mb-1 transition-all min-h-[44px] ${
                  isActive
                    ? 'bg-slate-900 text-white'
                    : 'text-slate-600 hover:bg-slate-100'
                }`}
                data-testid={`nav-${item.label.toLowerCase().replace(' ', '-')}`}
              >
                <Icon className="w-5 h-5 flex-shrink-0" />
                {(sidebarOpen || !isMobile) && <span className="font-medium text-sm md:text-base">{item.label}</span>}
              </Link>
            );
          })}
        </nav>
      </aside>

      {/* Main Content */}
      <div className={`transition-all duration-300 pb-20 md:pb-0 ${
        isMobile ? 'ml-0' : (sidebarOpen ? 'ml-64' : 'ml-20')
      }`}>
        {/* Top Bar */}
        <header className="bg-white border-b border-slate-200 sticky top-0 z-30">
          <div className="px-3 md:px-6 py-3 md:py-4 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Button
                id="menu-button"
                variant="ghost"
                size="icon"
                onClick={() => setSidebarOpen(!sidebarOpen)}
                data-testid="toggle-sidebar-button"
                className="min-h-[44px] min-w-[44px]"
              >
                <Menu className="w-5 h-5" />
              </Button>
              {isMobile && (
                <div className="w-8 h-8 bg-slate-900 rounded-lg flex items-center justify-center">
                  <Building2 className="w-5 h-5 text-white" />
                </div>
              )}
            </div>

            <div className="flex items-center space-x-2 md:space-x-4">
              <Button 
                variant="ghost" 
                size="icon" 
                data-testid="notifications-button"
                className="min-h-[44px] min-w-[44px]"
              >
                <Bell className="w-5 h-5" />
              </Button>

              <div className="hidden sm:flex items-center space-x-3 pl-4 border-l border-slate-200">
                <div className="text-right">
                  <p className="text-sm font-medium text-slate-900 truncate max-w-[150px]">{user?.full_name}</p>
                  <p className="text-xs text-slate-500">{user?.role_name}</p>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={handleLogout}
                  data-testid="logout-button"
                  className="min-h-[44px] min-w-[44px]"
                >
                  <LogOut className="w-5 h-5" />
                </Button>
              </div>
              
              {/* Mobile Logout Button */}
              <Button
                variant="ghost"
                size="icon"
                onClick={handleLogout}
                className="sm:hidden min-h-[44px] min-w-[44px]"
              >
                <LogOut className="w-5 h-5" />
              </Button>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="p-3 md:p-6">
          {children}
        </main>
      </div>

      {/* Mobile Bottom Navigation */}
      {isMobile && (
        <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-slate-200 z-40 md:hidden">
          <div className="grid grid-cols-4 gap-1">
            {mobileBottomNavItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex flex-col items-center justify-center py-2 px-1 transition-colors min-h-[60px] ${
                    isActive
                      ? 'text-slate-900 bg-slate-50'
                      : 'text-slate-500 hover:text-slate-900'
                  }`}
                >
                  <Icon className="w-6 h-6 mb-1" />
                  <span className="text-xs font-medium truncate max-w-full">{item.label}</span>
                </Link>
              );
            })}
          </div>
        </nav>
      )}
    </div>
  );
}
