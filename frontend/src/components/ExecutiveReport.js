import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Download, TrendingUp, TrendingDown, DollarSign, Package, AlertTriangle, Lightbulb, FileText } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts';
import axios from 'axios';
import { toast } from 'sonner';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || process.env.REACT_APP_BACKEND_URL;
const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316'];

export default function ExecutiveReport() {
  const [loading, setLoading] = useState(false);
  const [summaryData, setSummaryData] = useState(null);
  const [dateRange, setDateRange] = useState({
    start_date: new Date(new Date().setDate(new Date().getDate() - 30)).toISOString().split('T')[0],
    end_date: new Date().toISOString().split('T')[0]
  });
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    fetchSummary();
  }, []);

  const fetchSummary = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${BACKEND_URL}/api/reports/executive-summary`, {
        params: {
          start_date: `${dateRange.start_date}T00:00:00`,
          end_date: `${dateRange.end_date}T23:59:59`
        },
        headers: { Authorization: `Bearer ${token}` }
      });
      setSummaryData(response.data);
    } catch (error) {
      toast.error('Gagal memuat executive summary: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format) => {
    setExporting(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${BACKEND_URL}/api/reports/export`,
        {
          report_type: 'executive_summary',
          format: format,
          start_date: `${dateRange.start_date}T00:00:00`,
          end_date: `${dateRange.end_date}T23:59:59`
        },
        {
          headers: { Authorization: `Bearer ${token}` },
          responseType: 'blob'
        }
      );

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `executive_summary_${new Date().getTime()}.${format === 'pdf' ? 'pdf' : 'xlsx'}`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success(`Laporan berhasil diexport sebagai ${format.toUpperCase()}`);
    } catch (error) {
      toast.error('Gagal export laporan: ' + (error.response?.data?.detail || error.message));
    } finally {
      setExporting(false);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0
    }).format(value);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold">📊 Laporan Ringkasan Eksekutif</h1>
          <p className="text-gray-500 mt-1">Analisis kinerja komprehensif semua unit bisnis</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button onClick={() => handleExport('pdf')} disabled={exporting || !summaryData} className="bg-red-600 hover:bg-red-700">
            <Download className="w-4 h-4 mr-2" />
            Export PDF
          </Button>
          <Button onClick={() => handleExport('excel')} disabled={exporting || !summaryData} className="bg-green-600 hover:bg-green-700">
            <Download className="w-4 h-4 mr-2" />
            Export Excel
          </Button>
        </div>
      </div>

      {/* Date Range Filter */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-wrap gap-4 items-end">
            <div>
              <label className="block text-sm font-medium mb-2">Tanggal Mulai</label>
              <input
                type="date"
                value={dateRange.start_date}
                onChange={(e) => setDateRange({ ...dateRange, start_date: e.target.value })}
                className="border rounded-lg px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Tanggal Akhir</label>
              <input
                type="date"
                value={dateRange.end_date}
                onChange={(e) => setDateRange({ ...dateRange, end_date: e.target.value })}
                className="border rounded-lg px-3 py-2"
              />
            </div>
            <Button onClick={fetchSummary} disabled={loading}>
              <FileText className="w-4 h-4 mr-2" />
              Generate Laporan
            </Button>
          </div>
        </CardContent>
      </Card>

      {summaryData && (
        <>
          {/* Overall Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium flex items-center">
                  <DollarSign className="w-4 h-4 mr-2" />
                  Total Pendapatan
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatCurrency(summaryData.total_revenue)}</div>
                <div className="flex items-center mt-2 text-sm opacity-90">
                  <TrendingUp className="w-4 h-4 mr-1" />
                  Revenue Stream
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-red-500 to-red-600 text-white">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium flex items-center">
                  <DollarSign className="w-4 h-4 mr-2" />
                  Total Pengeluaran
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatCurrency(summaryData.total_expenses)}</div>
                <div className="flex items-center mt-2 text-sm opacity-90">
                  <TrendingDown className="w-4 h-4 mr-1" />
                  Expense Stream
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium flex items-center">
                  <DollarSign className="w-4 h-4 mr-2" />
                  Laba Bersih
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatCurrency(summaryData.net_profit)}</div>
                <div className="flex items-center mt-2 text-sm opacity-90">
                  {summaryData.net_profit >= 0 ? (
                    <TrendingUp className="w-4 h-4 mr-1" />
                  ) : (
                    <TrendingDown className="w-4 h-4 mr-1" />
                  )}
                  Net Profit
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium flex items-center">
                  <Package className="w-4 h-4 mr-2" />
                  Margin Keuntungan
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{summaryData.overall_profit_margin.toFixed(2)}%</div>
                <div className="flex items-center mt-2 text-sm opacity-90">
                  <TrendingUp className="w-4 h-4 mr-1" />
                  Profit Margin
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Top Performers */}
          <Card>
            <CardHeader>
              <CardTitle>🏆 Top Performers</CardTitle>
              <CardDescription>Unit bisnis dengan kinerja terbaik</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-3 gap-4">
                <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                  <div className="text-sm text-yellow-700 font-medium mb-1">Best Performing</div>
                  <div className="text-lg font-bold text-yellow-900">{summaryData.best_performing_business || 'N/A'}</div>
                </div>
                <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <div className="text-sm text-blue-700 font-medium mb-1">Highest Revenue</div>
                  <div className="text-lg font-bold text-blue-900">{summaryData.highest_revenue_business || 'N/A'}</div>
                </div>
                <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                  <div className="text-sm text-green-700 font-medium mb-1">Highest Margin</div>
                  <div className="text-lg font-bold text-green-900">{summaryData.highest_margin_business || 'N/A'}</div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Business Units Performance Chart */}
          <Card>
            <CardHeader>
              <CardTitle>📈 Kinerja Per Unit Bisnis</CardTitle>
              <CardDescription>Perbandingan pendapatan, pengeluaran, dan laba</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={summaryData.business_units}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="business_name" angle={-45} textAnchor="end" height={100} />
                  <YAxis />
                  <Tooltip formatter={(value) => formatCurrency(value)} />
                  <Legend />
                  <Bar dataKey="total_revenue" name="Pendapatan" fill="#3b82f6" />
                  <Bar dataKey="total_expenses" name="Pengeluaran" fill="#ef4444" />
                  <Bar dataKey="net_profit" name="Laba Bersih" fill="#10b981" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Profit Margin by Business */}
          <div className="grid md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>🎯 Margin Keuntungan per Bisnis</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={summaryData.business_units}
                      dataKey="total_revenue"
                      nameKey="business_name"
                      cx="50%"
                      cy="50%"
                      outerRadius={100}
                      label={(entry) => `${entry.business_name}: ${entry.profit_margin.toFixed(1)}%`}
                    >
                      {summaryData.business_units.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => formatCurrency(value)} />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>📦 Orders Completion Rate</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {summaryData.business_units.map((bu, index) => (
                    <div key={index}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="font-medium">{bu.business_name}</span>
                        <span className="text-gray-500">
                          {bu.completed_orders}/{bu.total_orders} ({bu.completion_rate.toFixed(1)}%)
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-500 h-2 rounded-full transition-all"
                          style={{ width: `${bu.completion_rate}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Alerts */}
          {summaryData.alerts && summaryData.alerts.length > 0 && (
            <Card className="border-orange-200 bg-orange-50">
              <CardHeader>
                <CardTitle className="flex items-center text-orange-800">
                  <AlertTriangle className="w-5 h-5 mr-2" />
                  Peringatan & Perhatian
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {summaryData.alerts.map((alert, index) => (
                    <div key={index} className="flex items-start p-3 bg-white rounded-lg border border-orange-200">
                      <AlertTriangle className="w-5 h-5 text-orange-500 mr-3 flex-shrink-0 mt-0.5" />
                      <span className="text-sm text-gray-700">{alert}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Insights & Recommendations */}
          <div className="grid md:grid-cols-2 gap-6">
            {summaryData.insights && summaryData.insights.length > 0 && (
              <Card className="border-blue-200 bg-blue-50">
                <CardHeader>
                  <CardTitle className="flex items-center text-blue-800">
                    <Lightbulb className="w-5 h-5 mr-2" />
                    Insights
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {summaryData.insights.map((insight, index) => (
                      <div key={index} className="flex items-start p-3 bg-white rounded-lg border border-blue-200">
                        <Lightbulb className="w-5 h-5 text-blue-500 mr-3 flex-shrink-0 mt-0.5" />
                        <span className="text-sm text-gray-700">{insight}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {summaryData.recommendations && summaryData.recommendations.length > 0 && (
              <Card className="border-green-200 bg-green-50">
                <CardHeader>
                  <CardTitle className="flex items-center text-green-800">
                    <TrendingUp className="w-5 h-5 mr-2" />
                    Rekomendasi
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {summaryData.recommendations.map((rec, index) => (
                      <div key={index} className="flex items-start p-3 bg-white rounded-lg border border-green-200">
                        <TrendingUp className="w-5 h-5 text-green-500 mr-3 flex-shrink-0 mt-0.5" />
                        <span className="text-sm text-gray-700">{rec}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Business Units Detail Table */}
          <Card>
            <CardHeader>
              <CardTitle>📋 Detail Unit Bisnis</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b bg-gray-50">
                      <th className="text-left p-3 font-medium">Unit Bisnis</th>
                      <th className="text-right p-3 font-medium">Pendapatan</th>
                      <th className="text-right p-3 font-medium">Pengeluaran</th>
                      <th className="text-right p-3 font-medium">Laba</th>
                      <th className="text-right p-3 font-medium">Margin</th>
                      <th className="text-right p-3 font-medium">Orders</th>
                      <th className="text-right p-3 font-medium">AOV</th>
                    </tr>
                  </thead>
                  <tbody>
                    {summaryData.business_units.map((bu, index) => (
                      <tr key={index} className="border-b hover:bg-gray-50">
                        <td className="p-3 font-medium">{bu.business_name}</td>
                        <td className="p-3 text-right">{formatCurrency(bu.total_revenue)}</td>
                        <td className="p-3 text-right">{formatCurrency(bu.total_expenses)}</td>
                        <td className={`p-3 text-right font-medium ${bu.net_profit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {formatCurrency(bu.net_profit)}
                        </td>
                        <td className={`p-3 text-right ${bu.profit_margin >= 20 ? 'text-green-600' : bu.profit_margin >= 10 ? 'text-yellow-600' : 'text-red-600'}`}>
                          {bu.profit_margin.toFixed(2)}%
                        </td>
                        <td className="p-3 text-right">
                          {bu.completed_orders}/{bu.total_orders}
                        </td>
                        <td className="p-3 text-right">{formatCurrency(bu.average_order_value)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
