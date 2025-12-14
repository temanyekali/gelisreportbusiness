import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Download, FileText } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export default function ExecutiveReport() {
  const [loading, setLoading] = useState(false);
  const [summaryData, setSummaryData] = useState(null);
  const [dateRange, setDateRange] = useState({
    start_date: new Date(new Date().setDate(new Date().getDate() - 30)).toISOString().split('T')[0],
    end_date: new Date().toISOString().split('T')[0]
  });

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
      toast.success('Executive summary loaded successfully');
    } catch (error) {
      toast.error('Failed to load executive summary: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
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
    <div className="space-y-6 p-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold">📊 Laporan Ringkasan Eksekutif</h1>
          <p className="text-gray-500 mt-1">Analisis kinerja komprehensif semua unit bisnis</p>
        </div>
      </div>

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
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">Total Pendapatan</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatCurrency(summaryData.total_revenue)}</div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-red-500 to-red-600 text-white">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">Total Pengeluaran</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatCurrency(summaryData.total_expenses)}</div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">Laba Bersih</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatCurrency(summaryData.net_profit)}</div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">Margin Keuntungan</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{summaryData.overall_profit_margin.toFixed(2)}%</div>
              </CardContent>
            </Card>
          </div>

          {summaryData.business_units && summaryData.business_units.length > 0 && (
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
                          <td className="p-3 text-right">{bu.profit_margin.toFixed(2)}%</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}

          {summaryData.alerts && summaryData.alerts.length > 0 && (
            <Card className="border-orange-200 bg-orange-50">
              <CardHeader>
                <CardTitle className="text-orange-800">⚠️ Peringatan & Perhatian</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {summaryData.alerts.map((alert, index) => (
                    <div key={index} className="p-3 bg-white rounded-lg border border-orange-200">
                      <span className="text-sm text-gray-700">{alert}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  );
}
