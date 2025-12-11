import React from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Textarea } from './ui/textarea';
import { Plus, Trash2 } from 'lucide-react';

export default function KasirReportForm({ 
  open, 
  onClose, 
  formData, 
  setFormData, 
  businesses, 
  onSubmit,
  isEditing 
}) {
  const addTopupTransaction = () => {
    setFormData({
      ...formData,
      topup_transactions: [...formData.topup_transactions, { amount: 0, description: '' }]
    });
  };

  const updateTopupTransaction = (index, field, value) => {
    const newTopups = [...formData.topup_transactions];
    newTopups[index][field] = field === 'amount' ? parseFloat(value) || 0 : value;
    setFormData({ ...formData, topup_transactions: newTopups });
  };

  const removeTopupTransaction = (index) => {
    const newTopups = formData.topup_transactions.filter((_, i) => i !== index);
    setFormData({ ...formData, topup_transactions: newTopups });
  };

  const calculateTotalTopup = () => {
    return formData.topup_transactions.reduce((sum, txn) => sum + txn.amount, 0);
  };

  const calculateTotalKasKecil = () => {
    return formData.penerimaan_kas_kecil - formData.pengurangan_kas_kecil - formData.belanja_loket;
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{isEditing ? 'Edit' : 'Input'} Laporan Harian Kasir</DialogTitle>
        </DialogHeader>
        
        <form onSubmit={onSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Bisnis *</Label>
              <Select value={formData.business_id} onValueChange={(value) => setFormData({ ...formData, business_id: value })}>
                <SelectTrigger>
                  <SelectValue placeholder="Pilih bisnis" />
                </SelectTrigger>
                <SelectContent>
                  {businesses.map(biz => (
                    <SelectItem key={biz.id} value={biz.id}>{biz.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label>Tanggal *</Label>
              <Input
                type="date"
                value={formData.report_date}
                onChange={(e) => setFormData({ ...formData, report_date: e.target.value })}
                required
              />
            </div>
          </div>

          <div className="space-y-3">
            <Label className="text-base font-semibold">Setoran</Label>
            <div className="grid grid-cols-3 gap-3">
              <div>
                <Label className="text-xs">Setoran Pagi</Label>
                <Input
                  type="number"
                  value={formData.setoran_pagi}
                  onChange={(e) => setFormData({ ...formData, setoran_pagi: parseFloat(e.target.value) || 0 })}
                />
              </div>
              <div>
                <Label className="text-xs">Setoran Siang</Label>
                <Input
                  type="number"
                  value={formData.setoran_siang}
                  onChange={(e) => setFormData({ ...formData, setoran_siang: parseFloat(e.target.value) || 0 })}
                />
              </div>
              <div>
                <Label className="text-xs">Setoran Sore</Label>
                <Input
                  type="number"
                  value={formData.setoran_sore}
                  onChange={(e) => setFormData({ ...formData, setoran_sore: parseFloat(e.target.value) || 0 })}
                />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-3">
              <div>
                <Label className="text-xs">Deposit Loket Luar</Label>
                <Input
                  type="number"
                  value={formData.setoran_deposit_loket_luar}
                  onChange={(e) => setFormData({ ...formData, setoran_deposit_loket_luar: parseFloat(e.target.value) || 0 })}
                />
              </div>
              <div>
                <Label className="text-xs">Pelunasan Pagi</Label>
                <Input
                  type="number"
                  value={formData.setoran_pelunasan_pagi}
                  onChange={(e) => setFormData({ ...formData, setoran_pelunasan_pagi: parseFloat(e.target.value) || 0 })}
                />
              </div>
              <div>
                <Label className="text-xs">Pelunasan Siang</Label>
                <Input
                  type="number"
                  value={formData.setoran_pelunasan_siang}
                  onChange={(e) => setFormData({ ...formData, setoran_pelunasan_siang: parseFloat(e.target.value) || 0 })}
                />
              </div>
            </div>
          </div>

          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label className="text-base font-semibold">Transfer Topup Loket Mandiri</Label>
              <Button type="button" size="sm" onClick={addTopupTransaction}>
                <Plus className="w-4 h-4 mr-1" />
                Tambah Topup
              </Button>
            </div>

            {formData.topup_transactions.map((topup, index) => (
              <div key={index} className="flex gap-2 items-end">
                <div className="flex-1">
                  <Label className="text-xs">Nominal Topup #{index + 1}</Label>
                  <Input
                    type="number"
                    value={topup.amount}
                    onChange={(e) => updateTopupTransaction(index, 'amount', e.target.value)}
                    placeholder="Nominal"
                  />
                </div>
                <div className="flex-1">
                  <Label className="text-xs">Keterangan</Label>
                  <Input
                    value={topup.description}
                    onChange={(e) => updateTopupTransaction(index, 'description', e.target.value)}
                    placeholder="Keterangan (optional)"
                  />
                </div>
                {formData.topup_transactions.length > 0 && (
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    onClick={() => removeTopupTransaction(index)}
                  >
                    <Trash2 className="w-4 h-4 text-red-600" />
                  </Button>
                )}
              </div>
            ))}

            <div className="p-3 bg-blue-50 rounded-lg">
              <div className="flex justify-between">
                <span className="font-medium text-blue-900">Total Topup ({formData.topup_transactions.length}x):</span>
                <span className="text-lg font-bold text-blue-900">
                  Rp {calculateTotalTopup().toLocaleString('id-ID')}
                </span>
              </div>
            </div>
          </div>

          <div className="space-y-3">
            <Label className="text-base font-semibold">Kas Kecil</Label>
            <div className="grid grid-cols-3 gap-3">
              <div>
                <Label className="text-xs">Penerimaan Kas Kecil</Label>
                <Input
                  type="number"
                  value={formData.penerimaan_kas_kecil}
                  onChange={(e) => setFormData({ ...formData, penerimaan_kas_kecil: parseFloat(e.target.value) || 0 })}
                />
              </div>
              <div>
                <Label className="text-xs">Pengurangan (Parkir, dll)</Label>
                <Input
                  type="number"
                  value={formData.pengurangan_kas_kecil}
                  onChange={(e) => setFormData({ ...formData, pengurangan_kas_kecil: parseFloat(e.target.value) || 0 })}
                />
              </div>
              <div>
                <Label className="text-xs">Belanja Loket</Label>
                <Input
                  type="number"
                  value={formData.belanja_loket}
                  onChange={(e) => setFormData({ ...formData, belanja_loket: parseFloat(e.target.value) || 0 })}
                />
              </div>
            </div>

            <div className="p-3 bg-slate-50 rounded-lg">
              <div className="flex justify-between">
                <span className="font-medium text-slate-900">Total Kas Kecil:</span>
                <span className="text-lg font-bold text-slate-900">
                  Rp {calculateTotalKasKecil().toLocaleString('id-ID')}
                </span>
              </div>
            </div>
          </div>

          <div>
            <Label>Penerimaan Admin</Label>
            <Input
              type="number"
              value={formData.penerimaan_admin}
              onChange={(e) => setFormData({ ...formData, penerimaan_admin: parseFloat(e.target.value) || 0 })}
            />
          </div>

          <div>
            <Label>Catatan</Label>
            <Textarea
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              placeholder="Catatan tambahan (optional)"
              rows={2}
            />
          </div>

          <div className="flex justify-end space-x-2 pt-4">
            <Button type="button" variant="outline" onClick={onClose}>
              Batal
            </Button>
            <Button type="submit">
              {isEditing ? 'Update' : 'Simpan'} Laporan
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
