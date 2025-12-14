import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { CheckCircle, Circle, Clock, Upload, Camera } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Textarea } from './ui/textarea';
import axios from 'axios';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const STEP_CONFIG = [
  { name: 'Survey Teknis', weight: 50, icon: '🔍', description: 'Survey lokasi dan kebutuhan teknis' },
  { name: 'Pemasangan/Instalasi', weight: 20, icon: '🔧', description: 'Pemasangan perangkat dan instalasi' },
  { name: 'Pemeriksaan NIDI/SLO', weight: 20, icon: '📋', description: 'Pemeriksaan dan pengurusan sertifikat' },
  { name: 'Pemberkasan Teknis', weight: 8, icon: '📁', description: 'Melengkapi dokumen teknis' },
  { name: 'Pemasangan KWH Meter', weight: 2, icon: '⚡', description: 'Pemasangan meteran listrik' }
];

export default function TechnicalProgressTracker({ orderId, onUpdate }) {
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedStep, setSelectedStep] = useState(null);
  const [showUpdateModal, setShowUpdateModal] = useState(false);
  const [updateData, setUpdateData] = useState({
    step_name: '',
    status: '',
    notes: '',
    photos: []
  });

  useEffect(() => {
    fetchProgress();
  }, [orderId]);

  const fetchProgress = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${BACKEND_URL}/api/technical-progress/${orderId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setProgress(response.data);
    } catch (error) {
      if (error.response?.status === 404) {
        // Progress belum dibuat, create default
        await createProgress();
      } else {
        console.error('Error fetching progress:', error);
      }
    } finally {
      setLoading(false);
    }
  };

  const createProgress = async () => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${BACKEND_URL}/api/technical-progress`,
        { order_id: orderId },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      await fetchProgress();
    } catch (error) {
      console.error('Error creating progress:', error);
    }
  };

  const handleUpdateStep = (step) => {
    setSelectedStep(step);
    setUpdateData({
      step_name: step.step_name,
      status: step.status,
      notes: step.notes || '',
      photos: step.photos || []
    });
    setShowUpdateModal(true);
  };

  const handleSubmitUpdate = async () => {
    try {
      const token = localStorage.getItem('token');
      await axios.put(
        `${BACKEND_URL}/api/technical-progress/${orderId}/step`,
        updateData,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      toast.success('Status tahapan berhasil diupdate!');
      setShowUpdateModal(false);
      await fetchProgress();
      if (onUpdate) onUpdate();
    } catch (error) {
      toast.error('Gagal update tahapan: ' + (error.response?.data?.detail || error.message));
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-6 h-6 text-green-500" />;
      case 'in_progress':
        return <Clock className="w-6 h-6 text-blue-500 animate-pulse" />;
      default:
        return <Circle className="w-6 h-6 text-gray-300" />;
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'completed':
        return <Badge className="bg-green-100 text-green-800">Selesai</Badge>;
      case 'in_progress':
        return <Badge className="bg-blue-100 text-blue-800">Dalam Proses</Badge>;
      default:
        return <Badge className="bg-gray-100 text-gray-600">Belum Mulai</Badge>;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!progress) {
    return (
      <Card>
        <CardContent className="py-8">
          <p className="text-center text-gray-500">Progress tracking tidak tersedia</p>
        </CardContent>
      </Card>
    );
  }

  const overallProgress = progress.overall_progress || 0;

  return (
    <div className="space-y-6">
      {/* Overall Progress */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>🎯 Progress Keseluruhan</span>
            <span className="text-3xl font-bold text-blue-600">{overallProgress.toFixed(1)}%</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Main Progress Bar */}
          <div>
            <Progress value={overallProgress} className="h-4" />
            <p className="text-sm text-gray-500 mt-2">
              {overallProgress === 100 
                ? '✅ Semua tahapan telah selesai!' 
                : `${progress.steps?.filter(s => s.status === 'completed').length || 0} dari ${progress.steps?.length || 0} tahapan selesai`
              }
            </p>
          </div>

          {/* Status Breakdown */}
          <div className="grid grid-cols-3 gap-3 pt-3 border-t">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {progress.steps?.filter(s => s.status === 'completed').length || 0}
              </div>
              <div className="text-xs text-gray-600">Selesai</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {progress.steps?.filter(s => s.status === 'in_progress').length || 0}
              </div>
              <div className="text-xs text-gray-600">Sedang Berjalan</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-400">
                {progress.steps?.filter(s => s.status === 'not_started').length || 0}
              </div>
              <div className="text-xs text-gray-600">Belum Dimulai</div>
            </div>
          </div>

          {/* Progress Calculation Info */}
          <div className="text-xs text-gray-500 bg-gray-50 rounded p-2">
            <span className="font-medium">ℹ️ Cara Perhitungan:</span> Progress dihitung berdasarkan bobot setiap tahapan. 
            Tahapan "Selesai" = 100% × bobot, "Sedang Berjalan" = 50% × bobot.
          </div>
        </CardContent>
      </Card>

      {/* Step-by-Step Progress */}
      <Card>
        <CardHeader>
          <CardTitle>📋 Tahapan Pekerjaan</CardTitle>
          <CardDescription>Klik untuk update status setiap tahapan</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {progress.steps?.map((step, index) => {
              const config = STEP_CONFIG.find(c => c.name === step.step_name) || {};
              
              return (
                <div
                  key={index}
                  className={`relative border rounded-lg p-4 transition-all cursor-pointer ${
                    step.status === 'completed'
                      ? 'bg-green-50 border-green-200'
                      : step.status === 'in_progress'
                      ? 'bg-blue-50 border-blue-200'
                      : 'bg-white hover:bg-gray-50'
                  }`}
                  onClick={() => handleUpdateStep(step)}
                >
                  {/* Connector Line */}
                  {index < progress.steps.length - 1 && (
                    <div className="absolute left-6 top-16 bottom-[-16px] w-0.5 bg-gray-200"></div>
                  )}

                  <div className="flex items-start gap-4">
                    {/* Icon & Status */}
                    <div className="flex-shrink-0 z-10 bg-white rounded-full">
                      {getStatusIcon(step.status)}
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-2xl">{config.icon}</span>
                            <h4 className="font-semibold text-lg">{step.step_name}</h4>
                            <span className="text-sm text-gray-500">({step.step_weight}%)</span>
                          </div>
                          <p className="text-sm text-gray-600">{config.description}</p>
                        </div>
                        {getStatusBadge(step.status)}
                      </div>

                      {/* Progress Bar for this step with percentage */}
                      <div className="space-y-1">
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-gray-600">Progress tahapan ini:</span>
                          <span className="font-semibold text-gray-700">
                            {step.status === 'completed' ? '100%' : step.status === 'in_progress' ? '50%' : '0%'}
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2.5">
                          <div
                            className={`h-2.5 rounded-full transition-all ${
                              step.status === 'completed'
                                ? 'bg-green-500'
                                : step.status === 'in_progress'
                                ? 'bg-blue-500'
                                : 'bg-gray-300'
                            }`}
                            style={{ width: step.status === 'completed' ? '100%' : step.status === 'in_progress' ? '50%' : '0%' }}
                          ></div>
                        </div>
                        <div className="flex items-center justify-between text-xs text-gray-500">
                          <span>Kontribusi ke total: {step.step_weight}%</span>
                          <span>
                            {step.status === 'completed' 
                              ? `✓ +${step.step_weight}%` 
                              : step.status === 'in_progress'
                              ? `⏳ +${(step.step_weight * 0.5).toFixed(1)}%`
                              : `○ +0%`
                            }
                          </span>
                        </div>
                      </div>

                      {/* Timestamps */}
                      <div className="flex gap-4 text-xs text-gray-500">
                        {step.started_at && (
                          <span>🚀 Mulai: {new Date(step.started_at).toLocaleString('id-ID')}</span>
                        )}
                        {step.completed_at && (
                          <span>✅ Selesai: {new Date(step.completed_at).toLocaleString('id-ID')}</span>
                        )}
                      </div>

                      {/* Notes */}
                      {step.notes && (
                        <div className="mt-2 p-2 bg-white rounded text-sm">
                          <span className="font-medium">Catatan:</span> {step.notes}
                        </div>
                      )}

                      {/* Photos */}
                      {step.photos && step.photos.length > 0 && (
                        <div className="mt-2 flex gap-2">
                          {step.photos.map((photo, idx) => (
                            <div key={idx} className="relative w-20 h-20 rounded overflow-hidden border">
                              <img src={photo} alt={`Photo ${idx + 1}`} className="w-full h-full object-cover" />
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Update Modal */}
      <Dialog open={showUpdateModal} onOpenChange={setShowUpdateModal}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Update Status Tahapan</DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Tahapan</label>
              <input
                type="text"
                value={updateData.step_name}
                disabled
                className="w-full border rounded-lg px-3 py-2 bg-gray-50"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Status</label>
              <select
                value={updateData.status}
                onChange={(e) => setUpdateData({ ...updateData, status: e.target.value })}
                className="w-full border rounded-lg px-3 py-2"
              >
                <option value="not_started">Belum Mulai</option>
                <option value="in_progress">Dalam Proses</option>
                <option value="completed">Selesai</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Catatan</label>
              <Textarea
                value={updateData.notes}
                onChange={(e) => setUpdateData({ ...updateData, notes: e.target.value })}
                placeholder="Tambahkan catatan pekerjaan..."
                rows={4}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                <Camera className="w-4 h-4 inline mr-2" />
                Foto Dokumentasi (Coming Soon)
              </label>
              <div className="border-2 border-dashed rounded-lg p-8 text-center text-gray-400">
                <Upload className="w-8 h-8 mx-auto mb-2" />
                <p className="text-sm">Upload foto dokumentasi</p>
                <p className="text-xs mt-1">Fitur upload foto akan segera tersedia</p>
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-4">
              <Button variant="outline" onClick={() => setShowUpdateModal(false)}>
                Batal
              </Button>
              <Button onClick={handleSubmitUpdate} className="bg-blue-600 hover:bg-blue-700">
                Simpan Update
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
