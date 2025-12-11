import React, { useState, useEffect } from 'react';
import { api } from '../utils/api';
import { Card } from './ui/card';
import { Building2, ShoppingCart, TrendingUp, TrendingDown, Clock, CheckCircle2 } from 'lucide-react';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const StatCard = ({ title, value, subtitle, icon: Icon, trend, color = 'slate' }) => {
  const colorClasses = {
    slate: 'bg-slate-100 text-slate-900',
    blue: 'bg-blue-100 text-blue-900',
    green: 'bg-green-100 text-green-900',
    orange: 'bg-orange-100 text-orange-900',
  };

  return (
    <Card className="p-6 hover:shadow-md transition-shadow duration-200" data-testid={`stat-card-${title.toLowerCase().replace(' ', '-')}`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-slate-500 font-medium mb-1">{title}</p>
          <h3 className="text-3xl font-bold text-slate-900 tracking-tight mb-2">{value}</h3>
          {subtitle && <p className="text-sm text-slate-600">{subtitle}</p>}
        </div>
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${colorClasses[color]}`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
      {trend && (
        <div className={`mt-3 flex items-center text-sm ${trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
          {trend > 0 ? <TrendingUp className="w-4 h-4 mr-1" /> : <TrendingDown className="w-4 h-4 mr-1" />}
          <span className="font-medium">{Math.abs(trend)}%</span>
          <span className="text-slate-500 ml-1">vs bulan lalu</span>
        </div>
      )}
    </Card>
  );
};

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await api.get('/dashboard/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-slate-500">Memuat data...</div>
      </div>
    );
  }

  // Sample data for charts
  const revenueData = [
    { name: 'Jan', pendapatan: 45000000, pengeluaran: 32000000 },
    { name: 'Feb', pendapatan: 52000000, pengeluaran: 35000000 },
    { name: 'Mar', pendapatan: 48000000, pengeluaran: 33000000 },
    { name: 'Apr', pendapatan: 61000000, pengeluaran: 38000000 },
    { name: 'Mei', pendapatan: 55000000, pengeluaran: 36000000 },
    { name: 'Jun', pendapatan: stats?.total_revenue || 65000000, pengeluaran: stats?.total_expenses || 40000000 },
  ];

  const businessData = [
    { name: 'PPOB', value: 35, color: '#2563EB' },
    { name: 'PLN', value: 25, color: '#10B981' },
    { name: 'Travel', value: 20, color: '#F59E0B' },
    { name: 'PDAM', value: 12, color: '#8B5CF6' },
    { name: 'Lainnya', value: 8, color: '#64748B' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold text-slate-900 tracking-tight mb-2">Dashboard GELIS</h1>
        <p className="text-slate-600">Gerbang Elektronik Layanan Informasi Sistem - Monitoring Terpadu Multi-Bisnis</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Bisnis"
          value={stats?.total_businesses || 0}
          subtitle="Bisnis aktif"
          icon={Building2}
          color="blue"
        />
        <StatCard
          title="Pesanan Aktif"
          value={stats?.active_orders || 0}
          subtitle={`${stats?.pending_orders || 0} pending`}
          icon={Clock}
          color="orange"
        />
        <StatCard
          title="Pendapatan Hari Ini"
          value={formatCurrency(stats?.revenue_today || 0)}
          subtitle={`Net: ${formatCurrency(stats?.net_today || 0)}`}
          icon={TrendingUp}
          color="green"
          trend={8.5}
        />
        <StatCard
          title="Pesanan Selesai"
          value={stats?.completed_orders_today || 0}
          subtitle="Hari ini"
          icon={CheckCircle2}
          color="slate"
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Revenue Trend */}
        <Card className="p-6 lg:col-span-2">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">Trend Pendapatan & Pengeluaran</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={revenueData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
              <XAxis dataKey="name" stroke="#64748B" style={{ fontSize: '12px' }} />
              <YAxis stroke="#64748B" style={{ fontSize: '12px' }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #E2E8F0',
                  borderRadius: '8px',
                }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="pendapatan"
                stroke="#10B981"
                strokeWidth={3}
                dot={{ fill: '#10B981', r: 4 }}
              />
              <Line
                type="monotone"
                dataKey="pengeluaran"
                stroke="#EF4444"
                strokeWidth={3}
                dot={{ fill: '#EF4444', r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        {/* Business Distribution */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">Distribusi Bisnis</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={businessData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {businessData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="p-6 bg-gradient-to-br from-slate-900 to-slate-800 text-white">
          <h3 className="text-sm font-medium opacity-90 mb-2">Total Pendapatan</h3>
          <p className="text-3xl font-bold tracking-tight">{formatCurrency(stats?.total_revenue || 0)}</p>
          <p className="text-sm opacity-75 mt-2">Akumulasi semua bisnis</p>
        </Card>

        <Card className="p-6 bg-gradient-to-br from-red-600 to-red-700 text-white">
          <h3 className="text-sm font-medium opacity-90 mb-2">Total Pengeluaran</h3>
          <p className="text-3xl font-bold tracking-tight">{formatCurrency(stats?.total_expenses || 0)}</p>
          <p className="text-sm opacity-75 mt-2">Akumulasi semua bisnis</p>
        </Card>

        <Card className="p-6 bg-gradient-to-br from-green-600 to-green-700 text-white">
          <h3 className="text-sm font-medium opacity-90 mb-2">Net Profit</h3>
          <p className="text-3xl font-bold tracking-tight">
            {formatCurrency((stats?.total_revenue || 0) - (stats?.total_expenses || 0))}
          </p>
          <p className="text-sm opacity-75 mt-2">
            Margin: {(((stats?.total_revenue - stats?.total_expenses) / stats?.total_revenue) * 100 || 0).toFixed(1)}%
          </p>
        </Card>
      </div>
    </div>
  );
}
