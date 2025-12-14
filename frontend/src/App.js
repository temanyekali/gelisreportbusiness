import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from './components/ui/sonner';
import { isAuthenticated, getUser } from './utils/auth';
import { api } from './utils/api';
import Login from './components/Login';
import Layout from './components/Layout';
import Dashboard from './components/Dashboard';
import './App.css';
import { toast } from 'sonner';

// Import actual components
import Businesses from './components/Businesses';
import Orders from './components/Orders';
import Reports from './components/Reports';
import TeknisiDashboard from './components/TeknisiDashboard';
import Accounting from './components/Accounting';
import Users from './components/Users';
import Loyalty from './components/Loyalty';
import CSR from './components/CSR';
import ActivityLogs from './components/ActivityLogs';
import Settings from './components/Settings';
import ExecutiveReport from './components/ExecutiveReport';
import BusinessModule from './components/BusinessModule';
import DeveloperTools from './components/DeveloperTools';

const PrivateRoute = ({ children }) => {
  return isAuthenticated() ? children : <Navigate to="/login" />;
};

// Role-based route protection
const RoleBasedRoute = ({ children, allowedRoles }) => {
  const [hasShownError, setHasShownError] = useState(false);
  
  if (!isAuthenticated()) {
    return <Navigate to="/login" />;
  }
  
  const user = getUser();
  
  // If user data not yet loaded, wait
  if (!user || typeof user.role_id === 'undefined') {
    return null;
  }
  
  // Check if user role is allowed
  if (allowedRoles && !allowedRoles.includes(user.role_id)) {
    // Only show error once to avoid spam
    if (!hasShownError) {
      toast.error('Anda tidak memiliki akses ke halaman ini');
      setHasShownError(true);
    }
    return <Navigate to="/dashboard" />;
  }
  
  return children;
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
          <RoleBasedRoute allowedRoles={[1, 2, 3, 4, 5, 6, 7, 8]}>
            <Layout><Dashboard /></Layout>
          </RoleBasedRoute>
        } />
        
        <Route path="/businesses" element={
          <RoleBasedRoute allowedRoles={[1, 2, 8]}>
            <Layout><Businesses /></Layout>
          </RoleBasedRoute>
        } />
        
        <Route path="/orders" element={
          <RoleBasedRoute allowedRoles={[1, 2, 5, 6, 8]}>
            <Layout><Orders /></Layout>
          </RoleBasedRoute>
        } />
        
        <Route path="/transactions" element={
          <RoleBasedRoute allowedRoles={[1, 2, 3, 8]}>
            <Layout><Accounting /></Layout>
          </RoleBasedRoute>
        } />
        
        <Route path="/accounting" element={
          <RoleBasedRoute allowedRoles={[1, 2, 3, 8]}>
            <Layout><Accounting /></Layout>
          </RoleBasedRoute>
        } />
        
        <Route path="/users" element={
          <RoleBasedRoute allowedRoles={[1, 2, 8]}>
            <Layout><Users /></Layout>
          </RoleBasedRoute>
        } />
        
        <Route path="/reports" element={
          <RoleBasedRoute allowedRoles={[1, 2, 3, 5, 6, 8]}>
            <Layout><Reports /></Layout>
          </RoleBasedRoute>
        } />
        
        <Route path="/loyalty" element={
          <RoleBasedRoute allowedRoles={[1, 2, 8]}>
            <Layout><Loyalty /></Layout>
          </RoleBasedRoute>
        } />
        
        <Route path="/csr" element={
          <RoleBasedRoute allowedRoles={[1, 2, 8]}>
            <Layout><CSR /></Layout>
          </RoleBasedRoute>
        } />
        
        <Route path="/activity-logs" element={
          <RoleBasedRoute allowedRoles={[1, 2, 8]}>
            <Layout><ActivityLogs /></Layout>
          </RoleBasedRoute>
        } />
        
        <Route path="/settings" element={
          <RoleBasedRoute allowedRoles={[1, 8]}>
            <Layout><Settings /></Layout>
          </RoleBasedRoute>
        } />
        
        <Route path="/teknisi" element={
          <RoleBasedRoute allowedRoles={[1, 2, 5, 7, 8]}>
            <Layout><TeknisiDashboard /></Layout>
          </RoleBasedRoute>
        } />
        
        <Route path="/dev-tools" element={
          <RoleBasedRoute allowedRoles={[8]}>
            <Layout><DeveloperTools /></Layout>
          </RoleBasedRoute>
        } />

        
        <Route path="/reports/executive" element={
          <RoleBasedRoute allowedRoles={[1, 2, 3, 8]}>
            <Layout><ExecutiveReport /></Layout>
          </RoleBasedRoute>
        } />
        
        <Route path="/business/:businessId/*" element={
          <RoleBasedRoute allowedRoles={[1, 2, 8]}>
            <Layout><BusinessModule /></Layout>
          </RoleBasedRoute>
        } />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
