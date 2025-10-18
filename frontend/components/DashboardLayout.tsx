'use client';

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/lib/store';
import { LogOut, FileText, LayoutDashboard, FolderOpen, Plus, Terminal, Sparkles } from 'lucide-react';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { user, isAuthenticated, logout, initialize, _hasHydrated } = useAuthStore();
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    // Sadece mount'ta bir kez initialize et
    initialize();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    // Hydration tamamlandıktan sonra kontrol et
    if (_hasHydrated && !isAuthenticated) {
      router.push('/login');
    }
  }, [_hasHydrated, isAuthenticated, router]);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  // Hydration tamamlanana kadar loading göster
  if (!_hasHydrated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <div className="text-center">
          <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-blue-500/20 animate-pulse">
            <Terminal className="w-8 h-8 text-white" />
          </div>
          <div className="flex items-center gap-2 justify-center">
            <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-indigo-600"></div>
            <span className="text-gray-600 font-medium">Yükleniyor...</span>
          </div>
        </div>
      </div>
    );
  }

  // Hydration tamamlandı ama auth yok
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  const isActive = (path: string) => pathname === path || pathname.startsWith(path);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Navigation */}
      <header className={`bg-white border-b border-gray-200 sticky top-0 z-50 backdrop-blur-xl transition-all duration-300 ${
        scrolled ? 'shadow-md bg-white' : 'shadow-sm bg-white/95'
      }`}>
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Logo & Navigation */}
            <div className="flex items-center gap-8">
              <Link href="/dashboard" className="flex items-center gap-3 group cursor-pointer">
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl blur-md opacity-50 group-hover:opacity-75 transition-opacity"></div>
                  <div className="relative w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg group-hover:scale-105 transition-transform">
                    <FileText className="w-6 h-6 text-white" />
                  </div>
                </div>
                <div>
                  <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent group-hover:from-blue-700 group-hover:to-indigo-700 transition-all">
                    Exam Evaluator
                  </h1>
                  <p className="text-xs text-gray-500 font-mono flex items-center gap-1">
                    <Sparkles className="w-3 h-3" />
                    AI-Powered Assessment
                  </p>
                </div>
              </Link>

              {/* Quick Nav */}
              <nav className="hidden md:flex items-center gap-2">
                <Link
                  href="/dashboard"
                  className={`flex items-center gap-2 px-4 py-2 rounded-xl font-medium transition-all ${
                    pathname === '/dashboard'
                      ? 'bg-blue-50 text-blue-600 shadow-sm'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <LayoutDashboard className="w-4 h-4" />
                  <span>Dashboard</span>
                </Link>
                <Link
                  href="/dashboard/exams"
                  className={`flex items-center gap-2 px-4 py-2 rounded-xl font-medium transition-all ${
                    pathname.startsWith('/dashboard/exams')
                      ? 'bg-blue-50 text-blue-600 shadow-sm'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <FolderOpen className="w-4 h-4" />
                  <span>Sınavlar</span>
                </Link>
                <Link
                  href="/dashboard/exams/new"
                  className="flex items-center gap-2 px-4 py-2 rounded-xl font-medium bg-gradient-to-r from-blue-600 to-indigo-600 text-white hover:from-blue-700 hover:to-indigo-700 shadow-lg shadow-blue-500/30 hover:shadow-xl hover:shadow-blue-500/40 transition-all hover:scale-105"
                >
                  <Plus className="w-4 h-4" />
                  <span>Yeni Sınav</span>
                </Link>
              </nav>
            </div>

            {/* User Menu */}
            <div className="flex items-center gap-4">
              <div className="hidden sm:block text-right">
                <p className="font-semibold text-sm text-gray-900">
                  {user?.first_name} {user?.last_name}
                </p>
                <p className="text-xs text-gray-500">{user?.email}</p>
              </div>
              <div className="relative group">
                <div className="absolute inset-0 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full blur-sm opacity-50 group-hover:opacity-75 transition-opacity"></div>
                <div className="relative w-11 h-11 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white font-bold text-sm shadow-lg ring-2 ring-blue-100 group-hover:ring-4 group-hover:scale-105 transition-all cursor-pointer">
                  {user?.first_name?.[0]}{user?.last_name?.[0]}
                </div>
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-4 py-2.5 text-red-600 hover:bg-red-50 rounded-xl transition-all font-medium border border-red-200 hover:border-red-300 hover:shadow-md group"
              >
                <LogOut className="w-4 h-4 group-hover:rotate-12 transition-transform" />
                <span className="hidden sm:inline">Çıkış</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">{children}</main>

      {/* Quick Action FAB (Mobile) */}
      <Link
        href="/dashboard/exams/new"
        className="md:hidden fixed bottom-6 right-6 w-14 h-14 bg-gradient-to-br from-blue-600 to-indigo-600 text-white rounded-full shadow-2xl shadow-blue-500/30 flex items-center justify-center hover:scale-110 transition-transform z-40"
      >
        <Plus className="w-6 h-6" />
      </Link>
    </div>
  );
}
