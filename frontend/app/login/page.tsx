'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { authApi } from '@/lib/api';
import { useAuthStore } from '@/lib/store';
import { Terminal, ArrowRight } from 'lucide-react';

export default function LoginPage() {
  const router = useRouter();
  const { setAuth, isAuthenticated, _hasHydrated } = useAuthStore();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    email: 'demo@demo.com',
    password: 'demo12345!',
  });

  // Redirect to dashboard if already logged in
  useEffect(() => {
    if (_hasHydrated && isAuthenticated) {
      router.push('/dashboard');
    }
  }, [_hasHydrated, isAuthenticated, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await authApi.login(formData);
      setAuth(response.user, response.access_token);

      // Wait for Zustand persist to complete before redirect
      await new Promise(resolve => setTimeout(resolve, 150));

      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Geçersiz kullanıcı adı veya şifre');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-6">
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
              Tekrar Hoş Geldiniz
            </h1>
            <p className="text-gray-600 text-sm">Devam etmek için giriş yapın</p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-5">
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
              />
            </div>

            {/* Demo Account Info */}
            <div className="bg-gradient-to-r from-amber-50 to-yellow-50 border border-amber-200 rounded-xl p-4">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 bg-amber-400 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-lg">🎯</span>
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-amber-900 text-sm mb-1">Demo Hesap</h3>
                  <p className="text-xs text-amber-800 leading-relaxed">
                    Test için hazır kullanıcı bilgileri otomatik dolduruldu. Hemen giriş yapabilirsiniz!
                  </p>
                  <div className="mt-2 space-y-1">
                    <div className="flex items-center gap-2 text-xs font-mono text-amber-900">
                      <span className="font-semibold">Email:</span>
                      <code className="bg-amber-100 px-2 py-0.5 rounded">demo@demo.com</code>
                    </div>
                    <div className="flex items-center gap-2 text-xs font-mono text-amber-900">
                      <span className="font-semibold">Şifre:</span>
                      <code className="bg-amber-100 px-2 py-0.5 rounded">demo12345!</code>
                    </div>
                  </div>
                </div>
              </div>
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
              className="group relative w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-4 rounded-xl font-semibold hover:from-blue-700 hover:to-indigo-700 active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-xl shadow-blue-500/40 flex items-center justify-center gap-2 mt-6 overflow-hidden"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/10 to-white/0 -translate-x-full group-hover:translate-x-full transition-transform duration-700"></div>
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  <span>Giriş yapılıyor...</span>
                </>
              ) : (
                <>
                  <span>Giriş Yap</span>
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </button>
          </form>

          {/* Footer */}
          <div className="mt-8 pt-6 border-t border-gray-100">
            <p className="text-center text-sm text-gray-600">
              Hesabınız yok mu?{' '}
              <Link
                href="/register"
                className="text-blue-600 hover:text-blue-700 font-medium hover:underline underline-offset-4 transition-colors"
              >
                Kayıt Ol
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
