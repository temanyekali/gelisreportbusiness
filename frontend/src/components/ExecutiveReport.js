import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { 
  Download, FileText, TrendingUp, TrendingDown, AlertTriangle, 
  CheckCircle, DollarSign, PieChart, BarChart3, ArrowUpRight,
  ArrowDownRight, Minus, Target, Award, Zap, RefreshCw
} from 'lucide-react';
import { api } from '../utils/api';
import { toast } from 'sonner';

export default function ExecutiveReport() {
  const [loading, setLoading] = useState(false);
  const [summaryData, setSummaryData] = useState(null);
  const [dateRange, setDateRange] = useState({
    start_date: new Date(new Date().setDate(new Date().getDate() - 30)).toISOString().split('T')[0],
    end_date: new Date().toISOString().split('T')[0]
  });

  useEffect(() => {
    fetchSummary();
  }, []);

  const fetchSummary = async () => {
    setLoading(true);
    try {
      const response = await api.get('/reports/executive-summary', {
        params: {
          start_date: `${dateRange.start_date}T00:00:00`,
          end_date: `${dateRange.end_date}T23:59:59`
        }
      });
      setSummaryData(response.data);
      toast.success('Ringkasan eksekutif berhasil dimuat');
    } catch (error) {
      console.error('Executive summary error:', error);
      toast.error('Gagal memuat ringkasan: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value || 0);
  };

  const formatPercent = (value) => {
    const num = parseFloat(value || 0);
    return `${num >= 0 ? '+' : ''}${num.toFixed(1)}%`;
  };

  const getHealthColor = (score) => {
    if (score >= 80) return 'text-green-600 bg-green-50 border-green-200';
    if (score >= 60) return 'text-blue-600 bg-blue-50 border-blue-200';
    if (score >= 40) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    return 'text-red-600 bg-red-50 border-red-200';
  };

  const getAlertColor = (level) => {
    if (level === 'critical') return 'destructive';
    if (level === 'warning') return 'default';
    return 'secondary';
  };

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center min-h-screen">
        <div className="text-center">
          <RefreshCw className="w-12 h-12 animate-spin mx-auto mb-4 text-slate-400" />
          <p className="text-slate-600">Memuat ringkasan eksekutif...</p>
        </div>
      </div>
    );
  }

  if (!summaryData) {
    return (
      <div className="p-6">
        <Card>
          <CardContent className="p-12 text-center">
            <FileText className="w-16 h-16 mx-auto mb-4 text-slate-300" />
            <p className="text-slate-600 mb-4">Belum ada data. Pilih periode dan klik "Generate Report"</p>
            <Button onClick={fetchSummary}>Generate Report</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 bg-slate-50 min-h-screen">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Ringkasan Eksekutif</h1>
          <p className="text-slate-600 mt-1">Analisa keuangan & performa bisnis komprehensif</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={fetchSummary} disabled={loading}>
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
          <Button variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Export PDF
          </Button>
        </div>
      </div>

      {/* Date Range Filter */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col md:flex-row gap-4 items-end">
            <div className="flex-1">
              <label className="text-sm font-medium text-slate-700 block mb-2">Tanggal Mulai</label>
              <input
                type="date"
                value={dateRange.start_date}
                onChange={(e) => setDateRange({ ...dateRange, start_date: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-md"
              />
            </div>
            <div className="flex-1">
              <label className="text-sm font-medium text-slate-700 block mb-2">Tanggal Akhir</label>
              <input
                type="date"
                value={dateRange.end_date}
                onChange={(e) => setDateRange({ ...dateRange, end_date: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-md"
              />
            </div>
            <Button onClick={fetchSummary} disabled={loading}>
              Generate Report
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Financial Health Score */}
      <Card className={`border-2 ${getHealthColor(summaryData.financial_health_score)}`}>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-full bg-white flex items-center justify-center shadow-lg">
                <span className="text-2xl font-bold">{summaryData.financial_health_score}</span>
              </div>
              <div>
                <h3 className="text-lg font-semibold">Financial Health Score</h3>
                <p className="text-2xl font-bold mt-1">{summaryData.health_status}</p>
                <p className="text-sm mt-1 opacity-75">Periode: {new Date(summaryData.period_start).toLocaleDateString('id-ID')} - {new Date(summaryData.period_end).toLocaleDateString('id-ID')}</p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-sm opacity-75">Overall Growth</div>
              <div className="flex items-center gap-2 mt-1">
                {summaryData.overall_revenue_growth > 0 ? (
                  <TrendingUp className="w-6 h-6 text-green-600" />
                ) : summaryData.overall_revenue_growth < 0 ? (
                  <TrendingDown className="w-6 h-6 text-red-600" />
                ) : (
                  <Minus className="w-6 h-6 text-slate-400" />
                )}
                <span className="text-2xl font-bold">{formatPercent(summaryData.overall_revenue_growth)}</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-slate-600 flex items-center gap-2">
              <DollarSign className="w-4 h-4" />
              Total Revenue
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-slate-900">
              {formatCurrency(summaryData.total_revenue)}
            </div>
            <div className="flex items-center gap-1 mt-2 text-sm">
              {summaryData.overall_revenue_growth > 0 ? (
                <><ArrowUpRight className="w-4 h-4 text-green-600" /><span className="text-green-600">{formatPercent(summaryData.overall_revenue_growth)}</span></>
              ) : (
                <><ArrowDownRight className="w-4 h-4 text-red-600" /><span className="text-red-600">{formatPercent(summaryData.overall_revenue_growth)}</span></>
              )}
              <span className="text-slate-500">vs periode sebelumnya</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-slate-600 flex items-center gap-2">
              <Target className="w-4 h-4" />
              Net Profit
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${summaryData.net_profit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {formatCurrency(summaryData.net_profit)}
            </div>
            <div className="flex items-center gap-1 mt-2 text-sm">
              <span className="text-slate-600">Margin: {summaryData.overall_profit_margin.toFixed(1)}%</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-slate-600 flex items-center gap-2">
              <PieChart className="w-4 h-4" />
              Expense Ratio
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-slate-900">
              {summaryData.overall_expense_ratio.toFixed(1)}%
            </div>
            <div className="mt-2">
              <div className="text-xs text-slate-500 mb-1">Expenses: {formatCurrency(summaryData.total_expenses)}</div>
              <div className="w-full bg-slate-200 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full ${summaryData.overall_expense_ratio < 60 ? 'bg-green-500' : summaryData.overall_expense_ratio < 70 ? 'bg-yellow-500' : 'bg-red-500'}`}
                  style={{ width: `${Math.min(summaryData.overall_expense_ratio, 100)}%` }}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-slate-600 flex items-center gap-2">
              <BarChart3 className="w-4 h-4" />
              Business Units
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-slate-900">
              {summaryData.total_business_units}
            </div>
            <div className="flex items-center gap-2 mt-2 text-xs">
              <span className="text-green-600">↑ {summaryData.growing_units}</span>
              <span className="text-slate-500">→ {summaryData.stable_units}</span>
              <span className="text-red-600">↓ {summaryData.declining_units}</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Alerts */}
      {summaryData.alerts && summaryData.alerts.length > 0 && (
        <Card className="border-orange-200 bg-orange-50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-orange-900">
              <AlertTriangle className="w-5 h-5" />
              Critical Alerts ({summaryData.alerts.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {summaryData.alerts.map((alert, idx) => (
                <div key={idx} className="bg-white p-4 rounded-lg border border-orange-200">
                  <div className="flex items-start gap-3">
                    <Badge variant={getAlertColor(alert.level)}>{alert.level}</Badge>
                    <div className="flex-1">
                      <div className="font-semibold text-slate-900">{alert.message}</div>
                      <div className="text-sm text-slate-600 mt-1">{alert.action}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Top Performers */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {summaryData.highest_revenue_business && (
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Award className="w-4 h-4 text-yellow-600" />
                Highest Revenue
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-lg font-bold text-slate-900">
                {summaryData.highest_revenue_business.name}
              </div>
              <div className="text-2xl font-bold text-green-600 mt-2">
                {formatCurrency(summaryData.highest_revenue_business.revenue)}
              </div>
            </CardContent>
          </Card>
        )}

        {summaryData.fastest_growing_business && (
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Zap className="w-4 h-4 text-blue-600" />
                Fastest Growing
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-lg font-bold text-slate-900">
                {summaryData.fastest_growing_business.name}
              </div>
              <div className="text-2xl font-bold text-blue-600 mt-2">
                {formatPercent(summaryData.fastest_growing_business.growth_rate)}
              </div>
            </CardContent>
          </Card>
        )}

        {summaryData.highest_margin_business && (
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Target className="w-4 h-4 text-purple-600" />
                Highest Margin
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-lg font-bold text-slate-900">
                {summaryData.highest_margin_business.name}
              </div>
              <div className="text-2xl font-bold text-purple-600 mt-2">
                {summaryData.highest_margin_business.margin.toFixed(1)}%
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Business Units Performance */}
      <Card>
        <CardHeader>
          <CardTitle>Business Units Performance</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {summaryData.business_units.map((bu, idx) => (
              <div key={idx} className="p-4 bg-slate-50 rounded-lg border border-slate-200">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <h4 className="font-semibold text-lg text-slate-900">{bu.business_name}</h4>
                      <Badge variant={bu.status === 'growing' ? 'success' : bu.status === 'declining' ? 'destructive' : 'secondary'}>
                        {bu.status}
                      </Badge>
                    </div>
                    <div className="text-sm text-slate-600 mt-1">{bu.business_category}</div>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                      <div className="text-xs text-slate-500">Revenue</div>
                      <div className="font-semibold text-slate-900">{formatCurrency(bu.total_revenue)}</div>
                      <div className={`text-xs ${bu.revenue_growth > 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {formatPercent(bu.revenue_growth)}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-slate-500">Profit</div>
                      <div className={`font-semibold ${bu.net_profit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {formatCurrency(bu.net_profit)}
                      </div>
                      <div className="text-xs text-slate-600">{bu.profit_margin.toFixed(1)}% margin</div>
                    </div>
                    <div>
                      <div className="text-xs text-slate-500">Orders</div>
                      <div className="font-semibold text-slate-900">{bu.total_orders}</div>
                      <div className="text-xs text-slate-600">{bu.completion_rate.toFixed(0)}% completed</div>
                    </div>
                    <div>
                      <div className="text-xs text-slate-500">Avg Order</div>
                      <div className="font-semibold text-slate-900">{formatCurrency(bu.average_order_value)}</div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Insights */}
      {summaryData.insights && summaryData.insights.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-blue-600" />
              Key Insights
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {summaryData.insights.map((insight, idx) => (
                <div key={idx} className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <h4 className="font-semibold text-slate-900 mb-2">{insight.title}</h4>
                  <p className="text-sm text-slate-700">{insight.description}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Recommendations */}
      {summaryData.recommendations && summaryData.recommendations.length > 0 && (
        <Card className="border-green-200 bg-green-50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-green-900">
              <Target className="w-5 h-5" />
              Strategic Recommendations
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {summaryData.recommendations.map((rec, idx) => (
                <div key={idx} className="bg-white p-6 rounded-lg border border-green-200">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <Badge variant={rec.priority === 'high' ? 'destructive' : rec.priority === 'medium' ? 'default' : 'secondary'}>
                          {rec.priority} priority
                        </Badge>
                        <Badge variant="outline">{rec.category}</Badge>
                      </div>
                      <h4 className="font-bold text-lg text-slate-900">{rec.title}</h4>
                    </div>
                  </div>
                  <p className="text-slate-700 mb-3">{rec.description}</p>
                  {rec.action_items && rec.action_items.length > 0 && (
                    <div className="mb-3">
                      <div className="text-sm font-semibold text-slate-700 mb-2">Action Items:</div>
                      <ul className="list-disc list-inside space-y-1">
                        {rec.action_items.map((item, itemIdx) => (
                          <li key={itemIdx} className="text-sm text-slate-600">{item}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  <div className="bg-green-50 p-3 rounded border border-green-200">
                    <div className="text-xs font-semibold text-green-900 mb-1">Potential Impact</div>
                    <div className="text-sm text-green-700">{rec.potential_impact}</div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Summary Stats */}
      {summaryData.summary_stats && (
        <Card>
          <CardHeader>
            <CardTitle>Summary Statistics</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-slate-50 rounded-lg">
                <div className="text-sm text-slate-600">Total Orders</div>
                <div className="text-2xl font-bold text-slate-900 mt-1">
                  {summaryData.summary_stats.total_orders}
                </div>
              </div>
              <div className="text-center p-4 bg-slate-50 rounded-lg">
                <div className="text-sm text-slate-600">Completed</div>
                <div className="text-2xl font-bold text-green-600 mt-1">
                  {summaryData.summary_stats.total_completed_orders}
                </div>
              </div>
              <div className="text-center p-4 bg-slate-50 rounded-lg">
                <div className="text-sm text-slate-600">Completion Rate</div>
                <div className="text-2xl font-bold text-blue-600 mt-1">
                  {summaryData.summary_stats.overall_completion_rate.toFixed(1)}%
                </div>
              </div>
              <div className="text-center p-4 bg-slate-50 rounded-lg">
                <div className="text-sm text-slate-600">Avg Order Value</div>
                <div className="text-2xl font-bold text-purple-600 mt-1">
                  {formatCurrency(summaryData.summary_stats.average_order_value)}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
