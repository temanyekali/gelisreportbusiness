import React, { useState, useEffect } from 'react';
import { api } from '../utils/api';
import { getUser } from '../utils/auth';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { FileText, Download, Calendar, Building2, Plus, Edit, Trash2 } from 'lucide-react';
import { toast } from 'sonner';
import LoketReportForm from './LoketReportForm';
import KasirReportForm from './KasirReportForm';

export default function Reports() {
  const [businesses, setBusinesses] = useState([]);
  const [selectedBusiness, setSelectedBusiness] = useState('all');
  const [loketReports, setLoketReports] = useState([]);
  const [kasirReports, setKasirReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('loket');
  const [showLoketForm, setShowLoketForm] = useState(false);
  const [showKasirForm, setShowKasirForm] = useState(false);
  const [editingReport, setEditingReport] = useState(null);
  
  const currentUser = getUser();
  const canEditDelete = currentUser && (currentUser.role_id === 1 || currentUser.role_id === 2);

  const [loketFormData, setLoketFormData] = useState({
    business_id: '',
    report_date: new Date().toISOString().split('T')[0],
    nama_petugas: currentUser?.full_name || '',
    shift: 1,
    bank_balances: [
      { bank_name: 'BRIS', saldo_awal: 0, saldo_inject: 0, data_lunas: 0, setor_kasir: 0, transfer_amount: 0, sisa_setoran: 0, saldo_akhir: 0, uang_lebih: 0 }
    ],
    notes: ''
  });

  const [kasirFormData, setKasirFormData] = useState({
    business_id: '',
    report_date: new Date().toISOString().split('T')[0],
    setoran_pagi: 0,
    setoran_siang: 0,
    setoran_sore: 0,
    setoran_deposit_loket_luar: 0,
    setoran_pelunasan_pagi: 0,
    setoran_pelunasan_siang: 0,
    topup_transactions: [],
    penerimaan_kas_kecil: 0,
    pengurangan_kas_kecil: 0,
    belanja_loket: 0,
    penerimaan_admin: 0,
    notes: ''
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [businessesRes, loketRes, kasirRes] = await Promise.all([
        api.get('/businesses'),
        api.get('/reports/loket-daily'),
        api.get('/reports/kasir-daily')
      ]);
      setBusinesses(businessesRes.data);
      setLoketReports(loketRes.data);
      setKasirReports(kasirRes.data);
    } catch (error) {
      toast.error('Gagal memuat data laporan');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitLoket = async (e) => {
    e.preventDefault();
    try {
      const totalSetoran = loketFormData.bank_balances.reduce((sum, bank) => sum + bank.sisa_setoran, 0);
      const submitData = {
        ...loketFormData,
        total_setoran_shift: totalSetoran,
        report_date: new Date(loketFormData.report_date).toISOString()
      };
      
      if (editingReport) {
        await api.put(`/reports/loket-daily/${editingReport.id}`, submitData);
        toast.success('Laporan berhasil diupdate!');
      } else {
        await api.post('/reports/loket-daily', submitData);
        toast.success('✅ Laporan berhasil disimpan & otomatis di-sync ke Accounting!');
      }
      
      setShowLoketForm(false);
      setEditingReport(null);
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Gagal menyimpan laporan');
    }
  };

  const handleSubmitKasir = async (e) => {
    e.preventDefault();
    try {
      const totalTopup = kasirFormData.topup_transactions.reduce((sum, txn) => sum + txn.amount, 0);
      const totalKasKecil = kasirFormData.penerimaan_kas_kecil - kasirFormData.pengurangan_kas_kecil - kasirFormData.belanja_loket;
      
      const submitData = {
        ...kasirFormData,
        total_topup: totalTopup,
        total_kas_kecil: totalKasKecil,
        total_admin: kasirFormData.penerimaan_admin,
        saldo_brankas: kasirFormData.penerimaan_admin,
        report_date: new Date(kasirFormData.report_date).toISOString()
      };
      
      if (editingReport) {
        await api.put(`/reports/kasir-daily/${editingReport.id}`, submitData);
        toast.success('✅ Laporan berhasil diupdate!');
      } else {
        await api.post('/reports/kasir-daily', submitData);
        toast.success('✅ Laporan berhasil disimpan & otomatis di-sync ke Accounting!');
      }
      
      setShowKasirForm(false);
      setEditingReport(null);
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Gagal menyimpan laporan');
    }
  };

  const handleEditLoket = (report) => {
    setEditingReport(report);
    setLoketFormData({
      business_id: report.business_id,
      report_date: new Date(report.report_date).toISOString().split('T')[0],
      nama_petugas: report.nama_petugas,
      shift: report.shift,
      bank_balances: report.bank_balances,
      notes: report.notes || ''
    });
    setShowLoketForm(true);
  };

  const handleEditKasir = (report) => {
    setEditingReport(report);
    setKasirFormData({
      business_id: report.business_id,
      report_date: new Date(report.report_date).toISOString().split('T')[0],
      setoran_pagi: report.setoran_pagi,
      setoran_siang: report.setoran_siang,
      setoran_sore: report.setoran_sore,
      setoran_deposit_loket_luar: report.setoran_deposit_loket_luar,
      setoran_pelunasan_pagi: report.setoran_pelunasan_pagi,
      setoran_pelunasan_siang: report.setoran_pelunasan_siang,
      topup_transactions: report.topup_transactions,
      penerimaan_kas_kecil: report.penerimaan_kas_kecil,
      pengurangan_kas_kecil: report.pengurangan_kas_kecil,
      belanja_loket: report.belanja_loket,
      penerimaan_admin: report.penerimaan_admin,
      notes: report.notes || ''
    });
    setShowKasirForm(true);
  };

  const handleDeleteLoket = async (reportId) => {
    if (!window.confirm('Apakah Anda yakin ingin menghapus laporan ini?')) return;
    
    try {
      await api.delete(`/reports/loket-daily/${reportId}`);
      toast.success('Laporan berhasil dihapus!');
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Gagal menghapus laporan');
    }
  };

  const handleDeleteKasir = async (reportId) => {
    if (!window.confirm('Apakah Anda yakin ingin menghapus laporan ini?')) return;
    
    try {
      await api.delete(`/reports/kasir-daily/${reportId}`);
      toast.success('Laporan berhasil dihapus!');
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Gagal menghapus laporan');
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('id-ID', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getFilteredLoketReports = () => {
    if (selectedBusiness === 'all') return loketReports;
    return loketReports.filter(r => r.business_id === selectedBusiness);
  };

  const getFilteredKasirReports = () => {
    if (selectedBusiness === 'all') return kasirReports;
    return kasirReports.filter(r => r.business_id === selectedBusiness);
  };

  if (loading) {
    return <div className="flex items-center justify-center h-96">Memuat data...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold text-slate-900 tracking-tight mb-2">Laporan</h1>
          <p className="text-slate-600">Laporan harian operasional dan keuangan</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={() => setShowLoketForm(true)} data-testid="add-loket-report">
            <Plus className="w-4 h-4 mr-2" />
            Laporan Loket
          </Button>
          <Button onClick={() => setShowKasirForm(true)} data-testid="add-kasir-report">
            <Plus className="w-4 h-4 mr-2" />
            Laporan Kasir
          </Button>
        </div>
      </div>

      {/* Filter */}
      <Card className="p-4">
        <div className="flex items-center gap-4">
          <div className="flex-1">
            <Select value={selectedBusiness} onValueChange={setSelectedBusiness}>
              <SelectTrigger>
                <SelectValue placeholder="Filter Bisnis" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Semua Bisnis</SelectItem>
                {businesses.map(biz => (
                  <SelectItem key={biz.id} value={biz.id}>{biz.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <Button variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Export Excel
          </Button>
          <Button variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Export PDF
          </Button>
        </div>
      </Card>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="text-sm text-slate-500">Total Laporan Loket</div>
          <div className="text-3xl font-bold text-slate-900 mt-1">{getFilteredLoketReports().length}</div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-slate-500">Total Laporan Kasir</div>
          <div className="text-3xl font-bold text-slate-900 mt-1">{getFilteredKasirReports().length}</div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-slate-500">Periode</div>
          <div className="text-2xl font-bold text-slate-900 mt-1">30 Hari</div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-slate-500">Status</div>
          <div className="text-2xl font-bold text-green-600 mt-1">Real-time</div>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="loket">Laporan Harian Loket</TabsTrigger>
          <TabsTrigger value="kasir">Laporan Harian Kasir</TabsTrigger>
        </TabsList>

        {/* Loket Reports */}
        <TabsContent value="loket" className="space-y-4 mt-6">
          {getFilteredLoketReports().slice(0, 10).map((report) => {
            const business = businesses.find(b => b.id === report.business_id);
            
            return (
              <Card key={report.id} className="p-6 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-slate-900">
                      Laporan Harian Loket - Shift {report.shift}
                    </h3>
                    <div className="flex items-center gap-3 mt-2">
                      <Badge variant="outline">{business?.name || 'N/A'}</Badge>
                      <span className="text-sm text-slate-600">
                        <Calendar className="w-4 h-4 inline mr-1" />
                        {formatDate(report.report_date)}
                      </span>
                      <span className="text-sm text-slate-600">
                        Petugas: {report.nama_petugas}
                      </span>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    {canEditDelete && (
                      <>
                        <Button size="sm" variant="outline" onClick={() => handleEditLoket(report)}>
                          <Edit className="w-4 h-4 text-blue-600" />
                        </Button>
                        {currentUser.role_id === 1 && (
                          <Button size="sm" variant="outline" onClick={() => handleDeleteLoket(report.id)}>
                            <Trash2 className="w-4 h-4 text-red-600" />
                          </Button>
                        )}
                      </>
                    )}
                    <Button size="sm" variant="outline">
                      <FileText className="w-4 h-4 mr-2" />
                      Cetak
                    </Button>
                  </div>
                </div>

                {/* Bank Balances */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  {report.bank_balances.map((bank, idx) => (
                    <div key={idx} className="p-4 bg-slate-50 rounded-lg">
                      <h4 className="font-semibold text-slate-900 mb-3 flex items-center">
                        <Building2 className="w-4 h-4 mr-2" />
                        {bank.bank_name}
                      </h4>
                      <div className="space-y-1 text-sm">
                        <div className="flex justify-between">
                          <span className="text-slate-600">Saldo Awal:</span>
                          <span className="font-medium">{formatCurrency(bank.saldo_awal)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-600">Saldo Inject:</span>
                          <span className="font-medium">{formatCurrency(bank.saldo_inject)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-600">Data Lunas:</span>
                          <span className="font-medium text-green-600">{formatCurrency(bank.data_lunas)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-600">Setor Kasir:</span>
                          <span className="font-medium">{formatCurrency(bank.setor_kasir)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-600">Transfer:</span>
                          <span className="font-medium">{formatCurrency(bank.transfer_amount)}</span>
                        </div>
                        <div className="flex justify-between border-t pt-1 mt-1">
                          <span className="text-slate-600">Sisa Setoran:</span>
                          <span className="font-semibold text-blue-600">{formatCurrency(bank.sisa_setoran)}</span>
                        </div>
                        <div className="flex justify-between border-t pt-1">
                          <span className="text-slate-700 font-medium">Saldo Akhir:</span>
                          <span className="font-bold text-slate-900">{formatCurrency(bank.saldo_akhir)}</span>
                        </div>
                        {bank.uang_lebih > 0 && (
                          <div className="flex justify-between text-orange-600">
                            <span>Uang Lebih:</span>
                            <span className="font-medium">{formatCurrency(bank.uang_lebih)}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>

                {/* Total Setoran */}
                <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <span className="text-sm font-medium text-blue-900">Total Setoran Shift {report.shift}:</span>
                  <span className="text-2xl font-bold text-blue-900">
                    {formatCurrency(report.total_setoran_shift)}
                  </span>
                </div>
              </Card>
            );
          })}

          {getFilteredLoketReports().length === 0 && (
            <Card className="p-12 text-center">
              <FileText className="w-16 h-16 text-slate-300 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-slate-900 mb-2">Tidak Ada Laporan</h3>
              <p className="text-slate-600">Belum ada laporan loket untuk periode ini</p>
            </Card>
          )}
        </TabsContent>

        {/* Kasir Reports - Similar structure */}
        <TabsContent value="kasir" className="space-y-4 mt-6">
          {getFilteredKasirReports().slice(0, 10).map((report) => {
            const business = businesses.find(b => b.id === report.business_id);
            
            return (
              <Card key={report.id} className="p-6 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-slate-900">Laporan Harian Kasir</h3>
                    <div className="flex items-center gap-3 mt-2">
                      <Badge variant="outline">{business?.name || 'N/A'}</Badge>
                      <span className="text-sm text-slate-600">
                        <Calendar className="w-4 h-4 inline mr-1" />
                        {formatDate(report.report_date)}
                      </span>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    {canEditDelete && (
                      <>
                        <Button size="sm" variant="outline" onClick={() => handleEditKasir(report)}>
                          <Edit className="w-4 h-4 text-blue-600" />
                        </Button>
                        {currentUser.role_id === 1 && (
                          <Button size="sm" variant="outline" onClick={() => handleDeleteKasir(report.id)}>
                            <Trash2 className="w-4 h-4 text-red-600" />
                          </Button>
                        )}
                      </>
                    )}
                    <Button size="sm" variant="outline">
                      <FileText className="w-4 h-4 mr-2" />
                      Cetak
                    </Button>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Setoran */}
                  <div className="space-y-3">
                    <h4 className="font-semibold text-slate-900 mb-3">Setoran</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-slate-600">Setoran Pagi:</span>
                        <span className="font-medium">{formatCurrency(report.setoran_pagi)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-600">Setoran Siang:</span>
                        <span className="font-medium">{formatCurrency(report.setoran_siang)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-600">Setoran Sore:</span>
                        <span className="font-medium">{formatCurrency(report.setoran_sore)}</span>
                      </div>
                      <div className="flex justify-between border-t pt-2">
                        <span className="text-slate-600">Deposit Loket Luar:</span>
                        <span className="font-medium">{formatCurrency(report.setoran_deposit_loket_luar)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-600">Pelunasan Pagi:</span>
                        <span className="font-medium">{formatCurrency(report.setoran_pelunasan_pagi)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-600">Pelunasan Siang:</span>
                        <span className="font-medium">{formatCurrency(report.setoran_pelunasan_siang)}</span>
                      </div>
                    </div>
                  </div>

                  {/* Topup & Kas Kecil */}
                  <div className="space-y-3">
                    <h4 className="font-semibold text-slate-900 mb-3">Transfer & Kas</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-slate-600">Total Topup ({report.topup_transactions.length}x):</span>
                        <span className="font-semibold text-blue-600">{formatCurrency(report.total_topup)}</span>
                      </div>
                      <div className="flex justify-between border-t pt-2">
                        <span className="text-slate-600">Penerimaan Kas Kecil:</span>
                        <span className="font-medium">{formatCurrency(report.penerimaan_kas_kecil)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-600">Pengurangan Kas Kecil:</span>
                        <span className="font-medium text-red-600">-{formatCurrency(report.pengurangan_kas_kecil)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-600">Belanja Loket:</span>
                        <span className="font-medium text-red-600">-{formatCurrency(report.belanja_loket)}</span>
                      </div>
                      <div className="flex justify-between border-t pt-2">
                        <span className="text-slate-700 font-medium">Total Kas Kecil:</span>
                        <span className="font-semibold">{formatCurrency(report.total_kas_kecil)}</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Summary */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6 pt-4 border-t">
                  <div className="p-3 bg-green-50 rounded-lg">
                    <div className="text-sm text-green-700">Penerimaan Admin</div>
                    <div className="text-xl font-bold text-green-900">{formatCurrency(report.penerimaan_admin)}</div>
                  </div>
                  <div className="p-3 bg-blue-50 rounded-lg">
                    <div className="text-sm text-blue-700">Total Admin</div>
                    <div className="text-xl font-bold text-blue-900">{formatCurrency(report.total_admin)}</div>
                  </div>
                  <div className="p-3 bg-purple-50 rounded-lg">
                    <div className="text-sm text-purple-700">Saldo Brankas</div>
                    <div className="text-xl font-bold text-purple-900">{formatCurrency(report.saldo_brankas)}</div>
                  </div>
                </div>
              </Card>
            );
          })}

          {getFilteredKasirReports().length === 0 && (
            <Card className="p-12 text-center">
              <FileText className="w-16 h-16 text-slate-300 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-slate-900 mb-2">Tidak Ada Laporan</h3>
              <p className="text-slate-600">Belum ada laporan kasir untuk periode ini</p>
            </Card>
          )}
        </TabsContent>
      </Tabs>

      {/* Forms */}
      <LoketReportForm
        open={showLoketForm}
        onClose={() => {
          setShowLoketForm(false);
          setEditingReport(null);
        }}
        formData={loketFormData}
        setFormData={setLoketFormData}
        businesses={businesses}
        onSubmit={handleSubmitLoket}
        isEditing={!!editingReport}
      />

      <KasirReportForm
        open={showKasirForm}
        onClose={() => {
          setShowKasirForm(false);
          setEditingReport(null);
        }}
        formData={kasirFormData}
        setFormData={setKasirFormData}
        businesses={businesses}
        onSubmit={handleSubmitKasir}
        isEditing={!!editingReport}
      />
    </div>
  );
}
