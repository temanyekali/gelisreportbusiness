import React, { useState, useEffect } from 'react';
import { api } from '../utils/api';
import { getUser } from '../utils/auth';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Users as UsersIcon, Plus, Edit, Trash2, Search, UserCheck, UserX } from 'lucide-react';
import { toast } from 'sonner';

const ROLES = [
  { id: 1, name: 'Owner', description: 'Full access ke semua fitur', color: 'bg-purple-100 text-purple-900' },
  { id: 2, name: 'Manager', description: 'Monitor & manage operasional', color: 'bg-blue-100 text-blue-900' },
  { id: 3, name: 'Finance', description: 'Kelola keuangan & payroll', color: 'bg-green-100 text-green-900' },
  { id: 4, name: 'Customer Service', description: 'Input & manage orders', color: 'bg-cyan-100 text-cyan-900' },
  { id: 5, name: 'Kasir', description: 'Process pembayaran', color: 'bg-yellow-100 text-yellow-900' },
  { id: 6, name: 'Loket', description: 'Layanan PPOB & counter', color: 'bg-orange-100 text-orange-900' },
  { id: 7, name: 'Teknisi', description: 'Handle work orders', color: 'bg-slate-100 text-slate-900' },
];

export default function Users() {
  const [users, setUsers] = useState([]);
  const [filteredUsers, setFilteredUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('all');
  const [showForm, setShowForm] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  
  const currentUser = getUser();
  const isOwner = currentUser && currentUser.role_id === 1;

  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    full_name: '',
    phone: '',
    address: '',
    role_id: 4,
  });

  useEffect(() => {
    if (isOwner) {
      fetchUsers();
    }
  }, [isOwner]);

  useEffect(() => {
    filterUsers();
  }, [users, searchTerm, roleFilter]);

  const fetchUsers = async () => {
    try {
      const response = await api.get('/users');
      setUsers(response.data);
    } catch (error) {
      toast.error('Gagal memuat data pengguna');
    } finally {
      setLoading(false);
    }
  };

  const filterUsers = () => {
    let filtered = users;

    if (searchTerm) {
      filtered = filtered.filter(user =>
        user.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.email.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (roleFilter !== 'all') {
      filtered = filtered.filter(user => user.role_id === parseInt(roleFilter));
    }

    setFilteredUsers(filtered);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingUser) {
        // Update user - need update endpoint
        toast.info('Fitur edit sedang dalam pengembangan');
      } else {
        await api.post('/auth/register', formData);
        toast.success('Pengguna berhasil ditambahkan!');
      }
      setShowForm(false);
      setEditingUser(null);
      resetForm();
      fetchUsers();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Gagal menyimpan pengguna');
    }
  };

  const handleToggleActive = async (userId) => {
    try {
      await api.put(`/users/${userId}/toggle-active`);
      toast.success('Status pengguna berhasil diubah!');
      fetchUsers();
    } catch (error) {
      toast.error('Gagal mengubah status pengguna');
    }
  };

  const resetForm = () => {
    setFormData({
      username: '',
      email: '',
      password: '',
      full_name: '',
      phone: '',
      address: '',
      role_id: 4,
    });
  };

  const getRoleInfo = (roleId) => {
    return ROLES.find(r => r.id === roleId) || ROLES[3];
  };

  if (!isOwner) {
    return (
      <Card className="p-12 text-center">
        <UsersIcon className="w-16 h-16 text-slate-300 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-slate-900 mb-2">Akses Terbatas</h3>
        <p className="text-slate-600">Hanya Owner yang dapat mengakses manajemen pengguna</p>
      </Card>
    );
  }

  if (loading) {
    return <div className="flex items-center justify-center h-96">Memuat data...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold text-slate-900 tracking-tight mb-2">Manajemen Pengguna</h1>
          <p className="text-slate-600">Kelola user, role, dan otorisasi akses</p>
        </div>
        <Button onClick={() => setShowForm(true)} data-testid="add-user-button">
          <Plus className="w-4 h-4 mr-2" />
          Tambah Pengguna
        </Button>
      </div>

      {/* Filter */}
      <Card className="p-4">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
              <Input
                placeholder="Cari pengguna..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
          <div>
            <Select value={roleFilter} onValueChange={setRoleFilter}>
              <SelectTrigger className="w-[200px]">
                <SelectValue placeholder="Semua Role" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Semua Role</SelectItem>
                {ROLES.map(role => (
                  <SelectItem key={role.id} value={role.id.toString()}>{role.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </Card>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="text-sm text-slate-500">Total Pengguna</div>
          <div className="text-3xl font-bold text-slate-900 mt-1">{users.length}</div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-slate-500">Aktif</div>
          <div className="text-3xl font-bold text-green-600 mt-1">
            {users.filter(u => u.is_active).length}
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-slate-500">Tidak Aktif</div>
          <div className="text-3xl font-bold text-red-600 mt-1">
            {users.filter(u => !u.is_active).length}
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-slate-500">Roles</div>
          <div className="text-3xl font-bold text-blue-600 mt-1">{ROLES.length}</div>
        </Card>
      </div>

      {/* Users Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredUsers.map((user) => {
          const role = getRoleInfo(user.role_id);
          
          return (
            <Card key={user.id} className="p-6 hover:shadow-md transition-shadow" data-testid={`user-card-${user.id}`}>
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center ${role.color}`}>
                    <UsersIcon className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-slate-900">{user.full_name}</h3>
                    <p className="text-sm text-slate-500">@{user.username}</p>
                  </div>
                </div>
                {user.is_active ? (
                  <UserCheck className="w-5 h-5 text-green-600" />
                ) : (
                  <UserX className="w-5 h-5 text-red-600" />
                )}
              </div>

              <div className="space-y-2 mb-4">
                <Badge className={role.color}>{role.name}</Badge>
                <p className="text-xs text-slate-500">{role.description}</p>
                
                <div className="pt-2 space-y-1">
                  <div className="text-sm text-slate-600">
                    📧 {user.email}
                  </div>
                  {user.phone && (
                    <div className="text-sm text-slate-600">
                      📞 {user.phone}
                    </div>
                  )}
                </div>
              </div>

              <div className="flex gap-2">
                <Button
                  variant={user.is_active ? 'outline' : 'default'}
                  size="sm"
                  className="flex-1"
                  onClick={() => handleToggleActive(user.id)}
                >
                  {user.is_active ? 'Nonaktifkan' : 'Aktifkan'}
                </Button>
              </div>
            </Card>
          );
        })}
      </div>

      {filteredUsers.length === 0 && (
        <Card className="p-12 text-center">
          <UsersIcon className="w-16 h-16 text-slate-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-slate-900 mb-2">Tidak Ada Pengguna</h3>
          <p className="text-slate-600">Coba ubah filter atau tambahkan pengguna baru</p>
        </Card>
      )}

      {/* Add User Form */}
      <Dialog open={showForm} onOpenChange={setShowForm}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>{editingUser ? 'Edit' : 'Tambah'} Pengguna</DialogTitle>
          </DialogHeader>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Username *</Label>
                <Input
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  required
                  placeholder="username"
                />
              </div>
              
              <div>
                <Label>Email *</Label>
                <Input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  required
                  placeholder="email@example.com"
                />
              </div>
            </div>

            <div>
              <Label>Nama Lengkap *</Label>
              <Input
                value={formData.full_name}
                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                required
                placeholder="Nama lengkap"
              />
            </div>

            <div>
              <Label>Password *</Label>
              <Input
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                required
                placeholder="Minimal 6 karakter"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>No. Telepon</Label>
                <Input
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  placeholder="081234567890"
                />
              </div>
              
              <div>
                <Label>Role / Jabatan *</Label>
                <Select value={formData.role_id.toString()} onValueChange={(value) => setFormData({ ...formData, role_id: parseInt(value) })}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {ROLES.map(role => (
                      <SelectItem key={role.id} value={role.id.toString()}>{role.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div>
              <Label>Alamat</Label>
              <Input
                value={formData.address}
                onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                placeholder="Alamat lengkap"
              />
            </div>

            <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
              <h4 className="font-medium text-blue-900 mb-2">Info Role:</h4>
              <p className="text-sm text-blue-800">
                {getRoleInfo(formData.role_id).description}
              </p>
            </div>

            <div className="flex justify-end space-x-2 pt-4">
              <Button type="button" variant="outline" onClick={() => setShowForm(false)}>
                Batal
              </Button>
              <Button type="submit">
                {editingUser ? 'Update' : 'Simpan'} Pengguna
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
