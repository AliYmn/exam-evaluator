'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store';
import Link from 'next/link';
import {
  Terminal,
  ArrowRight,
  Sparkles,
  CheckCircle2,
  Zap,
  Brain,
  FileText,
  Users,
  BarChart3,
  Shield,
  Clock,
  Lightbulb
} from 'lucide-react';

export default function Home() {
  const router = useRouter();
  const { isAuthenticated, _hasHydrated } = useAuthStore();
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    if (_hasHydrated) {
      setIsChecking(false);
      if (isAuthenticated) {
        router.push('/dashboard');
      }
    }
  }, [isAuthenticated, _hasHydrated, router]);

  if (isChecking) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="border-b border-gray-100 bg-white sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center shadow-lg shadow-blue-500/30">
                <Terminal className="w-5 h-5 text-white" />
              </div>
              <div>
                <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                  Exam Evaluator
                </span>
                <p className="text-xs text-gray-500 font-mono">AI-Powered Assessment</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Link
                href="/login"
                className="px-5 py-2.5 text-gray-700 hover:text-gray-900 font-medium transition-colors"
              >
                Giriş Yap
              </Link>
              <Link
                href="/register"
                className="px-5 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl font-medium hover:from-blue-700 hover:to-indigo-700 shadow-lg shadow-blue-500/30 transition-all flex items-center gap-2 group"
              >
                <span>Başlayın</span>
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-6 pt-20 pb-16 bg-gradient-to-b from-blue-50/30 to-white">
        <div className="text-center max-w-4xl mx-auto">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-50 border border-blue-200 rounded-full text-sm font-medium text-blue-700 mb-8">
            <Sparkles className="w-4 h-4" />
            <span>LangGraph + Google Gemini ile Destekleniyor</span>
          </div>

          {/* Title */}
          <h1 className="text-6xl font-bold text-gray-900 mb-6 leading-tight">
            AI ile Sınav Değerlendirme
            <br />
            <span className="bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 bg-clip-text text-transparent">
              Artık Çok Kolay
            </span>
          </h1>

          {/* Description */}
          <p className="text-xl text-gray-600 mb-10 leading-relaxed max-w-3xl mx-auto">
            Cevap anahtarınızı ve öğrenci cevaplarını yükleyin, yapay zeka her soruyu değerlendirsin,
            detaylı feedback üretsin ve performans analizi sağlasın. <strong>Agentic AI</strong> ile
            self-correction ve confidence scores.
          </p>

          {/* CTA Buttons */}
          <div className="flex items-center justify-center gap-4 mb-16">
            <Link
              href="/login"
              className="group px-8 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl font-semibold text-lg hover:from-blue-700 hover:to-indigo-700 shadow-2xl shadow-blue-500/40 transition-all flex items-center gap-3 hover:scale-105"
            >
              <span>Demo Hesabı ile Giriş Yap</span>
              <ArrowRight className="w-5 h-5 group-hover:translate-x-2 transition-transform" />
            </Link>
            <a
              href="https://github.com/yourusername/exam-evaluator"
          target="_blank"
          rel="noopener noreferrer"
              className="px-8 py-4 bg-white text-gray-700 rounded-xl font-semibold text-lg border-2 border-gray-200 hover:border-gray-300 hover:shadow-lg transition-all flex items-center gap-3"
            >
              <Terminal className="w-5 h-5" />
              <span>GitHub'da İncele</span>
            </a>
          </div>

          {/* Demo Info */}
          <div className="inline-flex items-center gap-2 px-5 py-3 bg-amber-50 border border-amber-200 rounded-xl text-sm text-amber-900">
            <span className="text-lg">🎯</span>
            <span className="font-medium">Demo: demo@demo.com / demo12345!</span>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="max-w-7xl mx-auto px-6 py-16">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">Neden Exam Evaluator?</h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Modern AI teknolojileri ile güçlendirilmiş, profesyonel sınav değerlendirme platformu
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Feature 1 */}
          <div className="group bg-white rounded-2xl p-6 border border-gray-200 hover:border-blue-300 hover:shadow-xl transition-all">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform shadow-lg shadow-blue-500/30">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Agentic AI Architecture</h3>
            <p className="text-gray-600 leading-relaxed">
              LangGraph ile multi-step reasoning, self-correction ve quality checks. ReAct pattern implementation.
            </p>
          </div>

          {/* Feature 2 */}
          <div className="group bg-white rounded-2xl p-6 border border-gray-200 hover:border-blue-300 hover:shadow-xl transition-all">
            <div className="w-12 h-12 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform shadow-lg shadow-emerald-500/30">
              <CheckCircle2 className="w-6 h-6 text-white" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Otomatik Değerlendirme</h3>
            <p className="text-gray-600 leading-relaxed">
              Her soru için detaylı puanlama, Türkçe feedback ve confidence scores. Low confidence → human review.
            </p>
          </div>

          {/* Feature 3 */}
          <div className="group bg-white rounded-2xl p-6 border border-gray-200 hover:border-blue-300 hover:shadow-xl transition-all">
            <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform shadow-lg shadow-purple-500/30">
              <FileText className="w-6 h-6 text-white" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">PDF Parsing</h3>
            <p className="text-gray-600 leading-relaxed">
              Cevap anahtarı ve öğrenci cevaplarını PDF'den otomatik çıkarım. Structured output garantisi.
            </p>
          </div>

          {/* Feature 4 */}
          <div className="group bg-white rounded-2xl p-6 border border-gray-200 hover:border-blue-300 hover:shadow-xl transition-all">
            <div className="w-12 h-12 bg-gradient-to-br from-orange-500 to-red-600 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform shadow-lg shadow-orange-500/30">
              <Zap className="w-6 h-6 text-white" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Real-time SSE Streaming</h3>
            <p className="text-gray-600 leading-relaxed">
              Canlı progress updates, incremental result streaming ve async background processing.
            </p>
          </div>

          {/* Feature 5 */}
          <div className="group bg-white rounded-2xl p-6 border border-gray-200 hover:border-blue-300 hover:shadow-xl transition-all">
            <div className="w-12 h-12 bg-gradient-to-br from-yellow-500 to-amber-600 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform shadow-lg shadow-yellow-500/30">
              <BarChart3 className="w-6 h-6 text-white" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Performans Analizi</h3>
            <p className="text-gray-600 leading-relaxed">
              Güçlü ve zayıf yönler, topic gaps identification ve comparative analytics.
            </p>
          </div>

          {/* Feature 6 */}
          <div className="group bg-white rounded-2xl p-6 border border-gray-200 hover:border-blue-300 hover:shadow-xl transition-all">
            <div className="w-12 h-12 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform shadow-lg shadow-cyan-500/30">
              <Lightbulb className="w-6 h-6 text-white" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Follow-up Q&A</h3>
            <p className="text-gray-600 leading-relaxed">
              Öğrenci performansı hakkında context-aware chat, chat history ve multi-turn conversations.
            </p>
          </div>
        </div>
      </section>

      {/* Tech Stack */}
      <section className="max-w-7xl mx-auto px-6 py-16">
        <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-3xl p-12 text-white relative overflow-hidden">
          <div className="absolute top-0 right-0 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl"></div>
          <div className="absolute bottom-0 left-0 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl"></div>

          <div className="relative">
            <div className="text-center mb-12">
              <h2 className="text-4xl font-bold mb-4">Modern Tech Stack</h2>
              <p className="text-gray-300 text-lg">Production-ready architecture ile güçlendirilmiş</p>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <div className="text-center">
                <div className="w-16 h-16 bg-white/10 backdrop-blur-sm rounded-xl flex items-center justify-center mx-auto mb-3">
                  <Terminal className="w-8 h-8 text-blue-400" />
                </div>
                <p className="font-semibold">FastAPI</p>
                <p className="text-sm text-gray-400">Backend</p>
              </div>

              <div className="text-center">
                <div className="w-16 h-16 bg-white/10 backdrop-blur-sm rounded-xl flex items-center justify-center mx-auto mb-3">
                  <Brain className="w-8 h-8 text-purple-400" />
                </div>
                <p className="font-semibold">LangGraph</p>
                <p className="text-sm text-gray-400">Agentic AI</p>
              </div>

              <div className="text-center">
                <div className="w-16 h-16 bg-white/10 backdrop-blur-sm rounded-xl flex items-center justify-center mx-auto mb-3">
                  <Sparkles className="w-8 h-8 text-yellow-400" />
                </div>
                <p className="font-semibold">Gemini 2.0</p>
                <p className="text-sm text-gray-400">LLM</p>
              </div>

              <div className="text-center">
                <div className="w-16 h-16 bg-white/10 backdrop-blur-sm rounded-xl flex items-center justify-center mx-auto mb-3">
                  <Terminal className="w-8 h-8 text-green-400" />
                </div>
                <p className="font-semibold">Next.js 15</p>
                <p className="text-sm text-gray-400">Frontend</p>
              </div>

              <div className="text-center">
                <div className="w-16 h-16 bg-white/10 backdrop-blur-sm rounded-xl flex items-center justify-center mx-auto mb-3">
                  <Shield className="w-8 h-8 text-red-400" />
                </div>
                <p className="font-semibold">PostgreSQL</p>
                <p className="text-sm text-gray-400">Database</p>
              </div>

              <div className="text-center">
                <div className="w-16 h-16 bg-white/10 backdrop-blur-sm rounded-xl flex items-center justify-center mx-auto mb-3">
                  <Zap className="w-8 h-8 text-orange-400" />
                </div>
                <p className="font-semibold">Redis</p>
                <p className="text-sm text-gray-400">Cache</p>
              </div>

              <div className="text-center">
                <div className="w-16 h-16 bg-white/10 backdrop-blur-sm rounded-xl flex items-center justify-center mx-auto mb-3">
                  <Clock className="w-8 h-8 text-cyan-400" />
                </div>
                <p className="font-semibold">Celery</p>
                <p className="text-sm text-gray-400">Task Queue</p>
              </div>

              <div className="text-center">
                <div className="w-16 h-16 bg-white/10 backdrop-blur-sm rounded-xl flex items-center justify-center mx-auto mb-3">
                  <Users className="w-8 h-8 text-indigo-400" />
                </div>
                <p className="font-semibold">RabbitMQ</p>
                <p className="text-sm text-gray-400">Message Broker</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="max-w-7xl mx-auto px-6 py-20">
        <div className="bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 rounded-3xl p-12 text-center text-white relative overflow-hidden">
          <div className="absolute top-0 right-0 w-96 h-96 bg-white/10 rounded-full blur-3xl"></div>
          <div className="absolute bottom-0 left-0 w-96 h-96 bg-white/5 rounded-full blur-3xl"></div>

          <div className="relative">
            <h2 className="text-4xl font-bold mb-4">Hemen Başlayın</h2>
            <p className="text-blue-100 text-lg mb-8 max-w-2xl mx-auto">
              Demo hesabı ile sistemi test edin. Tüm özellikler kullanıma hazır.
            </p>
            <Link
              href="/login"
              className="inline-flex items-center gap-3 px-8 py-4 bg-white text-blue-600 rounded-xl font-semibold text-lg hover:bg-gray-50 shadow-2xl hover:scale-105 transition-all"
            >
              <span>Demo ile Giriş Yap</span>
              <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-100 bg-gray-50">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
                <Terminal className="w-4 h-4 text-white" />
              </div>
              <div>
                <p className="font-semibold text-gray-900">Exam Evaluator</p>
                <p className="text-xs text-gray-500">v1.0.0 • Built with ❤️ and 🤖 AI</p>
              </div>
            </div>
            <div className="text-sm text-gray-600">
              © 2025 • LangGraph + Gemini 2.0 Flash
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
