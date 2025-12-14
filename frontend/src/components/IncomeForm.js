import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api/axios';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { ArrowLeft, Plus, Trash2 } from 'lucide-react';
import { Badge } from './ui/badge';

const INCOME_CATEGORIES = [
  { value: 'sales', label: 'Penjualan Produk/Jasa' },
  { value: 'payment', label: 'Pembayaran Customer' },
  { value: 'deposit', label: 'Setoran/Deposit' },
  { value: 'admin_fee', label: 'Fee Admin' },
  { value: 'commission', label: 'Komisi' },
  { value: 'refund_received', label: 'Refund Diterima' },
  { value: 'other_income', label: 'Pemasukan Lainnya' }
];

const PAYMENT_METHODS = ['cash', 'transfer', 'card', 'e-wallet', 'other'];

export default function IncomeForm() {
  const { businessId } = useParams();
  const navigate = useNavigate();
  const [business, setBusiness] = useState(null);
  const [incomes, setIncomes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [formData, setFormData] = useState({
    category: 'sales',
    description: '',
    amount: '',
    payment_method: 'cash',
    reference_number: '',
    customer_name: '',
    notes: '',
    transaction_date: new Date().toISOString().split('T')[0]
  });

  useEffect(() => {
    fetchBusinessData();
    fetchIncomes();
  }, [businessId]);

  const fetchBusinessData = async () => {
    try {
      const response = await api.get('/businesses');
      const biz = response.data.find(b => b.id === businessId);
      setBusiness(biz);
    } catch (err) {
      console.error('Error fetching business:', err);
    }
  };

  const fetchIncomes = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/business/${businessId}/income`);
      setIncomes(response.data);
    } catch (err) {
      console.error('Error fetching incomes:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!formData.description || !formData.amount) {
      setError('Deskripsi dan jumlah harus diisi');
      return;
    }

    try {
      setSubmitting(true);
      await api.post(`/business/${businessId}/income`, {
        ...formData,
        amount: parseFloat(formData.amount)
      });

      setSuccess('Data pemasukan berhasil ditambahkan!');
      
      // Reset form
      setFormData({
        category: 'sales',
        description: '',
        amount: '',
        payment_method: 'cash',
        reference_number: '',
        customer_name: '',
        notes: '',
        transaction_date: new Date().toISOString().split('T')[0]
      });

      // Refresh list
      fetchIncomes();

      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Gagal menambahkan data pemasukan');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (incomeId) => {
    if (!window.confirm('Yakin ingin menghapus data pemasukan ini?')) return;

    try {
      await api.delete(`/business/${businessId}/income/${incomeId}`);
      setSuccess('Data pemasukan berhasil dihapus!');
      fetchIncomes();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Gagal menghapus data');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button
            variant="outline"
            size="icon"
            onClick={() => navigate(`/business/${businessId}`)}
          >
            <ArrowLeft className="w-4 h-4" />
          </Button>
          <div>
            <h1 className="text-2xl md:text-3xl font-bold text-slate-900">
              Pemasukan - {business?.name}
            </h1>
            <p className="text-slate-600 mt-1">Kelola pemasukan bisnis</p>
          </div>
        </div>
      </div>

      {/* Alert Messages */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
          {error}
        </div>
      )}
      {success && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-green-700">
          {success}
        </div>
      )}

      {/* Form */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Plus className="w-5 h-5" />
            <span>Tambah Pemasukan Baru</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Category */}
              <div>
                <Label htmlFor="category">Kategori Pemasukan *</Label>
                <select
                  id="category"
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-900"
                  required
                >
                  {INCOME_CATEGORIES.map(cat => (
                    <option key={cat.value} value={cat.value}>{cat.label}</option>
                  ))}
                </select>
              </div>

              {/* Amount */}
              <div>
                <Label htmlFor="amount">Jumlah (Rp) *</Label>
                <Input
                  id="amount"
                  type="number"
                  value={formData.amount}
                  onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                  placeholder="0"
                  min="0"
                  step="1"
                  required
                />
              </div>

              {/* Description */}
              <div className="md:col-span-2">
                <Label htmlFor="description">Deskripsi *</Label>
                <Input
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Contoh: Pembayaran customer untuk layanan X"
                  required
                />
              </div>

              {/* Customer Name */}
              <div>
                <Label htmlFor="customer_name">Nama Customer</Label>
                <Input
                  id="customer_name"
                  value={formData.customer_name}
                  onChange={(e) => setFormData({ ...formData, customer_name: e.target.value })}
                  placeholder="Nama customer (opsional)"
                />
              </div>

              {/* Payment Method */}
              <div>
                <Label htmlFor="payment_method">Metode Pembayaran</Label>
                <select
                  id="payment_method"
                  value={formData.payment_method}
                  onChange={(e) => setFormData({ ...formData, payment_method: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-900"
                >
                  {PAYMENT_METHODS.map(method => (
                    <option key={method} value={method}>
                      {method.toUpperCase()}
                    </option>
                  ))}
                </select>
              </div>

              {/* Reference Number */}
              <div>
                <Label htmlFor="reference_number">Nomor Referensi</Label>
                <Input
                  id="reference_number"
                  value={formData.reference_number}
                  onChange={(e) => setFormData({ ...formData, reference_number: e.target.value })}
                  placeholder="Invoice/Receipt number"
                />
              </div>

              {/* Transaction Date */}
              <div>
                <Label htmlFor="transaction_date">Tanggal Transaksi</Label>
                <Input
                  id="transaction_date"
                  type="date"
                  value={formData.transaction_date}
                  onChange={(e) => setFormData({ ...formData, transaction_date: e.target.value })}
                  required
                />
              </div>

              {/* Notes */}
              <div className="md:col-span-2">
                <Label htmlFor="notes">Catatan</Label>
                <Textarea
                  id="notes"
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  placeholder="Catatan tambahan (opsional)"
                  rows={3}
                />
              </div>
            </div>

            <div className="flex justify-end">
              <Button type="submit" disabled={submitting}>
                {submitting ? 'Menyimpan...' : 'Simpan Pemasukan'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Income List */}
      <Card>
        <CardHeader>
          <CardTitle>Riwayat Pemasukan</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-slate-500">Memuat data...</div>
          ) : incomes.length === 0 ? (
            <div className="text-center py-8 text-slate-500">Belum ada data pemasukan</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-200">
                    <th className="text-left py-3 px-4 font-semibold text-slate-700">Tanggal</th>
                    <th className="text-left py-3 px-4 font-semibold text-slate-700">Kategori</th>
                    <th className="text-left py-3 px-4 font-semibold text-slate-700">Deskripsi</th>
                    <th className="text-left py-3 px-4 font-semibold text-slate-700">Customer</th>
                    <th className="text-right py-3 px-4 font-semibold text-slate-700">Jumlah</th>
                    <th className="text-center py-3 px-4 font-semibold text-slate-700">Aksi</th>
                  </tr>
                </thead>
                <tbody>
                  {incomes.map((income) => (
                    <tr key={income.id} className="border-b border-slate-100 hover:bg-slate-50">
                      <td className="py-3 px-4 text-sm">
                        {new Date(income.transaction_date).toLocaleDateString('id-ID')}
                      </td>
                      <td className="py-3 px-4">
                        <Badge variant="outline">
                          {INCOME_CATEGORIES.find(c => c.value === income.category)?.label || income.category}
                        </Badge>
                      </td>
                      <td className="py-3 px-4 text-sm">{income.description}</td>
                      <td className="py-3 px-4 text-sm">{income.customer_name || '-'}</td>
                      <td className="py-3 px-4 text-right font-semibold text-green-600">
                        Rp {income.amount.toLocaleString('id-ID')}
                      </td>
                      <td className="py-3 px-4 text-center">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDelete(income.id)}
                          className="text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
