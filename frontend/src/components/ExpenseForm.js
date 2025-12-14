import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../utils/api';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { CurrencyInput } from './ui/currency-input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { ArrowLeft, Plus, Trash2 } from 'lucide-react';
import { Badge } from './ui/badge';

const EXPENSE_CATEGORIES = [
  { value: 'salary', label: 'Gaji Karyawan' },
  { value: 'operational', label: 'Operasional' },
  { value: 'supplies', label: 'Perlengkapan' },
  { value: 'utilities', label: 'Listrik, Air, Internet' },
  { value: 'transportation', label: 'Transportasi' },
  { value: 'maintenance', label: 'Perawatan' },
  { value: 'marketing', label: 'Marketing/Promosi' },
  { value: 'purchase', label: 'Pembelian Barang' },
  { value: 'refund_paid', label: 'Refund Dibayarkan' },
  { value: 'other_expense', label: 'Pengeluaran Lainnya' }
];

const PAYMENT_METHODS = ['cash', 'transfer', 'card', 'e-wallet', 'other'];

export default function ExpenseForm() {
  const { businessId } = useParams();
  const navigate = useNavigate();
  const [business, setBusiness] = useState(null);
  const [expenses, setExpenses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [formData, setFormData] = useState({
    category: 'operational',
    description: '',
    amount: '',
    payment_method: 'cash',
    reference_number: '',
    vendor_name: '',
    notes: '',
    transaction_date: new Date().toISOString().split('T')[0]
  });

  useEffect(() => {
    fetchBusinessData();
    fetchExpenses();
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

  const fetchExpenses = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/business/${businessId}/expense`);
      setExpenses(response.data);
    } catch (err) {
      console.error('Error fetching expenses:', err);
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
      await api.post(`/business/${businessId}/expense`, {
        ...formData,
        amount: parseFloat(formData.amount)
      });

      setSuccess('Data pengeluaran berhasil ditambahkan!');
      
      // Reset form
      setFormData({
        category: 'operational',
        description: '',
        amount: '',
        payment_method: 'cash',
        reference_number: '',
        vendor_name: '',
        notes: '',
        transaction_date: new Date().toISOString().split('T')[0]
      });

      // Refresh list
      fetchExpenses();

      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Gagal menambahkan data pengeluaran');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (expenseId) => {
    if (!window.confirm('Yakin ingin menghapus data pengeluaran ini?')) return;

    try {
      await api.delete(`/business/${businessId}/expense/${expenseId}`);
      setSuccess('Data pengeluaran berhasil dihapus!');
      fetchExpenses();
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
              Pengeluaran - {business?.name}
            </h1>
            <p className="text-slate-600 mt-1">Kelola pengeluaran bisnis</p>
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
            <span>Tambah Pengeluaran Baru</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Category */}
              <div>
                <Label htmlFor="category">Kategori Pengeluaran *</Label>
                <select
                  id="category"
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-900"
                  required
                >
                  {EXPENSE_CATEGORIES.map(cat => (
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
                  placeholder="Contoh: Pembayaran gaji karyawan bulan ini"
                  required
                />
              </div>

              {/* Vendor Name */}
              <div>
                <Label htmlFor="vendor_name">Nama Vendor/Supplier</Label>
                <Input
                  id="vendor_name"
                  value={formData.vendor_name}
                  onChange={(e) => setFormData({ ...formData, vendor_name: e.target.value })}
                  placeholder="Nama vendor (opsional)"
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
                {submitting ? 'Menyimpan...' : 'Simpan Pengeluaran'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Expense List */}
      <Card>
        <CardHeader>
          <CardTitle>Riwayat Pengeluaran</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-slate-500">Memuat data...</div>
          ) : expenses.length === 0 ? (
            <div className="text-center py-8 text-slate-500">Belum ada data pengeluaran</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-200">
                    <th className="text-left py-3 px-4 font-semibold text-slate-700">Tanggal</th>
                    <th className="text-left py-3 px-4 font-semibold text-slate-700">Kategori</th>
                    <th className="text-left py-3 px-4 font-semibold text-slate-700">Deskripsi</th>
                    <th className="text-left py-3 px-4 font-semibold text-slate-700">Vendor</th>
                    <th className="text-right py-3 px-4 font-semibold text-slate-700">Jumlah</th>
                    <th className="text-center py-3 px-4 font-semibold text-slate-700">Aksi</th>
                  </tr>
                </thead>
                <tbody>
                  {expenses.map((expense) => (
                    <tr key={expense.id} className="border-b border-slate-100 hover:bg-slate-50">
                      <td className="py-3 px-4 text-sm">
                        {new Date(expense.transaction_date).toLocaleDateString('id-ID')}
                      </td>
                      <td className="py-3 px-4">
                        <Badge variant="outline">
                          {EXPENSE_CATEGORIES.find(c => c.value === expense.category)?.label || expense.category}
                        </Badge>
                      </td>
                      <td className="py-3 px-4 text-sm">{expense.description}</td>
                      <td className="py-3 px-4 text-sm">{expense.vendor_name || '-'}</td>
                      <td className="py-3 px-4 text-right font-semibold text-red-600">
                        Rp {expense.amount.toLocaleString('id-ID')}
                      </td>
                      <td className="py-3 px-4 text-center">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDelete(expense.id)}
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
