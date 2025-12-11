import React, { useState, useEffect } from 'react';
import { api } from '../utils/api';
import { getUser } from '../utils/auth';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Users as UsersIcon, Plus, Edit, Trash2, UserCheck, UserX, Mail, Phone } from 'lucide-react';
import { toast } from 'sonner';
import { Switch } from './ui/switch';

export default function Users() {
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    full_name: '',
    phone: '',
    address: '',
    role_id: 3,
    is_active: true
  });
  
  const currentUser = getUser();
  const canEdit = currentUser && [1, 2].includes(currentUser.role_id);
  const canDelete = currentUser && currentUser.role_id === 1;

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [usersRes, rolesRes] = await Promise.all([
        api.get('/users'),
        api.get('/init-data').catch(() => ({ data: {} }))
      ]);
      setUsers(usersRes.data);
      
      // Default roles
      const defaultRoles = [
        { id: 1, name: 'Owner' },
        { id: 2, name: 'Manager' },
        { id: 3, name: 'Finance' },
        { id: 4, name: 'Customer Service' },
        { id: 5, name: 'Kasir' },
        { id: 6, name: 'Loket' },
        { id: 7, name: 'Teknisi' }
      ];
      setRoles(defaultRoles);
    } catch (error) {
      toast.error('Gagal memuat data users');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingUser) {
        await api.put(`/users/${editingUser.id}`, formData);
        toast.success('User berhasil diupdate!');
      } else {
        await api.post('/auth/register', formData);
        toast.success('User berhasil ditambahkan!');
      }
      setShowForm(false);
      setEditingUser(null);
      resetForm();
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Gagal menyimpan user');
    }
  };

  const handleEdit = (user) => {
    setEditingUser(user);
    setFormData({
      username: user.username,
      email: user.email,
      password: '',
      full_name: user.full_name,
      phone: user.phone || '',
      address: user.address || '',
      role_id: user.role_id,
      is_active: user.is_active
    });
    setShowForm(true);
  };

  const handleDelete = async (userId) => {
    if (!window.confirm('Yakin ingin menghapus user ini?')) return;
    
    try {
      await api.delete(`/users/${userId}`);
      toast.success('User berhasil dihapus!');
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Gagal menghapus user');
    }
  };

  const handleToggleActive = async (userId) => {
    try {
      await api.put(`/users/${userId}/toggle-active`);
      toast.success('Status user berhasil diubah!');
      fetchData();
    } catch (error) {
      toast.error('Gagal mengubah status user');
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
      role_id: 3,
      is_active: true
    });
  };

  const getRoleBadge = (roleId) => {
    const role = roles.find(r => r.id === roleId);
    const colors = {
      1: 'bg-purple-100 text-purple-800',
      2: 'bg-blue-100 text-blue-800',
      3: 'bg-green-100 text-green-800',
      4: 'bg-yellow-100 text-yellow-800',
      5: 'bg-orange-100 text-orange-800',
      6: 'bg-pink-100 text-pink-800',
      7: 'bg-slate-100 text-slate-800'
    };
    return (
      <Badge className={colors[roleId] || 'bg-gray-100 text-gray-800'}>
        {role?.name || 'Unknown'}
      </Badge>
    );
  };

  if (loading) {
    return <div className="flex items-center justify-center h-96">Memuat data...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold text-slate-900 tracking-tight mb-2">Manajemen Pengguna</h1>
          <p className="text-slate-600">Kelola user dan role akses sistem</p>
        </div>
        {currentUser?.role_id === 1 && (
          <Button onClick={() => setShowForm(true)}>
            <Plus className="w-4 h-4 mr-2" />
            Tambah User
          </Button>
        )}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="text-sm text-slate-500">Total Users</div>
          <div className="text-3xl font-bold text-slate-900 mt-1">{users.length}</div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-slate-500">Active</div>
          <div className="text-3xl font-bold text-green-600 mt-1">
            {users.filter(u => u.is_active).length}
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-slate-500">Inactive</div>
          <div className="text-3xl font-bold text-red-600 mt-1">
            {users.filter(u => !u.is_active).length}
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-slate-500">Roles</div>
          <div className="text-3xl font-bold text-slate-900 mt-1">{roles.length}</div>
        </Card>
      </div>

      {/* Users List */}
      <Card className="p-6">
        <div className="space-y-4">
          {users.length === 0 ? (
            <div className="text-center py-12">
              <UsersIcon className="w-16 h-16 text-slate-300 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-slate-900 mb-2">Tidak Ada User</h3>
              <p className="text-slate-600">Belum ada user terdaftar</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {users.map((user) => (
                <Card key={user.id} className="p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 bg-slate-200 rounded-full flex items-center justify-center">
                        <UsersIcon className="w-6 h-6 text-slate-600" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-slate-900">{user.full_name}</h3>
                        <p className="text-sm text-slate-500">@{user.username}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {user.is_active ? (
                        <Badge className="bg-green-100 text-green-800">
                          <UserCheck className="w-3 h-3 mr-1" />
                          Active
                        </Badge>
                      ) : (
                        <Badge className="bg-red-100 text-red-800">
                          <UserX className="w-3 h-3 mr-1" />
                          Inactive
                        </Badge>
                      )}
                    </div>
                  </div>

                  <div className="space-y-2 mb-4">
                    <div className="flex items-center gap-2 text-sm text-slate-600">
                      <Mail className="w-4 h-4" />
                      <span>{user.email}</span>
                    </div>
                    {user.phone && (
                      <div className="flex items-center gap-2 text-sm text-slate-600">
                        <Phone className="w-4 h-4" />
                        <span>{user.phone}</span>
                      </div>
                    )}
                    <div className="mt-2">
                      {getRoleBadge(user.role_id)}
                    </div>
                  </div>

                  {canEdit && user.id !== currentUser.id && (
                    <div className="flex gap-2 pt-3 border-t">
                      {currentUser.role_id === 1 && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleToggleActive(user.id)}
                          className="flex-1"
                        >
                          {user.is_active ? 'Nonaktifkan' : 'Aktifkan'}
                        </Button>
                      )}
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleEdit(user)}
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                      {canDelete && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDelete(user.id)}
                        >
                          <Trash2 className="w-4 h-4 text-red-600" />
                        </Button>
                      )}
                    </div>
                  )}
                </Card>
              ))}
            </div>
          )}
        </div>
      </Card>

      {/* Form Dialog */}
      <Dialog open={showForm} onOpenChange={setShowForm}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>{editingUser ? 'Edit User' : 'Tambah User Baru'}</DialogTitle>
          </DialogHeader>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Username *</Label>
                <Input
                  value={formData.username}
                  onChange={(e) => setFormData({...formData, username: e.target.value})}
                  required
                  disabled={!!editingUser}
                />
              </div>
              
              <div>
                <Label>Email *</Label>
                <Input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  required
                />
              </div>
            </div>

            <div>
              <Label>Nama Lengkap *</Label>
              <Input
                value={formData.full_name}
                onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>No. Telepon</Label>
                <Input
                  value={formData.phone}
                  onChange={(e) => setFormData({...formData, phone: e.target.value})}
                  placeholder="08xxxxxxxxxx"
                />
              </div>
              
              <div>
                <Label>Role *</Label>
                <Select 
                  value={formData.role_id.toString()} 
                  onValueChange={(val) => setFormData({...formData, role_id: parseInt(val)})}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {roles.map(role => (
                      <SelectItem key={role.id} value={role.id.toString()}>
                        {role.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div>
              <Label>Password {editingUser ? '(kosongkan jika tidak diubah)' : '*'}</Label>
              <Input
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({...formData, password: e.target.value})}
                required={!editingUser}
                placeholder={editingUser ? 'Kosongkan jika tidak diubah' : 'Minimal 6 karakter'}
              />
            </div>

            <div>
              <Label>Alamat</Label>
              <Input
                value={formData.address}
                onChange={(e) => setFormData({...formData, address: e.target.value})}
                placeholder="Alamat lengkap"
              />
            </div>

            <div className="flex gap-2 pt-4">
              <Button type="submit" className="flex-1">
                {editingUser ? 'Update' : 'Simpan'}
              </Button>
              <Button 
                type="button" 
                variant="outline" 
                onClick={() => {
                  setShowForm(false);
                  setEditingUser(null);
                  resetForm();
                }}
              >
                Batal
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}