import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Plus, Save, Trash2, FileText, RefreshCw } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const HARI_OPTIONS = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu'];
const BANK_OPTIONS = ['BRIS', 'MANDIRI', 'BCA', 'BNI', 'BRI', 'Lainnya'];

export default function LoketPelunasanReport() {
  const [loading, setLoading] = useState(false);
  const [businesses, setBusinesses] = useState([]);
  const [reports, setReports] = useState([]);
  const [showForm, setShowForm] = useState(false);
  
  const [formData, setFormData] = useState({
    business_id: '',
    nama_petugas: '',
    hari: '',
    tanggal: new Date().toISOString().split('T')[0],
    shift: 1,
    bank_accounts: [],
    catatan: ''
  });

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
      setBusinesses(response.data.businesses || []);
      if (response.data.businesses.length > 0) {
        setFormData(prev => ({ ...prev, business_id: response.data.businesses[0].id }));
      }
    } catch (error) {
      console.error('Error fetching businesses:', error);
    }
  };

  const fetchReports = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${BACKEND_URL}/api/reports/loket-pelunasan`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setReports(response.data.reports || []);
    } catch (error) {
      toast.error('Gagal memuat laporan');
    } finally {
      setLoading(false);
    }
  };

  const addBankAccount = () => {
    setFormData({
      ...formData,
      bank_accounts: [
        ...formData.bank_accounts,
        {
          bank_name: BANK_OPTIONS[0],
          saldo_awal: 0,
          saldo_inject: 0,
          data_lunas: 0,
          setor_kasir: 0,
          transfer: 0,
          sisa_setoran: 0,
          saldo_akhir: 0,
          uang_lebih: 0
        }
      ]
    });
  };

  const removeBankAccount = (index) => {
    const newBanks = formData.bank_accounts.filter((_, i) => i !== index);
    setFormData({ ...formData, bank_accounts: newBanks });
  };

  const updateBankAccount = (index, field, value) => {
    const newBanks = [...formData.bank_accounts];
    const numValue = parseFloat(value) || 0;
    newBanks[index][field] = numValue;
    
    // Auto-calculate sisa setoran and saldo akhir
    const bank = newBanks[index];
    bank.sisa_setoran = bank.data_lunas - bank.setor_kasir - bank.transfer;
    bank.saldo_akhir = bank.saldo_awal + bank.saldo_inject - bank.data_lunas;
    
    setFormData({ ...formData, bank_accounts: newBanks });
  };

  const calculateTotalSetoran = () => {
    return formData.bank_accounts.reduce((sum, bank) => sum + (bank.sisa_setoran || 0), 0);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.business_id || !formData.nama_petugas || formData.bank_accounts.length === 0) {
      toast.error('Harap isi semua field yang diperlukan dan tambahkan minimal 1 bank');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${BACKEND_URL}/api/reports/loket-pelunasan`, formData, {
        headers: { Authorization: `Bearer ${token}` }
      });

      toast.success(`Laporan berhasil disimpan! Total Setoran: Rp ${response.data.total_setoran.toLocaleString('id-ID')}`);
      setShowForm(false);
      fetchReports();
      
      // Reset form
      setFormData({
        business_id: businesses[0]?.id || '',
        nama_petugas: '',
        hari: '',
        tanggal: new Date().toISOString().split('T')[0],
        shift: 1,
        bank_accounts: [],
        catatan: ''
      });
    } catch (error) {
      toast.error('Gagal menyimpan laporan: ' + (error.response?.data?.detail || error.message));
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0
    }).format(value);
  };

  return (
    <div className="space-y-6 p-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold">📊 Laporan Harian Loket (Pelunasan)</h1>
          <p className="text-gray-500 mt-1">Laporan akumulasi pelunasan per shift dengan multiple bank accounts</p>
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

      {showForm && (
        <Card>
          <CardHeader>
            <CardTitle>📝 Form Laporan Harian Loket</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
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
                    value={formData.nama_petugas}
                    onChange={(e) => setFormData({ ...formData, nama_petugas: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2"
                    placeholder="Nama petugas loket"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Hari</label>
                  <select
                    value={formData.hari}
                    onChange={(e) => setFormData({ ...formData, hari: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2"
                    required
                  >
                    <option value="">Pilih Hari</option>
                    {HARI_OPTIONS.map(hari => (
                      <option key={hari} value={hari}>{hari}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Tanggal</label>
                  <input
                    type="date"
                    value={formData.tanggal}
                    onChange={(e) => setFormData({ ...formData, tanggal: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Shift Ke</label>
                  <select
                    value={formData.shift}
                    onChange={(e) => setFormData({ ...formData, shift: parseInt(e.target.value) })}
                    className="w-full border rounded-lg px-3 py-2"
                    required
                  >
                    <option value={1}>Shift 1</option>
                    <option value={2}>Shift 2</option>
                    <option value={3}>Shift 3</option>
                  </select>
                </div>
              </div>

              <div className="border-t pt-4">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-semibold">Pelunasan Bank Accounts</h3>
                  <Button type="button" onClick={addBankAccount} size="sm" className="bg-green-600 hover:bg-green-700">
                    <Plus className="w-4 h-4 mr-2" />
                    Tambah Bank
                  </Button>
                </div>

                {formData.bank_accounts.map((bank, index) => (
                  <Card key={index} className="mb-4 bg-gray-50">
                    <CardContent className="pt-6">
                      <div className="flex justify-between items-start mb-4">
                        <h4 className="font-semibold text-lg">Bank {index + 1}</h4>
                        <Button
                          type="button"
                          onClick={() => removeBankAccount(index)}
                          size="sm"
                          variant="destructive"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>

                      <div className="grid md:grid-cols-3 gap-4">
                        <div>
                          <label className="block text-sm font-medium mb-2">Nama Bank</label>
                          <select
                            value={bank.bank_name}
                            onChange={(e) => {
                              const newBanks = [...formData.bank_accounts];
                              newBanks[index].bank_name = e.target.value;
                              setFormData({ ...formData, bank_accounts: newBanks });
                            }}
                            className="w-full border rounded-lg px-3 py-2"
                          >
                            {BANK_OPTIONS.map(bankName => (
                              <option key={bankName} value={bankName}>{bankName}</option>
                            ))}
                          </select>
                        </div>

                        <div>
                          <label className="block text-sm font-medium mb-2">Saldo Awal</label>
                          <input
                            type="number"
                            value={bank.saldo_awal}
                            onChange={(e) => updateBankAccount(index, 'saldo_awal', e.target.value)}
                            className="w-full border rounded-lg px-3 py-2"
                            step="0.01"
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium mb-2">Saldo Inject</label>
                          <input
                            type="number"
                            value={bank.saldo_inject}
                            onChange={(e) => updateBankAccount(index, 'saldo_inject', e.target.value)}
                            className="w-full border rounded-lg px-3 py-2"
                            step="0.01"
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium mb-2">Data Lunas</label>
                          <input
                            type="number"
                            value={bank.data_lunas}
                            onChange={(e) => updateBankAccount(index, 'data_lunas', e.target.value)}
                            className="w-full border rounded-lg px-3 py-2"
                            step="0.01"
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium mb-2">Setor Kasir</label>
                          <input
                            type="number"
                            value={bank.setor_kasir}
                            onChange={(e) => updateBankAccount(index, 'setor_kasir', e.target.value)}
                            className="w-full border rounded-lg px-3 py-2"
                            step="0.01"
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium mb-2">Transfer</label>
                          <input
                            type="number"
                            value={bank.transfer}
                            onChange={(e) => updateBankAccount(index, 'transfer', e.target.value)}
                            className="w-full border rounded-lg px-3 py-2"
                            step="0.01"
                          />
                        </div>

                        <div className="bg-blue-50 p-3 rounded-lg">
                          <label className="block text-sm font-medium mb-1">Sisa Setoran (Auto)</label>
                          <div className="text-lg font-bold text-blue-600">
                            {formatCurrency(bank.sisa_setoran)}
                          </div>
                        </div>

                        <div className="bg-green-50 p-3 rounded-lg">
                          <label className="block text-sm font-medium mb-1">Saldo Akhir (Auto)</label>
                          <div className="text-lg font-bold text-green-600">
                            {formatCurrency(bank.saldo_akhir)}
                          </div>
                        </div>

                        <div>
                          <label className="block text-sm font-medium mb-2">Uang Lebih</label>
                          <input
                            type="number"
                            value={bank.uang_lebih}
                            onChange={(e) => {
                              const newBanks = [...formData.bank_accounts];
                              newBanks[index].uang_lebih = parseFloat(e.target.value) || 0;
                              setFormData({ ...formData, bank_accounts: newBanks });
                            }}
                            className="w-full border rounded-lg px-3 py-2"
                            step="0.01"
                          />
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}

                {formData.bank_accounts.length > 0 && (
                  <Card className="bg-yellow-50 border-yellow-200">
                    <CardContent className="pt-6">
                      <div className="flex justify-between items-center">
                        <span className="text-lg font-semibold">Total Setoran Shift {formData.shift}</span>
                        <span className="text-2xl font-bold text-yellow-600">
                          {formatCurrency(calculateTotalSetoran())}
                        </span>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Catatan</label>
                <textarea
                  value={formData.catatan}
                  onChange={(e) => setFormData({ ...formData, catatan: e.target.value })}
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
                  <Save className="w-4 h-4 mr-2" />
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
              <p className="text-gray-500 text-lg">Belum ada laporan loket pelunasan</p>
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
                      {report.hari}, {new Date(report.tanggal).toLocaleDateString('id-ID')} - Shift {report.shift}
                    </CardTitle>
                    <p className="text-sm text-gray-500 mt-1">
                      Petugas: {report.nama_petugas} • {report.bank_accounts?.length || 0} Bank Accounts
                    </p>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-gray-500">Total Setoran</div>
                    <div className="text-xl font-bold text-green-600">
                      {formatCurrency(report.total_setoran)}
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {report.bank_accounts && report.bank_accounts.map((bank, bidx) => (
                  <div key={bidx} className="mb-4 p-4 bg-gray-50 rounded-lg">
                    <h4 className="font-semibold text-lg mb-3">{bank.bank_name}</h4>
                    <div className="grid md:grid-cols-2 gap-3 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Saldo Awal:</span>
                        <span className="font-medium">{formatCurrency(bank.saldo_awal)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Saldo Inject:</span>
                        <span className="font-medium">{formatCurrency(bank.saldo_inject)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Data Lunas:</span>
                        <span className="font-medium">{formatCurrency(bank.data_lunas)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Setor Kasir:</span>
                        <span className="font-medium">{formatCurrency(bank.setor_kasir)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Transfer:</span>
                        <span className="font-medium">{formatCurrency(bank.transfer)}</span>
                      </div>
                      <div className="flex justify-between bg-blue-100 p-2 rounded">
                        <span className="font-semibold">Sisa Setoran:</span>
                        <span className="font-bold text-blue-600">{formatCurrency(bank.sisa_setoran)}</span>
                      </div>
                      <div className="flex justify-between bg-green-100 p-2 rounded">
                        <span className="font-semibold">Saldo Akhir:</span>
                        <span className="font-bold text-green-600">{formatCurrency(bank.saldo_akhir)}</span>
                      </div>
                      {bank.uang_lebih > 0 && (
                        <div className="flex justify-between">
                          <span className="text-gray-600">Uang Lebih:</span>
                          <span className="font-medium">{formatCurrency(bank.uang_lebih)}</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
