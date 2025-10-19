'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import DashboardLayout from '@/components/DashboardLayout';
import {
  ArrowLeft, CheckCircle2, XCircle, AlertCircle,
  MessageSquare, Send, X, Loader2, FileText, Award, Target, TrendingUp, AlertTriangle, Sparkles
} from 'lucide-react';
import Link from 'next/link';
import { examApi, StudentDetailResponse } from '@/lib/api';
import { useAuthStore } from '@/lib/store';

export default function StudentResultPage() {
  const params = useParams();
  const router = useRouter();
  const examId = params.id as string;
  const studentId = parseInt(params.studentId as string);
  const { token, _hasHydrated } = useAuthStore();

  const [student, setStudent] = useState<StudentDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [chatMessages, setChatMessages] = useState<Array<{ role: 'user' | 'ai', message: string }>>([
    {
      role: 'ai',
      message: 'Merhaba! Ben AI asistanınızım. Bu öğrencinin performansı, belirli sorular veya nasıl gelişebileceği hakkında her şeyi sorabilirsiniz.'
    }
  ]);
  const [newMessage, setNewMessage] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(true);

  // Load chat history from localStorage on mount
  useEffect(() => {
    const chatKey = `chat_history_${studentId}`;
    const savedChat = localStorage.getItem(chatKey);
    if (savedChat) {
      try {
        const parsed = JSON.parse(savedChat);
        if (Array.isArray(parsed) && parsed.length > 0) {
          setChatMessages(parsed);
          console.log('💬 Loaded chat history from localStorage:', parsed.length, 'messages');
        }
      } catch (e) {
        console.error('❌ Failed to parse saved chat:', e);
      }
    }
  }, [studentId.toString()]);

  // Save chat history to localStorage whenever it changes
  useEffect(() => {
    if (chatMessages.length > 1) {
      const chatKey = `chat_history_${studentId}`;
      localStorage.setItem(chatKey, JSON.stringify(chatMessages));
      console.log('💾 Saved chat history to localStorage:', chatMessages.length, 'messages');
    }
  }, [chatMessages, studentId.toString()]);

  useEffect(() => {
    console.log('🔍 Student detail page mounted:', { examId, studentId, hasToken: !!token, hasHydrated: _hasHydrated });
    if (_hasHydrated && token && studentId) {
      fetchStudentDetail();
    }
  }, [studentId, token, _hasHydrated]);

  // Auto-refresh if student is still being processed
  useEffect(() => {
    if (!student) return;

    const isProcessing = student.total_score === 0 && student.questions.some(q => q.feedback === "Pending evaluation");

    if (isProcessing && token && _hasHydrated) {
      console.log('⏳ Student is processing, setting up silent auto-refresh...');
      const interval = setInterval(() => {
        console.log('🔄 Silent refresh for processing student...');
        fetchStudentDetail();
      }, 5000);

      return () => clearInterval(interval);
    }
  }, [student, token, _hasHydrated]);

  const fetchStudentDetail = async () => {
    try {
      const response = await examApi.getStudentDetail(token!, studentId);
      setStudent(response);
      setError(null);
    } catch (err: any) {
      console.error('Error fetching student detail:', err);
      setError(err.message || 'Bir hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newMessage.trim() || chatLoading) return;

    const userMessage = newMessage.trim();
    setNewMessage('');

    // Add user message
    setChatMessages((prev) => [...prev, { role: 'user', message: userMessage }]);
    setChatLoading(true);

    try {
      // Build chat history for API
      const history = chatMessages.slice(1).map((msg) => ({
        role: msg.role === 'user' ? 'user' : 'assistant',
        content: msg.message,
      }));

      const response = await examApi.chatAboutStudent(
        token!,
        studentId,
        userMessage,
        history
      );

      // Add AI response
      setChatMessages((prev) => [
        ...prev,
        {
          role: 'ai',
          message: response.answer
        }
      ]);
    } catch (err: any) {
      console.error('Chat error:', err);
      setChatMessages((prev) => [
        ...prev,
        {
          role: 'ai',
          message: 'Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.'
        }
      ]);
    } finally {
      setChatLoading(false);
    }
  };

  const clearChatHistory = () => {
    const chatKey = `chat_history_${studentId}`;
    localStorage.removeItem(chatKey);
    setChatMessages([
      {
        role: 'ai',
        message: 'Merhaba! Ben AI asistanınızım. Bu öğrencinin performansı, belirli sorular veya nasıl gelişebileceği hakkında her şeyi sorabilirsiniz.'
      }
    ]);
    console.log('🗑️ Chat history cleared');
  };

  const getScoreColor = (percentage: number) => {
    if (percentage >= 80) return 'text-emerald-600';
    if (percentage >= 60) return 'text-amber-600';
    return 'text-rose-600';
  };

  const getScoreBg = (percentage: number) => {
    if (percentage >= 80) return 'bg-emerald-500';
    if (percentage >= 60) return 'bg-amber-500';
    return 'bg-rose-500';
  };

  const getScoreGrade = (percentage: number) => {
    if (percentage >= 90) return 'A+';
    if (percentage >= 85) return 'A';
    if (percentage >= 80) return 'A-';
    if (percentage >= 75) return 'B+';
    if (percentage >= 70) return 'B';
    if (percentage >= 65) return 'B-';
    if (percentage >= 60) return 'C+';
    if (percentage >= 55) return 'C';
    if (percentage >= 50) return 'C-';
    if (percentage >= 40) return 'D';
    return 'F';
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="relative">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl mx-auto mb-6 flex items-center justify-center shadow-lg">
                <Loader2 className="w-8 h-8 text-white animate-spin" />
              </div>
              <div className="absolute inset-0 w-16 h-16 bg-blue-400 rounded-2xl mx-auto animate-ping opacity-20"></div>
            </div>
            <p className="text-lg font-medium text-gray-700">Sonuçlar yükleniyor...</p>
            <p className="text-sm text-gray-500 mt-2">Lütfen bekleyin</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (error || !student) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-screen px-4">
          <div className="text-center max-w-md">
            <div className="w-20 h-20 bg-rose-100 rounded-3xl mx-auto mb-6 flex items-center justify-center">
              <AlertCircle className="w-10 h-10 text-rose-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-3">Sonuçlar Yüklenemedi</h2>
            <p className="text-gray-600 mb-8">{error}</p>
            <div className="flex items-center justify-center gap-3">
              <button
                onClick={() => {
                  setError(null);
                  setLoading(true);
                  fetchStudentDetail();
                }}
                className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 transition-all shadow-lg shadow-blue-500/30 font-medium"
              >
                <Loader2 className="w-5 h-5" />
                Tekrar Dene
              </button>
              <Link
                href={`/dashboard/exams/${examId}`}
                className="inline-flex items-center gap-2 px-6 py-3 bg-gray-100 text-gray-700 rounded-xl hover:bg-gray-200 transition-all font-medium"
              >
                <ArrowLeft className="w-5 h-5" />
                Sınava Dön
              </Link>
            </div>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  const correctCount = student.questions.filter(q => q.is_correct).length;
  const totalQuestions = student.questions.length;

  // Check if student is still being evaluated
  const isProcessing = student.total_score === 0 && (
    student.questions.some(q => q.feedback === "Pending evaluation") ||
    student.questions.some(q => q.feedback === "Değerlendirme bekleniyor...") ||
    student.questions.some(q => q.student_answer === "[Cevap çıkarılıyor...]")
  );

  const evaluatedCount = student.questions.filter(q =>
    q.feedback !== "Pending evaluation" &&
    q.feedback !== "Değerlendirme bekleniyor..." &&
    q.student_answer !== "[Cevap çıkarılıyor...]"
  ).length;

  return (
    <DashboardLayout>
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

        {/* Header */}
        <div className="mb-8">
          <Link
            href={`/dashboard/exams/${examId}`}
            className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors mb-6 group"
          >
            <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
            <span className="font-medium">Sınava Dön</span>
          </Link>

          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{student.student_name}</h1>
              <p className="text-gray-500">Sınav Sonuç Detayı</p>
            </div>
          </div>
        </div>

        {/* Processing Banner */}
        {isProcessing && (
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-2xl p-6 mb-8">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center flex-shrink-0 shadow-lg shadow-blue-500/30">
                <Loader2 className="w-6 h-6 text-white animate-spin" />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <h3 className="font-bold text-blue-900 text-lg">AI Değerlendirme Devam Ediyor</h3>
                  <span className="px-2.5 py-0.5 bg-blue-500 text-white text-xs rounded-full font-semibold animate-pulse">
                    CANLI
                  </span>
                </div>
                <p className="text-blue-800 mb-4">
                  <span className="font-semibold">{evaluatedCount}/{totalQuestions}</span> soru değerlendirildi
                </p>

                <div className="mb-2">
                  <div className="flex items-center justify-between text-xs text-blue-700 mb-1.5">
                    <span className="font-medium">İlerleme</span>
                    <span className="font-bold">{Math.round((evaluatedCount / totalQuestions) * 100)}%</span>
                  </div>
                  <div className="w-full bg-blue-200 rounded-full h-2 overflow-hidden">
                    <div
                      className="bg-gradient-to-r from-blue-500 to-indigo-600 h-2 rounded-full transition-all duration-700 ease-out"
                      style={{ width: `${(evaluatedCount / totalQuestions) * 100}%` }}
                    />
                  </div>
                </div>

                <p className="text-xs text-blue-600 mt-3">
                  ⚡ Sayfa otomatik olarak güncelleniyor...
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Score Card */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">

            {/* Total Score */}
            <div className="md:col-span-2">
              <div className="flex items-center gap-4">
                <div className={`w-20 h-20 ${getScoreBg(student.percentage)} rounded-2xl flex items-center justify-center shadow-lg`}>
                  <Award className="w-10 h-10 text-white" />
                </div>
                <div>
                  <p className="text-sm text-gray-500 mb-1">Toplam Puan</p>
                  <div className="flex items-baseline gap-3">
                    <span className={`text-4xl font-bold ${getScoreColor(student.percentage)}`}>
                      {student.total_score.toFixed(1)}
                    </span>
                    <span className="text-xl text-gray-400">/ {student.max_score}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Percentage */}
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center shadow-lg shadow-purple-500/30">
                <Sparkles className="w-8 h-8 text-white" />
              </div>
              <div>
                <p className="text-sm text-gray-500 mb-1">Yüzde</p>
                <p className={`text-3xl font-bold ${getScoreColor(student.percentage)}`}>
                  %{student.percentage.toFixed(1)}
                </p>
              </div>
            </div>

            {/* Grade */}
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 bg-gradient-to-br from-amber-500 to-orange-600 rounded-xl flex items-center justify-center shadow-lg shadow-amber-500/30">
                <Target className="w-8 h-8 text-white" />
              </div>
              <div>
                <p className="text-sm text-gray-500 mb-1">Harf Notu</p>
                <p className="text-3xl font-bold text-gray-900">
                  {getScoreGrade(student.percentage)}
                </p>
              </div>
            </div>

          </div>
        </div>

        {/* Performance Analysis */}
        {(student.strengths && student.strengths.length > 0) || (student.weaknesses && student.weaknesses.length > 0) ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">

            {/* Strengths */}
            {student.strengths && student.strengths.length > 0 && (
              <div className="bg-gradient-to-br from-emerald-50 to-teal-50 border border-emerald-200 rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-lg flex items-center justify-center shadow-lg shadow-emerald-500/30">
                    <TrendingUp className="w-5 h-5 text-white" />
                  </div>
                  <h3 className="font-bold text-emerald-900 text-lg">Güçlü Yönler</h3>
                </div>
                <ul className="space-y-2.5">
                  {student.strengths.map((strength, idx) => (
                    <li key={idx} className="flex items-start gap-2.5">
                      <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0 mt-0.5" />
                      <span className="text-emerald-900 leading-relaxed">{strength}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Weaknesses */}
            {student.weaknesses && student.weaknesses.length > 0 && (
              <div className="bg-gradient-to-br from-rose-50 to-pink-50 border border-rose-200 rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-gradient-to-br from-rose-500 to-pink-600 rounded-lg flex items-center justify-center shadow-lg shadow-rose-500/30">
                    <AlertTriangle className="w-5 h-5 text-white" />
                  </div>
                  <h3 className="font-bold text-rose-900 text-lg">Gelişim Alanları</h3>
                </div>
                <ul className="space-y-2.5">
                  {student.weaknesses.map((weakness, idx) => (
                    <li key={idx} className="flex items-start gap-2.5">
                      <XCircle className="w-5 h-5 text-rose-600 flex-shrink-0 mt-0.5" />
                      <span className="text-rose-900 leading-relaxed">{weakness}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

          </div>
        ) : null}

        {/* Questions */}
        <div className="space-y-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center shadow-lg shadow-blue-500/30">
              <FileText className="w-5 h-5 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900">Soru Bazlı Değerlendirme</h2>
          </div>

          {student.questions.map((q) => {
            const isExtractingAnswer = q.student_answer === "[Cevap çıkarılıyor...]";
            const isPending = q.feedback === "Pending evaluation" || q.feedback === "Değerlendirme bekleniyor...";
            const percentage = isPending ? 0 : (q.score / q.max_score) * 100;
            const isCorrect = !isPending && percentage >= 70;
            const isPartial = !isPending && percentage >= 50 && percentage < 70;

            return (
              <div key={q.question_number} className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow duration-300">

                {/* Question Header */}
                <div className={`px-6 py-4 flex items-center justify-between border-b ${
                  isExtractingAnswer ? 'bg-blue-50 border-blue-200' :
                  isPending ? 'bg-amber-50 border-amber-200' :
                  isCorrect ? 'bg-emerald-50 border-emerald-200' :
                  isPartial ? 'bg-amber-50 border-amber-200' :
                  'bg-rose-50 border-rose-200'
                }`}>
                  <div className="flex items-center gap-4">
                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center font-bold text-lg shadow-sm ${
                      isExtractingAnswer ? 'bg-blue-500 text-white' :
                      isPending ? 'bg-amber-500 text-white' :
                      isCorrect ? 'bg-emerald-500 text-white' :
                      isPartial ? 'bg-amber-500 text-white' :
                      'bg-rose-500 text-white'
                    }`}>
                      {q.question_number}
                    </div>
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-semibold text-gray-900">Soru {q.question_number}</span>
                        {!isExtractingAnswer && !isPending && (
                          <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                            isCorrect ? 'bg-emerald-100 text-emerald-700' :
                            isPartial ? 'bg-amber-100 text-amber-700' :
                            'bg-rose-100 text-rose-700'
                          }`}>
                            {isCorrect ? '✓ Doğru' : isPartial ? '◐ Kısmen' : '✗ Yanlış'}
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-600">Maksimum {q.max_score} puan</p>
                    </div>
                  </div>
                  <div className="text-right">
                    {isExtractingAnswer || isPending ? (
                      <div className="px-4 py-2 bg-white/80 rounded-lg border border-gray-200">
                        <Loader2 className="w-5 h-5 text-gray-600 animate-spin" />
                      </div>
                    ) : (
                      <>
                        <div className={`text-3xl font-bold ${
                          isCorrect ? 'text-emerald-600' :
                          isPartial ? 'text-amber-600' :
                          'text-rose-600'
                        }`}>
                          {q.score.toFixed(1)}
                        </div>
                        <div className="text-sm text-gray-500">/ {q.max_score}</div>
                      </>
                    )}
                  </div>
                </div>

                {/* Question Content */}
                <div className="p-6 space-y-5">

                  {/* Question Text */}
                  {q.question_text && (
                    <div>
                      <div className="flex items-center gap-2 mb-2">
                        <FileText className="w-4 h-4 text-gray-500" />
                        <h4 className="text-sm font-semibold text-gray-700">Soru:</h4>
                      </div>
                      <p className="text-gray-800 leading-relaxed bg-gray-50 p-4 rounded-xl border border-gray-200">
                        {q.question_text}
                      </p>
                    </div>
                  )}

                  {/* Expected Answer */}
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                      <h4 className="text-sm font-semibold text-emerald-700">Beklenen Cevap:</h4>
                    </div>
                    <p className="text-gray-800 leading-relaxed bg-emerald-50/50 p-4 rounded-xl border border-emerald-100">
                      {q.expected_answer}
                    </p>
                  </div>

                  {/* Student Answer */}
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <FileText className="w-4 h-4 text-blue-600" />
                      <h4 className="text-sm font-semibold text-blue-700">Öğrenci Cevabı:</h4>
                    </div>
                    {isExtractingAnswer ? (
                      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-5">
                        <div className="flex items-start gap-4">
                          <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center flex-shrink-0 shadow-sm">
                            <Loader2 className="w-5 h-5 text-white animate-spin" />
                          </div>
                          <div className="flex-1">
                            <h4 className="font-bold text-blue-900 mb-1">📄 PDF Okunuyor</h4>
                            <p className="text-blue-800 text-sm">
                              Öğrencinin bu soruya verdiği cevap PDF'den çıkarılıyor...
                            </p>
                          </div>
                        </div>
                      </div>
                    ) : q.student_answer === "[No answer provided]" || !q.student_answer ? (
                      <div className="text-gray-500 italic bg-gray-100 p-4 rounded-xl border border-gray-300">
                        Cevap bulunamadı veya boş bırakılmış
                      </div>
                    ) : (
                      <p className="text-gray-800 leading-relaxed bg-blue-50/50 p-4 rounded-xl border border-blue-100">
                        {q.student_answer}
                      </p>
                    )}
                  </div>

                  {/* AI Feedback */}
                  <div>
                    {isPending ? (
                      <div className="bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200 rounded-xl p-5">
                        <div className="flex items-start gap-4">
                          <div className="w-12 h-12 bg-gradient-to-br from-amber-500 to-orange-600 rounded-xl flex items-center justify-center flex-shrink-0 shadow-lg shadow-amber-500/30">
                            <Loader2 className="w-6 h-6 text-white animate-spin" />
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <h4 className="font-bold text-amber-900">🤖 AI Değerlendirme Yapılıyor</h4>
                              <span className="px-2 py-0.5 bg-amber-200 text-amber-800 text-xs rounded-full font-semibold animate-pulse">
                                İŞLENİYOR
                              </span>
                            </div>
                            <p className="text-amber-800 text-sm">
                              Bu soru şu anda yapay zeka tarafından analiz ediliyor.
                            </p>
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className={`bg-gradient-to-br ${
                        isCorrect ? 'from-emerald-50 to-teal-50 border-emerald-200' :
                        isPartial ? 'from-amber-50 to-orange-50 border-amber-200' :
                        'from-rose-50 to-pink-50 border-rose-200'
                      } border rounded-xl p-5`}>
                        <div className="flex items-start gap-4">
                          {/* AI Icon */}
                          <div className={`w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 shadow-lg ${
                            isCorrect ? 'bg-gradient-to-br from-emerald-500 to-teal-600 shadow-emerald-500/30' :
                            isPartial ? 'bg-gradient-to-br from-amber-500 to-orange-600 shadow-amber-500/30' :
                            'bg-gradient-to-br from-rose-500 to-pink-600 shadow-rose-500/30'
                          }`}>
                            <MessageSquare className="w-6 h-6 text-white" />
                          </div>

                          <div className="flex-1">
                            {/* Header */}
                            <div className="flex items-center justify-between mb-3">
                              <div className="flex items-center gap-2">
                                <h4 className={`font-bold text-lg ${
                                  isCorrect ? 'text-emerald-900' :
                                  isPartial ? 'text-amber-900' :
                                  'text-rose-900'
                                }`}>
                                  🤖 AI Geri Bildirimi
                                </h4>
                              </div>

                              {/* Confidence Score */}
                              {q.confidence !== undefined && q.confidence !== null && (
                                <div className="flex items-center gap-1.5 bg-white/80 px-3 py-1.5 rounded-lg shadow-sm border border-gray-200">
                                  <div className="text-xs font-semibold text-gray-600">Güven:</div>
                                  <div className={`text-sm font-bold ${
                                    q.confidence >= 0.8 ? 'text-emerald-600' :
                                    q.confidence >= 0.6 ? 'text-amber-600' :
                                    'text-rose-600'
                                  }`}>
                                    {(q.confidence * 100).toFixed(0)}%
                                  </div>
                                </div>
                              )}
                            </div>

                            {/* Feedback Content */}
                            <div className="bg-white/80 backdrop-blur-sm p-4 rounded-lg border border-white/50 shadow-sm">
                              <p className={`leading-relaxed whitespace-pre-wrap ${
                                isCorrect ? 'text-emerald-900' :
                                isPartial ? 'text-amber-900' :
                                'text-rose-900'
                              }`}>
                                {q.feedback}
                              </p>
                            </div>

                            {/* Reasoning */}
                            {q.reasoning && (
                              <div className="mt-3 bg-white/60 backdrop-blur-sm p-3 rounded-lg border border-white/50">
                                <div className="flex items-center gap-2 mb-1.5">
                                  <div className="w-1.5 h-1.5 bg-gray-400 rounded-full"></div>
                                  <span className="text-xs font-semibold text-gray-600 uppercase tracking-wide">
                                    Değerlendirme Mantığı
                                  </span>
                                </div>
                                <p className="text-sm text-gray-700 leading-relaxed italic">
                                  {q.reasoning}
                                </p>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Floating Chat Button */}
      <button
        onClick={() => setIsChatOpen(!isChatOpen)}
        className="fixed bottom-6 right-6 w-14 h-14 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-full shadow-xl hover:shadow-2xl hover:scale-110 transition-all flex items-center justify-center z-50"
      >
        {isChatOpen ? <X className="w-6 h-6" /> : <MessageSquare className="w-6 h-6" />}
      </button>

      {/* Chat Window */}
      {isChatOpen && (
        <div className="fixed bottom-24 right-6 w-96 h-[600px] bg-white rounded-2xl shadow-2xl border border-gray-200 flex flex-col z-50 animate-in slide-in-from-bottom-5 duration-300">

          {/* Chat Header */}
          <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-t-2xl flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
                <h3 className="font-bold text-gray-900">AI Asistan</h3>
              </div>
              <p className="text-sm text-gray-600">Performans hakkında soru sorun</p>
            </div>
            {chatMessages.length > 1 && (
              <button
                onClick={clearChatHistory}
                className="text-gray-500 hover:text-rose-600 transition flex items-center gap-1 text-xs bg-white px-2 py-1 rounded-lg hover:bg-rose-50 border border-gray-200 ml-2"
                title="Sohbet geçmişini temizle"
              >
                <X className="w-3 h-3" />
                Temizle
              </button>
            )}
          </div>

          {/* Chat Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
            {chatMessages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] px-4 py-3 rounded-2xl shadow-sm ${
                    msg.role === 'user'
                      ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-br-none'
                      : 'bg-white text-gray-900 rounded-bl-none border border-gray-200'
                  }`}
                >
                  <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.message}</p>
                </div>
              </div>
            ))}
            {chatLoading && (
              <div className="flex justify-start">
                <div className="bg-white px-4 py-3 rounded-2xl rounded-bl-none border border-gray-200 shadow-sm">
                  <Loader2 className="w-5 h-5 text-gray-600 animate-spin" />
                </div>
              </div>
            )}
          </div>

          {/* Chat Input */}
          <form onSubmit={handleSendMessage} className="p-4 border-t border-gray-200 bg-white rounded-b-2xl">
            <div className="flex gap-2">
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder="Bir soru sorun..."
                className="flex-1 px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-400 transition-all"
                disabled={chatLoading}
              />
              <button
                type="submit"
                disabled={!newMessage.trim() || chatLoading}
                className="px-4 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-blue-500/30"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
          </form>
        </div>
      )}
    </DashboardLayout>
  );
}
