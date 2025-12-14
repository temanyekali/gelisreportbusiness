import React, { useState, useEffect } from 'react';
import { useParams, Link, Routes, Route, useNavigate } from 'react-router-dom';
import api from '../api/axios';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { ArrowLeft, BarChart3, DollarSign, TrendingDown, ShoppingCart, FileText } from 'lucide-react';
import BusinessDashboard from './BusinessDashboard';
import IncomeForm from './IncomeForm';
import ExpenseForm from './ExpenseForm';
import Orders from './Orders';

export default function BusinessModule() {
  const { businessId } = useParams();
  const navigate = useNavigate();
  const [business, setBusiness] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBusiness();
  }, [businessId]);

  const fetchBusiness = async () => {
    try {
      const response = await api.get('/businesses');
      const biz = response.data.find(b => b.id === businessId);
      setBusiness(biz);
    } catch (err) {
      console.error('Error fetching business:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-slate-900 mx-auto"></div>
          <p className="mt-4 text-slate-600">Memuat...</p>
        </div>
      </div>
    );
  }

  if (!business) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="font-semibold text-red-900">Bisnis tidak ditemukan</h3>
          <p className="text-red-700">Bisnis dengan ID tersebut tidak ditemukan.</p>
          <Button
            onClick={() => navigate('/dashboard')}
            className="mt-4"
            variant="outline"
          >
            Kembali ke Dashboard
          </Button>
        </div>
      </div>
    );
  }

  // Main landing page for business module
  const BusinessLanding = () => (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button
            variant="outline"
            size="icon"
            onClick={() => navigate('/dashboard')}
          >
            <ArrowLeft className="w-4 h-4" />
          </Button>
          <div>
            <h1 className="text-2xl md:text-3xl font-bold text-slate-900">
              {business.name}
            </h1>
            <p className="text-slate-600 mt-1">{business.category}</p>
          </div>
        </div>
      </div>

      {/* Action Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card
          className="cursor-pointer hover:shadow-lg transition-shadow"
          onClick={() => navigate(`/business/${businessId}/dashboard`)}
        >
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-slate-900">
              <BarChart3 className="w-5 h-5" />
              <span>Dashboard</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-slate-600">
              Lihat statistik dan analitik bisnis
            </p>
          </CardContent>
        </Card>

        <Card
          className="cursor-pointer hover:shadow-lg transition-shadow"
          onClick={() => navigate(`/business/${businessId}/orders`)}
        >
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-slate-900">
              <ShoppingCart className="w-5 h-5" />
              <span>Pemesanan</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-slate-600">
              Kelola pesanan dan order bisnis
            </p>
          </CardContent>
        </Card>

        <Card
          className="cursor-pointer hover:shadow-lg transition-shadow"
          onClick={() => navigate(`/business/${businessId}/income`)}
        >
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-green-600">
              <DollarSign className="w-5 h-5" />
              <span>Pemasukan</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-slate-600">
              Catat dan kelola pemasukan
            </p>
          </CardContent>
        </Card>

        <Card
          className="cursor-pointer hover:shadow-lg transition-shadow"
          onClick={() => navigate(`/business/${businessId}/expense`)}
        >
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-red-600">
              <TrendingDown className="w-5 h-5" />
              <span>Pengeluaran</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-slate-600">
              Catat dan kelola pengeluaran
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Quick Info */}
      <Card>
        <CardHeader>
          <CardTitle>Informasi Bisnis</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-slate-600">Nama Bisnis</p>
              <p className="font-semibold text-slate-900">{business.name}</p>
            </div>
            <div>
              <p className="text-sm text-slate-600">Kategori</p>
              <p className="font-semibold text-slate-900">{business.category}</p>
            </div>
            {business.address && (
              <div>
                <p className="text-sm text-slate-600">Alamat</p>
                <p className="font-semibold text-slate-900">{business.address}</p>
              </div>
            )}
            {business.phone && (
              <div>
                <p className="text-sm text-slate-600">Telepon</p>
                <p className="font-semibold text-slate-900">{business.phone}</p>
              </div>
            )}
          </div>
          {business.description && (
            <div>
              <p className="text-sm text-slate-600">Deskripsi</p>
              <p className="text-slate-700">{business.description}</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );

  return (
    <Routes>
      <Route index element={<BusinessLanding />} />
      <Route path="dashboard" element={<BusinessDashboard />} />
      <Route path="orders" element={<Orders businessId={businessId} />} />
      <Route path="income" element={<IncomeForm />} />
      <Route path="expense" element={<ExpenseForm />} />
    </Routes>
  );
}
