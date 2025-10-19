'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import DashboardLayout from '@/components/DashboardLayout';
import { Upload, FileText, ArrowLeft, CheckCircle2, AlertCircle } from 'lucide-react';
import Link from 'next/link';
import { examApi } from '@/lib/api';
import { useAuthStore } from '@/lib/store';

export default function NewExamPage() {
  const router = useRouter();
  const { token } = useAuthStore();

  const [examName, setExamName] = useState('');
  const [answerKey, setAnswerKey] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Prevent multiple submissions - HEMEN kontrol et
    if (loading) {
      return;
    }

    // HEMEN loading'i true yap
    setLoading(true);
    setError(null);
    setSuccess(false);

    // Validation
    if (!examName || !answerKey) {
      setError('Please fill in all fields');
      setLoading(false);
      return;
    }

    if (examName.length < 3) {
      setError('Exam name must be at least 3 characters');
      setLoading(false);
      return;
    }

    if (!answerKey.name.toLowerCase().endsWith('.pdf')) {
      setError('Answer key must be a PDF file');
      setLoading(false);
      return;
    }

    if (!token) {
      setError('You must be logged in to create an exam');
      setLoading(false);
      router.push('/login');
      return;
    }

    try {
      // Call API to upload answer key
      const response = await examApi.uploadAnswerKey(token, examName, answerKey);

      setSuccess(true);

      // Show success message briefly, then redirect
      setTimeout(() => {
        router.push(`/dashboard/exams/${response.evaluation_id}`);
      }, 1500);

    } catch (err: any) {
      setError(err.message || 'Failed to create exam. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto">
        {/* Header with gradient accent */}
        <div className="mb-8 relative">
          <Link
            href="/dashboard/exams"
            className="inline-flex items-center gap-2 text-gray-600 hover:text-blue-600 mb-6 group transition-colors"
          >
            <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
            <span className="font-medium">Sınavlara Dön</span>
          </Link>
          <div className="flex items-center gap-4 mb-4">
            <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-500/30">
              <Upload className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-4xl font-bold text-gray-900">Yeni Sınav Oluştur</h1>
              <p className="text-gray-600 mt-1">Cevap anahtarını yükleyin ve sınavınızı başlatın</p>
            </div>
          </div>
          <div className="absolute -bottom-2 left-0 w-32 h-1 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full"></div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6" noValidate>
          {/* Exam Name */}
          <div className="group bg-white rounded-2xl shadow-sm p-6 border border-gray-200 hover:border-blue-300 hover:shadow-md transition-all">
            <label className="flex items-center gap-2 text-sm font-semibold text-gray-900 mb-3 uppercase tracking-wide">
              <FileText className="w-4 h-4 text-blue-600" />
              Sınav Adı
            </label>
            <input
              type="text"
              value={examName}
              onChange={(e) => setExamName(e.target.value)}
              placeholder="örn: Biyoloji Vize Sınavı"
              className="w-full px-4 py-3 bg-gray-50 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 focus:bg-white text-gray-900 placeholder-gray-400 transition-all font-medium"
            />
          </div>

          {/* Answer Key Upload - Enhanced */}
          <div className="group bg-white rounded-2xl shadow-sm p-6 border border-gray-200 hover:border-blue-300 hover:shadow-md transition-all">
            <label className="flex items-center gap-2 text-sm font-semibold text-gray-900 mb-4 uppercase tracking-wide">
              <Upload className="w-4 h-4 text-blue-600" />
              Cevap Anahtarı (PDF)
            </label>
            <div className={`relative border-2 border-dashed rounded-2xl p-10 text-center transition-all ${
              answerKey
                ? 'border-emerald-300 bg-emerald-50'
                : 'border-gray-300 bg-gray-50/50 hover:border-blue-400 hover:bg-blue-50/50'
            }`}>
              <input
                type="file"
                id="answer-key"
                accept=".pdf"
                onChange={(e) => e.target.files && setAnswerKey(e.target.files[0])}
                className="hidden"
              />
              <label htmlFor="answer-key" className="cursor-pointer">
                {answerKey ? (
                  <div className="space-y-4">
                    <div className="w-16 h-16 bg-emerald-100 rounded-2xl flex items-center justify-center mx-auto">
                      <CheckCircle2 className="w-8 h-8 text-emerald-600" />
                    </div>
                    <div>
                      <p className="text-base font-semibold text-gray-900 mb-1">{answerKey.name}</p>
                      <p className="text-sm text-gray-600">
                        {(answerKey.size / 1024).toFixed(2)} KB • PDF Dosyası
                      </p>
                    </div>
                    <button
                      type="button"
                      onClick={(e) => {
                        e.preventDefault();
                        setAnswerKey(null);
                      }}
                      className="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium"
                    >
                      Değiştir
                    </button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="w-16 h-16 bg-blue-100 rounded-2xl flex items-center justify-center mx-auto group-hover:scale-110 transition-transform">
                      <Upload className="w-8 h-8 text-blue-600" />
                    </div>
                    <div>
                      <p className="text-base font-semibold text-gray-900 mb-1">
                        Cevap Anahtarı Yükle
                      </p>
                      <p className="text-sm text-gray-500">
                        PDF dosyanızı sürükleyin veya tıklayın
                      </p>
                    </div>
                    <div className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg font-medium shadow-lg shadow-blue-500/30 hover:shadow-xl hover:from-blue-700 hover:to-indigo-700 transition-all">
                      Dosya Seç
                    </div>
                  </div>
                )}
              </label>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="text-sm font-medium text-red-900 mb-1">Error</h3>
                <p className="text-sm text-red-800">{error}</p>
              </div>
            </div>
          )}

          {/* Success Message */}
          {success && (
            <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4 flex items-start gap-3">
              <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="text-sm font-medium text-emerald-900 mb-1">Success!</h3>
                <p className="text-sm text-emerald-800">
                  Answer key uploaded successfully. Processing in background...
                </p>
              </div>
            </div>
          )}

          {/* Info Box - Enhanced */}
          <div className="relative bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-2xl p-6 overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-blue-200 rounded-full blur-3xl opacity-30"></div>
            <div className="relative">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 bg-blue-500 rounded-xl flex items-center justify-center shadow-lg">
                  <CheckCircle2 className="w-5 h-5 text-white" />
                </div>
                <h3 className="text-base font-bold text-blue-900">Sonraki Adımlar</h3>
              </div>
              <ul className="space-y-2.5 text-sm text-blue-800">
                <li className="flex items-start gap-2">
                  <span className="text-blue-500 font-bold mt-0.5">1.</span>
                  <span>Sınav oluşturulduktan sonra öğrenci cevap kağıtlarını yükleyebilirsiniz</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-500 font-bold mt-0.5">2.</span>
                  <span>AI, cevap anahtarını otomatik olarak analiz edip soruları çıkaracak</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-500 font-bold mt-0.5">3.</span>
                  <span>Her öğrenci kağıdı bu cevap anahtarına göre değerlendirilecek</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-500 font-bold mt-0.5">4.</span>
                  <span>Sınav oluşturduktan sonra istediğiniz zaman öğrenci ekleyebilirsiniz</span>
                </li>
              </ul>
            </div>
          </div>

          {/* Submit Button - Enhanced */}
          <button
            type="submit"
            disabled={loading || !examName || !answerKey || success}
            className="group relative w-full bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white py-5 rounded-2xl font-semibold text-lg hover:from-blue-700 hover:via-indigo-700 hover:to-purple-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 shadow-2xl shadow-blue-500/40 hover:shadow-3xl hover:scale-[1.02] active:scale-[0.98] flex items-center justify-center gap-3 overflow-hidden"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/10 to-white/0 -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 border-white"></div>
                <span>Sınav Oluşturuluyor...</span>
              </>
            ) : (
              <>
                <Upload className="w-6 h-6 group-hover:rotate-12 transition-transform" />
                <span>Sınavı Oluştur</span>
              </>
            )}
          </button>
        </form>
      </div>
    </DashboardLayout>
  );
}
