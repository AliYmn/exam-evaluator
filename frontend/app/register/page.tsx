'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { authApi } from '@/lib/api';
import { Terminal, ArrowRight, Sparkles } from 'lucide-react';

export default function RegisterPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    first_name: '',
    last_name: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await authApi.register(formData);

      // Wait briefly for success state then redirect
      await new Promise(resolve => setTimeout(resolve, 800));

      router.push('/login');
    } catch (err: any) {
      setError(err.message || 'Kayıt işlemi başarısız oldu');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        {/* Card */}
        <div className="bg-white rounded-2xl shadow-xl shadow-gray-200/50 border border-gray-100 p-8 relative overflow-hidden">
          {/* Subtle gradient accent */}
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500"></div>

          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center gap-2 mb-6">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center shadow-lg shadow-blue-500/30">
                <Terminal className="w-5 h-5 text-white" />
              </div>
              <span className="text-sm font-mono text-gray-500">exam-evaluator</span>
            </div>
            <h1 className="text-2xl font-semibold text-gray-900 mb-2">
              Hesap Oluştur
            </h1>
            <p className="text-gray-600 text-sm">AI ile sınav değerlendirmeye başlayın</p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-2">
                <label className="block text-xs font-medium text-gray-700 uppercase tracking-wide">
                  Ad
                </label>
                <input
                  type="text"
                  required
                  value={formData.first_name}
                  onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                  className="w-full px-3 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent focus:bg-white transition-all text-gray-900 placeholder-gray-400 text-sm"
                  placeholder="Ali"
                />
              </div>

              <div className="space-y-2">
                <label className="block text-xs font-medium text-gray-700 uppercase tracking-wide">
                  Soyad
                </label>
                <input
                  type="text"
                  required
                  value={formData.last_name}
                  onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                  className="w-full px-3 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent focus:bg-white transition-all text-gray-900 placeholder-gray-400 text-sm"
                  placeholder="Yaman"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="block text-xs font-medium text-gray-700 uppercase tracking-wide">
                E-posta
              </label>
              <input
                type="email"
                required
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent focus:bg-white transition-all text-gray-900 placeholder-gray-400"
                placeholder="ornek@mail.com"
              />
            </div>

            <div className="space-y-2">
              <label className="block text-xs font-medium text-gray-700 uppercase tracking-wide">
                Şifre
              </label>
              <input
                type="password"
                required
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent focus:bg-white transition-all text-gray-900 placeholder-gray-400"
                placeholder="••••••••"
                minLength={6}
              />
              <p className="text-xs text-gray-500 flex items-center gap-1">
                <Sparkles className="w-3 h-3" />
                Minimum 6 karakter
              </p>
            </div>

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-800">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-3.5 rounded-xl font-medium hover:from-blue-700 hover:to-indigo-700 active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-blue-500/30 flex items-center justify-center gap-2 group mt-6"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  <span>Hesap oluşturuluyor...</span>
                </>
              ) : (
                <>
                  <span>Hesap Oluştur</span>
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </button>
          </form>

          {/* Footer */}
          <div className="mt-8 pt-6 border-t border-gray-100">
            <p className="text-center text-sm text-gray-600">
              Zaten hesabınız var mı?{' '}
              <Link
                href="/login"
                className="text-blue-600 hover:text-blue-700 font-medium hover:underline underline-offset-4 transition-colors"
              >
                Giriş Yap
              </Link>
            </p>
          </div>
        </div>

        {/* Bottom hint */}
        <p className="text-center mt-6 text-xs text-gray-500 font-mono">
          v1.0.0 • Güvenli kimlik doğrulama
        </p>
      </div>
    </div>
  );
}
