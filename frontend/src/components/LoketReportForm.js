import React from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Textarea } from './ui/textarea';
import { Plus, Trash2 } from 'lucide-react';

export default function LoketReportForm({ 
  open, 
  onClose, 
  formData, 
  setFormData, 
  businesses, 
  onSubmit,
  isEditing 
}) {
  const addBankBalance = () => {
    setFormData({
      ...formData,
      bank_balances: [
        ...formData.bank_balances,
        { bank_name: '', saldo_awal: 0, saldo_inject: 0, data_lunas: 0, setor_kasir: 0, transfer_amount: 0, sisa_setoran: 0, saldo_akhir: 0, uang_lebih: 0 }
      ]
    });
  };

  const updateBankBalance = (index, field, value) => {
    const newBalances = [...formData.bank_balances];
    newBalances[index][field] = field === 'bank_name' ? value : parseFloat(value) || 0;
    
    // Auto calculate
    const bank = newBalances[index];
    bank.sisa_setoran = bank.data_lunas - bank.setor_kasir - bank.transfer_amount;
    bank.saldo_akhir = bank.saldo_awal + bank.saldo_inject - bank.data_lunas;
    
    setFormData({ ...formData, bank_balances: newBalances });
  };

  const removeBankBalance = (index) => {
    const newBalances = formData.bank_balances.filter((_, i) => i !== index);
    setFormData({ ...formData, bank_balances: newBalances });
  };

  const calculateTotal = () => {
    return formData.bank_balances.reduce((sum, bank) => sum + bank.sisa_setoran, 0);
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{isEditing ? 'Edit' : 'Input'} Laporan Harian Loket</DialogTitle>
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

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Nama Petugas *</Label>
              <Input
                value={formData.nama_petugas}
                onChange={(e) => setFormData({ ...formData, nama_petugas: e.target.value })}
                required
                placeholder="Nama petugas loket"
              />
            </div>
            
            <div>
              <Label>Shift *</Label>
              <Select value={formData.shift.toString()} onValueChange={(value) => setFormData({ ...formData, shift: parseInt(value) })}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">Shift 1</SelectItem>
                  <SelectItem value="2">Shift 2</SelectItem>
                  <SelectItem value="3">Shift 3</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <Label className="text-base font-semibold">Saldo Bank</Label>
              <Button type="button" size="sm" onClick={addBankBalance}>
                <Plus className="w-4 h-4 mr-1" />
                Tambah Bank
              </Button>
            </div>

            {formData.bank_balances.map((bank, index) => (
              <div key={index} className="p-4 border rounded-lg space-y-3 relative">
                {formData.bank_balances.length > 1 && (
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="absolute top-2 right-2"
                    onClick={() => removeBankBalance(index)}
                  >
                    <Trash2 className="w-4 h-4 text-red-600" />
                  </Button>
                )}
                
                <div>
                  <Label>Nama Bank *</Label>
                  <Input
                    value={bank.bank_name}
                    onChange={(e) => updateBankBalance(index, 'bank_name', e.target.value)}
                    placeholder="Contoh: BRIS, Mandiri, BCA"
                    required
                  />
                </div>

                <div className="grid grid-cols-4 gap-3">
                  <div>
                    <Label className="text-xs">Saldo Awal</Label>
                    <Input
                      type="number"
                      value={bank.saldo_awal}
                      onChange={(e) => updateBankBalance(index, 'saldo_awal', e.target.value)}
                    />
                  </div>
                  <div>
                    <Label className="text-xs">Saldo Inject</Label>
                    <Input
                      type="number"
                      value={bank.saldo_inject}
                      onChange={(e) => updateBankBalance(index, 'saldo_inject', e.target.value)}
                    />
                  </div>
                  <div>
                    <Label className="text-xs">Data Lunas</Label>
                    <Input
                      type="number"
                      value={bank.data_lunas}
                      onChange={(e) => updateBankBalance(index, 'data_lunas', e.target.value)}
                    />
                  </div>
                  <div>
                    <Label className="text-xs">Setor Kasir</Label>
                    <Input
                      type="number"
                      value={bank.setor_kasir}
                      onChange={(e) => updateBankBalance(index, 'setor_kasir', e.target.value)}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-4 gap-3">
                  <div>
                    <Label className="text-xs">Transfer</Label>
                    <Input
                      type="number"
                      value={bank.transfer_amount}
                      onChange={(e) => updateBankBalance(index, 'transfer_amount', e.target.value)}
                    />
                  </div>
                  <div>
                    <Label className="text-xs">Uang Lebih</Label>
                    <Input
                      type="number"
                      value={bank.uang_lebih}
                      onChange={(e) => updateBankBalance(index, 'uang_lebih', e.target.value)}
                    />
                  </div>
                  <div className="bg-blue-50 p-2 rounded">
                    <Label className="text-xs text-blue-900">Sisa Setoran</Label>
                    <div className="text-lg font-bold text-blue-900">
                      {bank.sisa_setoran.toLocaleString('id-ID')}
                    </div>
                  </div>
                  <div className="bg-slate-50 p-2 rounded">
                    <Label className="text-xs text-slate-900">Saldo Akhir</Label>
                    <div className="text-lg font-bold text-slate-900">
                      {bank.saldo_akhir.toLocaleString('id-ID')}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
            <div className="flex justify-between items-center">
              <span className="font-semibold text-blue-900">Total Setoran Shift {formData.shift}:</span>
              <span className="text-2xl font-bold text-blue-900">
                Rp {calculateTotal().toLocaleString('id-ID')}
              </span>
            </div>
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
