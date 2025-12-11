import React, { useState, useEffect } from 'react';
import { api } from '../utils/api';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Building2, Plus, Search, Edit, Eye } from 'lucide-react';
import { toast } from 'sonner';

const BUSINESS_CATEGORIES = [
  { value: 'PPOB', label: 'PPOB - Payment Point' },
  { value: 'PLN', label: 'PLN - Instalasi Listrik' },
  { value: 'Travel', label: 'Travel Umroh' },
  { value: 'PDAM', label: 'PDAM - Air Bersih' },
  { value: 'Inventory', label: 'Inventory & Pengadaan' },
  { value: 'Custom', label: 'Custom Business' }
];

export default function Businesses() {
  const [businesses, setBusinesses] = useState([]);
  const [filteredBusinesses, setFilteredBusinesses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [showDialog, setShowDialog] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    category: 'PPOB',
    description: '',
    address: '',
    phone: '',
    email: '',
  });

  useEffect(() => {
    fetchBusinesses();
  }, []);

  useEffect(() => {
    filterBusinesses();
  }, [businesses, searchTerm, selectedCategory]);

  const fetchBusinesses = async () => {
    try {
      const response = await api.get('/businesses');
      setBusinesses(response.data);
    } catch (error) {
      toast.error('Gagal memuat data bisnis');
    } finally {
      setLoading(false);
    }
  };

  const filterBusinesses = () => {
    let filtered = businesses;

    if (searchTerm) {
      filtered = filtered.filter(biz =>
        biz.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        biz.description?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (selectedCategory !== 'all') {
      filtered = filtered.filter(biz => biz.category === selectedCategory);
    }

    setFilteredBusinesses(filtered);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post('/businesses', formData);
      toast.success('Bisnis berhasil ditambahkan!');
      setShowDialog(false);
      resetForm();
      fetchBusinesses();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Gagal menambahkan bisnis');
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      category: 'PPOB',
      description: '',
      address: '',
      phone: '',
      email: '',
    });
  };

  const getCategoryBadgeColor = (category) => {
    const colors = {
      PPOB: 'bg-blue-100 text-blue-900',
      PLN: 'bg-green-100 text-green-900',
      Travel: 'bg-purple-100 text-purple-900',
      PDAM: 'bg-cyan-100 text-cyan-900',
      Inventory: 'bg-orange-100 text-orange-900',
      Custom: 'bg-gray-100 text-gray-900'
    };
    return colors[category] || 'bg-gray-100 text-gray-900';
  };

  if (loading) {
    return <div className="flex items-center justify-center h-96">Memuat data...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold text-slate-900 tracking-tight mb-2">Manajemen Bisnis</h1>
          <p className="text-slate-600">Kelola berbagai jenis bisnis Anda</p>
        </div>
        <Dialog open={showDialog} onOpenChange={setShowDialog}>
          <DialogTrigger asChild>
            <Button data-testid="add-business-button">
              <Plus className="w-4 h-4 mr-2" />
              Tambah Bisnis
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Tambah Bisnis Baru</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label>Nama Bisnis *</Label>
                <Input
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                  placeholder="Contoh: Loket PPOB Cabang 1"
                />
              </div>
              <div>
                <Label>Kategori Bisnis *</Label>
                <Select value={formData.category} onValueChange={(value) => setFormData({ ...formData, category: value })}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {BUSINESS_CATEGORIES.map(cat => (
                      <SelectItem key={cat.value} value={cat.value}>{cat.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>Deskripsi</Label>
                <Textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Deskripsi singkat tentang bisnis ini"
                  rows={3}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Telepon</Label>
                  <Input
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    placeholder="021xxxxxxx"
                  />
                </div>
                <div>
                  <Label>Email</Label>
                  <Input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    placeholder="bisnis@example.com"
                  />
                </div>
              </div>
              <div>
                <Label>Alamat</Label>
                <Textarea
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                  placeholder="Alamat lengkap bisnis"
                  rows={2}
                />
              </div>
              <div className="flex justify-end space-x-2">
                <Button type="button" variant="outline" onClick={() => setShowDialog(false)}>
                  Batal
                </Button>
                <Button type="submit">Simpan</Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Filters */}
      <Card className="p-4">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
              <Input
                placeholder="Cari bisnis..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
          <div>
            <Select value={selectedCategory} onValueChange={setSelectedCategory}>
              <SelectTrigger className="w-[200px]">
                <SelectValue placeholder="Semua Kategori" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Semua Kategori</SelectItem>
                {BUSINESS_CATEGORIES.map(cat => (
                  <SelectItem key={cat.value} value={cat.value}>{cat.value}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </Card>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="text-sm text-slate-500">Total Bisnis</div>
          <div className="text-3xl font-bold text-slate-900 mt-1">{businesses.length}</div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-slate-500">Bisnis Aktif</div>
          <div className="text-3xl font-bold text-green-600 mt-1">
            {businesses.filter(b => b.is_active).length}
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-slate-500">PPOB & PLN</div>
          <div className="text-3xl font-bold text-blue-600 mt-1">
            {businesses.filter(b => ['PPOB', 'PLN'].includes(b.category)).length}
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-slate-500">Travel & Lainnya</div>
          <div className="text-3xl font-bold text-purple-600 mt-1">
            {businesses.filter(b => ['Travel', 'PDAM', 'Inventory', 'Custom'].includes(b.category)).length}
          </div>
        </Card>
      </div>

      {/* Business List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredBusinesses.map((business) => (
          <Card key={business.id} className="p-6 hover:shadow-lg transition-shadow" data-testid={`business-card-${business.id}`}>
            <div className="flex items-start justify-between mb-4">
              <div className="w-12 h-12 rounded-xl bg-slate-100 flex items-center justify-center">
                <Building2 className="w-6 h-6 text-slate-900" />
              </div>
              <Badge className={getCategoryBadgeColor(business.category)}>
                {business.category}
              </Badge>
            </div>
            <h3 className="text-lg font-semibold text-slate-900 mb-2">{business.name}</h3>
            <p className="text-sm text-slate-600 mb-4 line-clamp-2">
              {business.description || 'Tidak ada deskripsi'}
            </p>
            <div className="space-y-2 mb-4">
              {business.phone && (
                <div className="text-sm text-slate-600">
                  📞 {business.phone}
                </div>
              )}
              {business.email && (
                <div className="text-sm text-slate-600">
                  ✉️ {business.email}
                </div>
              )}
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" className="flex-1">
                <Eye className="w-4 h-4 mr-2" />
                Detail
              </Button>
              <Button variant="outline" size="sm" className="flex-1">
                <Edit className="w-4 h-4 mr-2" />
                Edit
              </Button>
            </div>
          </Card>
        ))}
      </div>

      {filteredBusinesses.length === 0 && (
        <Card className="p-12 text-center">
          <Building2 className="w-16 h-16 text-slate-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-slate-900 mb-2">Tidak Ada Bisnis Ditemukan</h3>
          <p className="text-slate-600">Coba ubah filter atau tambahkan bisnis baru</p>
        </Card>
      )}
    </div>
  );
}
