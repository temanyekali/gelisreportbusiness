import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from './components/ui/sonner';
import { isAuthenticated } from './utils/auth';
import { api } from './utils/api';
import Login from './components/Login';
import Layout from './components/Layout';
import Dashboard from './components/Dashboard';
import './App.css';

// Import actual components
import Businesses from './components/Businesses';
import Orders from './components/Orders';
import Reports from './components/Reports';
import TeknisiDashboard from './components/TeknisiDashboard';
import Accounting from './components/Accounting';
const Users = () => <div className="p-6"><h1 className="text-3xl font-bold">Manajemen Pengguna</h1><p className="mt-4 text-slate-600">Module dalam pengembangan...</p></div>;
const Loyalty = () => <div className="p-6"><h1 className="text-3xl font-bold">Program Loyalitas</h1><p className="mt-4 text-slate-600">Module dalam pengembangan...</p></div>;
const CSR = () => <div className="p-6"><h1 className="text-3xl font-bold">Program CSR</h1><p className="mt-4 text-slate-600">Module dalam pengembangan...</p></div>;
const ActivityLogs = () => <div className="p-6"><h1 className="text-3xl font-bold">Log Aktivitas</h1><p className="mt-4 text-slate-600">Module dalam pengembangan...</p></div>;
const Settings = () => <div className="p-6"><h1 className="text-3xl font-bold">Pengaturan Sistem</h1><p className="mt-4 text-slate-600">Module dalam pengembangan...</p></div>;

const PrivateRoute = ({ children }) => {
  return isAuthenticated() ? children : <Navigate to="/login" />;
};

const InitData = () => {
  const [initialized, setInitialized] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initData = async () => {
      try {
        const response = await api.post('/init-data');
        console.log('Init response:', response.data);
        setInitialized(true);
      } catch (error) {
        console.log('Init may have already run:', error.response?.data);
        setInitialized(true);
      } finally {
        setLoading(false);
      }
    };

    initData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-slate-300 border-t-slate-900 rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-slate-600">Mempersiapkan sistem...</p>
        </div>
      </div>
    );
  }

  return <Navigate to="/login" />;
};

function App() {
  return (
    <BrowserRouter>
      <Toaster position="top-right" />
      <Routes>
        <Route path="/" element={<InitData />} />
        <Route path="/login" element={<Login />} />
        
        <Route path="/dashboard" element={
          <PrivateRoute>
            <Layout><Dashboard /></Layout>
          </PrivateRoute>
        } />
        
        <Route path="/businesses" element={
          <PrivateRoute>
            <Layout><Businesses /></Layout>
          </PrivateRoute>
        } />
        
        <Route path="/orders" element={
          <PrivateRoute>
            <Layout><Orders /></Layout>
          </PrivateRoute>
        } />
        
        <Route path="/transactions" element={
          <PrivateRoute>
            <Layout><Accounting /></Layout>
          </PrivateRoute>
        } />
        
        <Route path="/accounting" element={
          <PrivateRoute>
            <Layout><Accounting /></Layout>
          </PrivateRoute>
        } />
        
        <Route path="/users" element={
          <PrivateRoute>
            <Layout><Users /></Layout>
          </PrivateRoute>
        } />
        
        <Route path="/reports" element={
          <PrivateRoute>
            <Layout><Reports /></Layout>
          </PrivateRoute>
        } />
        
        <Route path="/loyalty" element={
          <PrivateRoute>
            <Layout><Loyalty /></Layout>
          </PrivateRoute>
        } />
        
        <Route path="/csr" element={
          <PrivateRoute>
            <Layout><CSR /></Layout>
          </PrivateRoute>
        } />
        
        <Route path="/activity-logs" element={
          <PrivateRoute>
            <Layout><ActivityLogs /></Layout>
          </PrivateRoute>
        } />
        
        <Route path="/settings" element={
          <PrivateRoute>
            <Layout><Settings /></Layout>
          </PrivateRoute>
        } />
        
        <Route path="/teknisi" element={
          <PrivateRoute>
            <Layout><TeknisiDashboard /></Layout>
          </PrivateRoute>
        } />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
