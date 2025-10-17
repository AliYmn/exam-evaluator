'use client';

import { useState, useEffect } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { FileText, Upload, CheckCircle2, ArrowRight, Eye, Loader2, BarChart3, Clock, XCircle, FolderOpen } from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { examApi, ExamListItem } from '@/lib/api';
import { useAuthStore } from '@/lib/store';

export default function DashboardPage() {
  const router = useRouter();
  const { token } = useAuthStore();

  const [exams, setExams] = useState<ExamListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (token) {
      fetchExams();
    }
  }, [token]);

  const fetchExams = async () => {
    if (!token) {
      router.push('/login');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await examApi.getAllExams(token);
      setExams(response.exams);
    } catch (err: any) {
      console.error('Error fetching exams:', err);

      // Check if it's a 401 Unauthorized error
      if (err.message && err.message.includes('401')) {
        // Token expired, redirect to login
        localStorage.removeItem('auth-storage');
        router.push('/login');
        return;
      }

      setError(err.message || 'Sınavlar yüklenirken bir hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  // Recent evaluations (limit to 5)
  const recentEvaluations = exams.slice(0, 5);
  const isEmpty = exams.length === 0;

  const getRelativeTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Şimdi';
    if (diffMins < 60) return `${diffMins} dk önce`;
    if (diffHours < 24) return `${diffHours} saat önce`;
    if (diffDays < 7) return `${diffDays} gün önce`;
    return date.toLocaleDateString('tr-TR');
  };

  const getStatusDisplay = (status: string) => {
    switch (status) {
      case 'completed':
        return { text: 'Tamamlandı', color: 'emerald' };
      case 'parsing':
        return { text: 'İşleniyor', color: 'amber' };
      case 'failed':
        return { text: 'Başarısız', color: 'red' };
      case 'pending':
      default:
        return { text: 'Bekliyor', color: 'gray' };
    }
  };

  // Loading State
  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <Loader2 className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-4" />
            <p className="text-gray-600">Sınavlar yükleniyor...</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  // Error State
  if (error) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center max-w-md">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <FileText className="w-8 h-8 text-red-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Veriler Yüklenemedi</h2>
            <p className="text-gray-600 mb-6">{error}</p>
            <button
              onClick={fetchExams}
              className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              <Upload className="w-5 h-5" />
              Tekrar Dene
            </button>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div>
          {/* Header */}
        <div className="mb-10">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-2">
                Hoş Geldiniz! 👋
              </h1>
              <p className="text-lg text-gray-600">Sınavlarınızı yönetin ve sonuçları inceleyin.</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-500">Bugün</p>
              <p className="text-xl font-bold text-gray-900">
                {new Date().toLocaleDateString('tr-TR', { day: 'numeric', month: 'long', year: 'numeric' })}
              </p>
            </div>
          </div>
        </div>

        {/* Quick Actions - Compact Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-10">
          {/* Create New Exam */}
          <Link
            href="/dashboard/exams/new"
            className="group relative bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-600 rounded-2xl p-6 text-white shadow-xl shadow-blue-500/30 hover:shadow-2xl hover:shadow-blue-500/40 transition-all hover:scale-[1.02] cursor-pointer overflow-hidden"
          >
            <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl -mr-32 -mt-32 group-hover:bg-white/20 transition-colors"></div>
            <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/5 rounded-full blur-3xl -ml-24 -mb-24"></div>
            <div className="relative">
              <div className="w-16 h-16 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 group-hover:rotate-3 transition-all">
                <Upload className="w-8 h-8" />
              </div>
              <h2 className="text-2xl font-bold mb-2">Yeni Sınav Oluştur</h2>
              <p className="text-blue-100 mb-4 text-base leading-relaxed">Cevap anahtarı ile yeni sınav oluşturun ve öğrencileri ekleyin</p>
              <div className="flex items-center gap-2 text-sm font-semibold bg-white/20 backdrop-blur-sm w-fit px-4 py-2 rounded-lg group-hover:bg-white/30 transition-colors">
                <span>Başla</span>
                <ArrowRight className="w-4 h-4 group-hover:translate-x-2 transition-transform" />
              </div>
            </div>
          </Link>

          {/* View All Exams */}
          <Link
            href="/dashboard/exams"
            className="group relative bg-white rounded-2xl p-6 shadow-lg border-2 border-gray-200 hover:shadow-xl hover:border-blue-300 transition-all hover:scale-[1.02] cursor-pointer overflow-hidden"
          >
            <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 rounded-full blur-3xl -mr-32 -mt-32 group-hover:from-blue-100 group-hover:via-indigo-100 group-hover:to-purple-100 transition-colors"></div>
            <div className="relative">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 via-indigo-600 to-purple-600 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 group-hover:-rotate-3 transition-all shadow-lg shadow-blue-500/30">
                <BarChart3 className="w-8 h-8 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Tüm Sınavlar</h2>
              <p className="text-gray-600 mb-4 text-base leading-relaxed">Tüm sınavları görüntüleyin ve detaylı analizlere göz atın</p>
              <div className="flex items-center gap-2 text-sm font-semibold text-blue-600 bg-blue-50 w-fit px-4 py-2 rounded-lg group-hover:bg-blue-100 transition-colors">
                <span>Sınavları Gör</span>
                <ArrowRight className="w-4 h-4 group-hover:translate-x-2 transition-transform" />
              </div>
            </div>
          </Link>
        </div>

        {/* Recent Evaluations List */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
          <div className="p-6 border-b border-gray-200 bg-gradient-to-r from-gray-50 to-white">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center shadow-lg shadow-blue-500/30">
                  <FileText className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-gray-900">Son Değerlendirmeler</h2>
                  <p className="text-sm text-gray-600">En son eklenen sınavlarınız</p>
                </div>
              </div>
              <Link
                href="/dashboard/exams"
                className="text-sm font-medium text-blue-600 hover:text-blue-700 flex items-center gap-1 hover:gap-2 transition-all"
              >
                Tümünü Gör
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>

          <div className="p-6">
            {loading ? (
              // Loading State
              <div className="text-center py-16">
                <Loader2 className="w-10 h-10 text-blue-600 animate-spin mx-auto mb-4" />
                <p className="text-gray-600">Sınavlar yükleniyor...</p>
              </div>
            ) : isEmpty ? (
              // Empty State
              <div className="text-center py-16">
                <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <FolderOpen className="w-10 h-10 text-gray-400" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Henüz değerlendirme yok</h3>
                <p className="text-gray-600 mb-6 max-w-md mx-auto">
                  İlk sınavınızı oluşturarak AI destekli değerlendirmeye başlayın
                </p>
                <Link
                  href="/dashboard/exams/new"
                  className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-3 rounded-xl font-medium hover:from-blue-700 hover:to-indigo-700 shadow-lg shadow-blue-500/30 transition-all"
                >
                  <Upload className="w-4 h-4" />
                  İlk Sınavı Oluştur
                </Link>
              </div>
            ) : (
              // Evaluations List
              <div className="space-y-3">
                {recentEvaluations.map((evaluation) => (
                  <div
                    key={evaluation.evaluation_id}
                    onClick={() => router.push(`/dashboard/exams/${evaluation.evaluation_id}`)}
                    className="group flex items-center justify-between p-5 bg-gray-50 hover:bg-gradient-to-r hover:from-blue-50 hover:to-indigo-50 rounded-xl cursor-pointer transition-all border border-transparent hover:border-blue-200"
                  >
                    <div className="flex items-center gap-4 flex-1">
                      {/* Status Icon */}
                      <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                        evaluation.status === 'completed'
                          ? 'bg-emerald-100 text-emerald-600'
                          : evaluation.status === 'failed'
                          ? 'bg-red-100 text-red-600'
                          : evaluation.status === 'parsing'
                          ? 'bg-amber-100 text-amber-600'
                          : 'bg-gray-100 text-gray-600'
                      }`}>
                        {evaluation.status === 'completed' ? (
                          <CheckCircle2 className="w-6 h-6" />
                        ) : evaluation.status === 'failed' ? (
                          <XCircle className="w-6 h-6" />
                        ) : (
                          <Clock className="w-6 h-6 animate-pulse" />
                        )}
                      </div>

                      {/* Info */}
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900 mb-1 group-hover:text-blue-600 transition-colors">
                          {evaluation.exam_title}
                        </h3>
                        <div className="flex items-center gap-4 text-sm text-gray-600">
                          <span className="flex items-center gap-1">
                            <FileText className="w-4 h-4" />
                            {getStatusDisplay(evaluation.status).text}
                          </span>
                          {evaluation.total_questions && evaluation.total_questions > 0 && (
                            <>
                              <span>•</span>
                              <span>{evaluation.total_questions} soru</span>
                            </>
                          )}
                          {evaluation.status === 'parsing' && evaluation.progress_percentage > 0 && (
                            <>
                              <span>•</span>
                              <span className="font-medium text-blue-600">
                                {Math.round(evaluation.progress_percentage)}%
                              </span>
                            </>
                          )}
                        </div>
                      </div>

                      {/* Date & Action */}
                      <div className="flex items-center gap-4">
                        <span className="text-sm text-gray-500">{getRelativeTime(evaluation.created_at)}</span>
                        <button className="w-9 h-9 rounded-lg bg-white border border-gray-200 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all hover:border-blue-300 hover:bg-blue-50">
                          <Eye className="w-4 h-4 text-gray-600" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Footer Stats */}
          {!isEmpty && (
            <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-6">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
                    <span className="text-gray-600">
                      <span className="font-semibold text-gray-900">
                        {recentEvaluations.filter(e => e.status === 'completed').length}
                      </span> Tamamlandı
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></div>
                    <span className="text-gray-600">
                      <span className="font-semibold text-gray-900">
                        {recentEvaluations.filter(e => e.status === 'parsing' || e.status === 'pending').length}
                      </span> İşleniyor
                    </span>
                  </div>
                  {recentEvaluations.filter(e => e.status === 'failed').length > 0 && (
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full bg-red-500"></div>
                      <span className="text-gray-600">
                        <span className="font-semibold text-gray-900">
                          {recentEvaluations.filter(e => e.status === 'failed').length}
                        </span> Başarısız
                      </span>
                    </div>
                  )}
                </div>
                <Link
                  href="/dashboard/exams"
                  className="text-blue-600 hover:text-blue-700 font-medium flex items-center gap-1"
                >
                  Tüm {exams.length} sınavı gör
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
