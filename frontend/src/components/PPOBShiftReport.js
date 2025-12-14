import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Download, Plus, RefreshCw, FileText, TrendingUp } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import axios from 'axios';
import { toast } from 'sonner';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || process.env.REACT_APP_BACKEND_URL;
const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

export default function PPOBShiftReport() {
  const [loading, setLoading] = useState(false);
  const [reports, setReports] = useState([]);
  const [businesses, setBusinesses] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [autoGenerating, setAutoGenerating] = useState(false);
  const [formData, setFormData] = useState({
    business_id: '',
    report_date: new Date().toISOString().split('T')[0],
    shift: 1,
    petugas_name: '',
    product_breakdown: [],
    notes: ''
  });

  const productTypes = [
    'Token PLN',
    'Pulsa',
    'PDAM',
    'Paket Data',
    'TV Kabel',
    'Internet',
    'Lainnya'
  ];

  useEffect(() => {
    fetchBusinesses();
    fetchReports();
  }, []);

  const fetchBusinesses = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${BACKEND_URL}/api/businesses`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const ppobBusinesses = response.data.businesses.filter(b => b.category === 'PPOB');
      setBusinesses(ppobBusinesses);
      if (ppobBusinesses.length > 0) {
        setFormData(prev => ({ ...prev, business_id: ppobBusinesses[0].id }));
      }
    } catch (error) {
      console.error('Error fetching businesses:', error);
    }
  };

  const fetchReports = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${BACKEND_URL}/api/reports/ppob-shift`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setReports(response.data.reports || []);
    } catch (error) {
      toast.error('Gagal memuat laporan PPOB');
    } finally {
      setLoading(false);
    }
  };

  const handleAutoGenerate = async () => {
    if (!formData.business_id || !formData.report_date || !formData.shift) {
      toast.error('Pilih business, tanggal, dan shift terlebih dahulu');
      return;
    }

    setAutoGenerating(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${BACKEND_URL}/api/reports/ppob-shift/auto-generate`,
        null,
        {
          params: {
            business_id: formData.business_id,
            report_date: formData.report_date,
            shift: formData.shift
          },
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      // Populate form with auto-generated data
      setFormData(prev => ({
        ...prev,
        product_breakdown: response.data.product_breakdown
      }));

      toast.success('Data berhasil digenerate otomatis dari transaksi');
    } catch (error) {
      toast.error('Gagal generate data: ' + (error.response?.data?.detail || error.message));
    } finally {
      setAutoGenerating(false);
    }
  };

  const handleProductChange = (index, field, value) => {
    const newBreakdown = [...formData.product_breakdown];
    newBreakdown[index] = { ...newBreakdown[index], [field]: parseFloat(value) || 0 };
    setFormData({ ...formData, product_breakdown: newBreakdown });
  };

  const addProduct = () => {
    setFormData({
      ...formData,
      product_breakdown: [
        ...formData.product_breakdown,
        {
          product_type: productTypes[0],
          transaction_count: 0,
          total_amount: 0,
          total_fee: 0,
          total_commission: 0
        }
      ]
    });
  };

  const removeProduct = (index) => {
    const newBreakdown = formData.product_breakdown.filter((_, i) => i !== index);
    setFormData({ ...formData, product_breakdown: newBreakdown });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.business_id || !formData.petugas_name) {
      toast.error('Harap isi semua field yang diperlukan');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      await axios.post(`${BACKEND_URL}/api/reports/ppob-shift`, formData, {
        headers: { Authorization: `Bearer ${token}` }
      });

      toast.success('Laporan shift PPOB berhasil disimpan');
      setShowForm(false);
      fetchReports();
      
      // Reset form
      setFormData({
        business_id: businesses[0]?.id || '',
        report_date: new Date().toISOString().split('T')[0],
        shift: 1,
        petugas_name: '',
        product_breakdown: [],
        notes: ''
      });
    } catch (error) {
      toast.error('Gagal menyimpan laporan: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleExport = async (reportId, format) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${BACKEND_URL}/api/reports/export`,
        {
          report_type: 'ppob_shift',
          format: format,
          filters: { report_id: reportId }
        },
        {
          headers: { Authorization: `Bearer ${token}` },
          responseType: 'blob'
        }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `ppob_shift_${new Date().getTime()}.${format === 'pdf' ? 'pdf' : 'xlsx'}`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success(`Laporan berhasil diexport sebagai ${format.toUpperCase()}`);
    } catch (error) {
      toast.error('Gagal export laporan');
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0
    }).format(value);
  };

  const calculateTotals = () => {
    if (!formData.product_breakdown.length) return { count: 0, amount: 0, fee: 0, commission: 0 };
    
    return {
      count: formData.product_breakdown.reduce((sum, p) => sum + (p.transaction_count || 0), 0),
      amount: formData.product_breakdown.reduce((sum, p) => sum + (p.total_amount || 0), 0),
      fee: formData.product_breakdown.reduce((sum, p) => sum + (p.total_fee || 0), 0),
      commission: formData.product_breakdown.reduce((sum, p) => sum + (p.total_commission || 0), 0)
    };
  };

  const totals = calculateTotals();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold">💳 Laporan Shift PPOB</h1>
          <p className="text-gray-500 mt-1">Akumulasi transaksi PPOB per shift dengan breakdown produk</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={() => setShowForm(!showForm)} className="bg-blue-600 hover:bg-blue-700">
            <Plus className="w-4 h-4 mr-2" />
            {showForm ? 'Tutup Form' : 'Buat Laporan'}
          </Button>
          <Button onClick={fetchReports} variant="outline">
            <RefreshCw className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Form */}
      {showForm && (
        <Card>
          <CardHeader>
            <CardTitle>📝 Form Laporan Shift PPOB</CardTitle>
            <CardDescription>Input manual atau auto-generate dari data transaksi</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Business</label>
                  <select
                    value={formData.business_id}
                    onChange={(e) => setFormData({ ...formData, business_id: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2"
                    required
                  >
                    <option value="">Pilih Business</option>
                    {businesses.map(b => (
                      <option key={b.id} value={b.id}>{b.name}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Nama Petugas</label>
                  <input
                    type="text"
                    value={formData.petugas_name}
                    onChange={(e) => setFormData({ ...formData, petugas_name: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2"
                    placeholder="Nama petugas shift"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Tanggal</label>
                  <input
                    type="date"
                    value={formData.report_date}
                    onChange={(e) => setFormData({ ...formData, report_date: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Shift</label>
                  <select
                    value={formData.shift}
                    onChange={(e) => setFormData({ ...formData, shift: parseInt(e.target.value) })}
                    className="w-full border rounded-lg px-3 py-2"
                    required
                  >
                    <option value={1}>Shift 1 (00:00 - 08:00)</option>
                    <option value={2}>Shift 2 (08:00 - 16:00)</option>
                    <option value={3}>Shift 3 (16:00 - 24:00)</option>
                  </select>
                </div>
              </div>

              <div className="flex gap-2">
                <Button
                  type="button"
                  onClick={handleAutoGenerate}
                  disabled={autoGenerating}
                  className="bg-purple-600 hover:bg-purple-700"
                >
                  <RefreshCw className={`w-4 h-4 mr-2 ${autoGenerating ? 'animate-spin' : ''}`} />
                  Auto-Generate dari Transaksi
                </Button>
                <Button type="button" onClick={addProduct} variant="outline">
                  <Plus className="w-4 h-4 mr-2" />
                  Tambah Produk
                </Button>
              </div>

              {/* Product Breakdown Table */}
              {formData.product_breakdown.length > 0 && (
                <div className="border rounded-lg overflow-hidden">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="text-left p-3">Jenis Produk</th>
                        <th className="text-right p-3">Jumlah Trx</th>
                        <th className="text-right p-3">Total Amount</th>
                        <th className="text-right p-3">Fee</th>
                        <th className="text-right p-3">Komisi</th>
                        <th className="p-3">Aksi</th>
                      </tr>
                    </thead>
                    <tbody>
                      {formData.product_breakdown.map((product, index) => (
                        <tr key={index} className="border-t">
                          <td className="p-2">
                            <select
                              value={product.product_type}
                              onChange={(e) => {
                                const newBreakdown = [...formData.product_breakdown];
                                newBreakdown[index].product_type = e.target.value;
                                setFormData({ ...formData, product_breakdown: newBreakdown });
                              }}
                              className="border rounded px-2 py-1"
                            >
                              {productTypes.map(type => (
                                <option key={type} value={type}>{type}</option>
                              ))}
                            </select>
                          </td>
                          <td className="p-2">
                            <input
                              type="number"
                              value={product.transaction_count}
                              onChange={(e) => handleProductChange(index, 'transaction_count', e.target.value)}
                              className="border rounded px-2 py-1 w-20 text-right"
                            />
                          </td>
                          <td className="p-2">
                            <input
                              type="number"
                              value={product.total_amount}
                              onChange={(e) => handleProductChange(index, 'total_amount', e.target.value)}
                              className="border rounded px-2 py-1 w-32 text-right"
                            />
                          </td>
                          <td className="p-2">
                            <input
                              type="number"
                              value={product.total_fee}
                              onChange={(e) => handleProductChange(index, 'total_fee', e.target.value)}
                              className="border rounded px-2 py-1 w-32 text-right"
                            />
                          </td>
                          <td className="p-2">
                            <input
                              type="number"
                              value={product.total_commission}
                              onChange={(e) => handleProductChange(index, 'total_commission', e.target.value)}
                              className="border rounded px-2 py-1 w-32 text-right"
                            />
                          </td>
                          <td className="p-2 text-center">
                            <Button
                              type="button"
                              onClick={() => removeProduct(index)}
                              variant="destructive"
                              size="sm"
                            >
                              Hapus
                            </Button>
                          </td>
                        </tr>
                      ))}
                      <tr className="border-t bg-blue-50 font-bold">
                        <td className="p-3">TOTAL</td>
                        <td className="p-3 text-right">{totals.count}</td>
                        <td className="p-3 text-right">{formatCurrency(totals.amount)}</td>
                        <td className="p-3 text-right">{formatCurrency(totals.fee)}</td>
                        <td className="p-3 text-right">{formatCurrency(totals.commission)}</td>
                        <td></td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium mb-2">Catatan</label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2"
                  rows="3"
                  placeholder="Catatan tambahan..."
                />
              </div>

              <div className="flex justify-end gap-2">
                <Button type="button" onClick={() => setShowForm(false)} variant="outline">
                  Batal
                </Button>
                <Button type="submit" className="bg-green-600 hover:bg-green-700">
                  <FileText className="w-4 h-4 mr-2" />
                  Simpan Laporan
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Reports List */}
      <div className="grid gap-4">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          </div>
        ) : reports.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <FileText className="w-16 h-16 text-gray-300 mb-4" />
              <p className="text-gray-500 text-lg">Belum ada laporan shift PPOB</p>
              <Button onClick={() => setShowForm(true)} className="mt-4">
                <Plus className="w-4 h-4 mr-2" />
                Buat Laporan Pertama
              </Button>
            </CardContent>
          </Card>
        ) : (
          reports.map((report, idx) => (
            <Card key={idx} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="text-lg">
                      Shift {report.shift} - {new Date(report.report_date).toLocaleDateString('id-ID')}
                    </CardTitle>
                    <CardDescription>
                      Petugas: {report.petugas_name} • Total: {report.total_transactions} transaksi
                    </CardDescription>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleExport(report.id, 'pdf')}
                    >
                      <Download className="w-4 h-4 mr-1" />
                      PDF
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleExport(report.id, 'excel')}
                    >
                      <Download className="w-4 h-4 mr-1" />
                      Excel
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-4 gap-4 mb-4">
                  <div className="bg-blue-50 rounded-lg p-3">
                    <div className="text-sm text-gray-600 mb-1">Total Amount</div>
                    <div className="text-lg font-bold text-blue-600">
                      {formatCurrency(report.total_amount)}
                    </div>
                  </div>
                  <div className="bg-green-50 rounded-lg p-3">
                    <div className="text-sm text-gray-600 mb-1">Total Fee</div>
                    <div className="text-lg font-bold text-green-600">
                      {formatCurrency(report.total_fee)}
                    </div>
                  </div>
                  <div className="bg-purple-50 rounded-lg p-3">
                    <div className="text-sm text-gray-600 mb-1">Total Komisi</div>
                    <div className="text-lg font-bold text-purple-600">
                      {formatCurrency(report.total_commission)}
                    </div>
                  </div>
                  <div className="bg-orange-50 rounded-lg p-3">
                    <div className="text-sm text-gray-600 mb-1">Transaksi</div>
                    <div className="text-lg font-bold text-orange-600">
                      {report.total_transactions}
                    </div>
                  </div>
                </div>

                {/* Product Breakdown */}
                {report.product_breakdown && report.product_breakdown.length > 0 && (
                  <div className="mt-4">
                    <h4 className="font-semibold mb-3">Breakdown Produk:</h4>
                    <div className="grid md:grid-cols-2 gap-4">
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead className="bg-gray-50">
                            <tr>
                              <th className="text-left p-2">Produk</th>
                              <th className="text-right p-2">Trx</th>
                              <th className="text-right p-2">Amount</th>
                            </tr>
                          </thead>
                          <tbody>
                            {report.product_breakdown.map((product, pidx) => (
                              <tr key={pidx} className="border-t">
                                <td className="p-2">{product.product_type}</td>
                                <td className="p-2 text-right">{product.transaction_count}</td>
                                <td className="p-2 text-right">{formatCurrency(product.total_amount)}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                      <div>
                        <ResponsiveContainer width="100%" height={200}>
                          <PieChart>
                            <Pie
                              data={report.product_breakdown}
                              dataKey="total_amount"
                              nameKey="product_type"
                              cx="50%"
                              cy="50%"
                              outerRadius={70}
                              label
                            >
                              {report.product_breakdown.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                              ))}
                            </Pie>
                            <Tooltip formatter={(value) => formatCurrency(value)} />
                          </PieChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
