'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import DashboardLayout from '@/components/DashboardLayout';
import {
  ArrowLeft, CheckCircle2, XCircle, AlertCircle,
  MessageSquare, Send, X, Loader2, FileText, Award, Target, TrendingUp, AlertTriangle
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
  const [isChatOpen, setIsChatOpen] = useState(false);

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
        console.log('🔄 Silent auto-refresh...');
        // Silent refresh - don't show loading state
        examApi.getStudentDetail(token, studentId)
          .then(data => setStudent(data))
          .catch(err => console.error('Silent refresh error:', err));
      }, 5000); // Refresh every 5 seconds

      return () => {
        console.log('🛑 Clearing auto-refresh interval');
        clearInterval(interval);
      };
    }
  }, [student, token, _hasHydrated]);

  const fetchStudentDetail = async () => {
    console.log('📡 Fetching student detail for ID:', studentId);

    // Wait for hydration before checking token
    if (!_hasHydrated) {
      return;
    }

    if (!token) {
      console.error('❌ No token found, redirecting to login');
      router.push('/login');
      return;
    }

    try {
      console.log('🚀 Calling examApi.getStudentDetail...');
      const data = await examApi.getStudentDetail(token, studentId);
      console.log('✅ Student detail received:', data);
      setStudent(data);
      setError(null);
    } catch (err: any) {
      console.error('❌ Error fetching student detail:', err);
      setError(err.message || 'Öğrenci detayları yüklenirken bir hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newMessage.trim() || chatLoading || !token) return;

    const userMessage = newMessage.trim();

    // Add user message immediately
    setChatMessages((prev) => [...prev, { role: 'user', message: userMessage }]);
    setNewMessage('');
    setChatLoading(true);

    try {
      // Prepare chat history for API (convert to required format)
      const historyForAPI = chatMessages.map(msg => ({
        role: msg.role === 'user' ? 'user' : 'assistant',
        content: msg.message
      }));

      // Call API
      const response = await examApi.chatAboutStudent(
        token,
        studentId,
        userMessage,
        historyForAPI
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
      // Add error message
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

  const getScoreColor = (percentage: number) => {
    if (percentage >= 80) return 'text-emerald-600';
    if (percentage >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBg = (percentage: number) => {
    if (percentage >= 80) return 'bg-emerald-500';
    if (percentage >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
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
            <Loader2 className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-4" />
            <p className="text-gray-600">Sonuçlar yükleniyor...</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (error || !student) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center max-w-md">
            <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Sonuçlar Yüklenemedi</h2>
            <p className="text-gray-600 mb-6">{error}</p>
            <div className="flex items-center justify-center gap-4">
              <button
                onClick={() => {
                  setError(null);
                  setLoading(true);
                  fetchStudentDetail();
                }}
                className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
              >
                <Loader2 className="w-5 h-5" />
                Tekrar Dene
              </button>
              <Link
                href={`/dashboard/exams/${examId}`}
                className="inline-flex items-center gap-2 px-6 py-3 bg-gray-200 text-gray-900 rounded-lg hover:bg-gray-300 transition"
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
      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Processing Banner */}
        {isProcessing && (
          <div className="bg-gradient-to-r from-blue-50 via-indigo-50 to-purple-50 border-2 border-blue-300 rounded-xl p-6 mb-6 shadow-lg">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 bg-blue-500 rounded-xl flex items-center justify-center flex-shrink-0 shadow-md">
                <Loader2 className="w-6 h-6 text-white animate-spin" />
              </div>
              <div className="flex-1">
                <h3 className="font-bold text-blue-900 text-lg mb-2 flex items-center gap-2">
                  ⚡ AI Değerlendirme Devam Ediyor
                  <span className="px-2 py-1 bg-blue-200 text-blue-700 text-xs rounded-full font-semibold">
                    CANLI
                  </span>
                </h3>
                <p className="text-blue-800 mb-3">
                  <strong>{evaluatedCount}/{totalQuestions}</strong> soru değerlendirildi.
                  Geriye <strong>{totalQuestions - evaluatedCount}</strong> soru kaldı.
                </p>

                {/* Progress Bar */}
                <div className="mb-3">
                  <div className="flex items-center justify-between text-xs text-blue-700 mb-1">
                    <span>İlerleme</span>
                    <span className="font-bold">{Math.round((evaluatedCount / totalQuestions) * 100)}%</span>
                  </div>
                  <div className="w-full bg-blue-200 rounded-full h-2.5 overflow-hidden">
                    <div
                      className="bg-gradient-to-r from-blue-500 to-indigo-600 h-2.5 rounded-full transition-all duration-500"
                      style={{ width: `${(evaluatedCount / totalQuestions) * 100}%` }}
                    ></div>
                  </div>
                </div>

                <div className="flex items-center gap-2 text-blue-700 text-sm bg-white/60 rounded-lg p-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                  <span>Sayfa her 5 saniyede otomatik güncelleniyor</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Back Button */}
        <Link
          href={`/dashboard/exams/${examId}`}
          className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 transition mb-6"
        >
          <ArrowLeft className="w-5 h-5" />
          <span className="font-medium">Sınava Dön</span>
        </Link>

        {/* Student Header Card */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-8 mb-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
            {/* Student Info */}
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
                <span className="text-2xl font-bold text-white">
                  {student.student_name.charAt(0).toUpperCase()}
                </span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">{student.student_name}</h1>
                <p className="text-gray-600 mt-1">Detaylı Değerlendirme Sonuçları</p>
              </div>
            </div>

            {/* Score Display */}
            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="text-sm text-gray-600 mb-1">Toplam Puan</div>
                <div className="text-3xl font-bold text-gray-900">
                  {student.total_score.toFixed(1)}<span className="text-xl text-gray-500">/{student.max_score}</span>
                </div>
              </div>
              <div className={`w-24 h-24 rounded-full ${getScoreBg(student.percentage)} flex items-center justify-center`}>
                <div className="text-center">
                  <div className="text-2xl font-bold text-white">{student.percentage.toFixed(0)}%</div>
                  <div className="text-sm text-white/90">{getScoreGrade(student.percentage)}</div>
                </div>
              </div>
            </div>
          </div>

          {/* Stats Row */}
          <div className="grid grid-cols-3 gap-4 mt-6 pt-6 border-t border-gray-200">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{totalQuestions}</div>
              <div className="text-sm text-gray-600">Toplam Soru</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-emerald-600">{correctCount}</div>
              <div className="text-sm text-gray-600">Doğru</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">{totalQuestions - correctCount}</div>
              <div className="text-sm text-gray-600">Yanlış</div>
            </div>
          </div>
        </div>

        {/* Performance Summary */}
        {student.summary && (
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-6 mb-6">
            <div className="flex items-start gap-3">
              <Award className="w-6 h-6 text-blue-600 flex-shrink-0 mt-1" />
              <div>
                <h3 className="font-bold text-blue-900 mb-2">Performans Özeti</h3>
                <p className="text-blue-800 leading-relaxed">{student.summary}</p>
              </div>
            </div>
          </div>
        )}

        {/* Strengths and Weaknesses Grid */}
        {((student.strengths && student.strengths.length > 0) || (student.weaknesses && student.weaknesses.length > 0)) && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            {/* Strengths */}
            {student.strengths && student.strengths.length > 0 && (
              <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-emerald-600 rounded-lg flex items-center justify-center">
                    <TrendingUp className="w-5 h-5 text-white" />
                  </div>
                  <h3 className="font-bold text-emerald-900 text-lg">Güçlü Yönler</h3>
                </div>
                <ul className="space-y-2">
                  {student.strengths.map((strength, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0 mt-0.5" />
                      <span className="text-emerald-900 leading-relaxed">{strength}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Weaknesses */}
            {student.weaknesses && student.weaknesses.length > 0 && (
              <div className="bg-red-50 border border-red-200 rounded-xl p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-red-600 rounded-lg flex items-center justify-center">
                    <AlertTriangle className="w-5 h-5 text-white" />
                  </div>
                  <h3 className="font-bold text-red-900 text-lg">Zayıf Yönler</h3>
                </div>
                <ul className="space-y-2">
                  {student.weaknesses.map((weakness, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <XCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                      <span className="text-red-900 leading-relaxed">{weakness}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Topic Gaps */}
        {student.topic_gaps && student.topic_gaps.length > 0 && (
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-6 mb-6">
            <div className="flex items-start gap-3">
              <Target className="w-6 h-6 text-amber-600 flex-shrink-0 mt-1" />
              <div className="flex-1">
                <h3 className="font-bold text-amber-900 mb-3">Geliştirilmesi Gereken Konular</h3>
                <div className="flex flex-wrap gap-2">
                  {student.topic_gaps.map((topic, idx) => (
                    <span
                      key={idx}
                      className="px-4 py-2 bg-white border border-amber-300 text-amber-900 text-sm font-medium rounded-lg"
                    >
                      {topic}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Questions */}
        <div className="space-y-4">
          <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
            <FileText className="w-6 h-6" />
            Soru Bazlı Değerlendirme
          </h2>

          {student.questions.map((q) => {
            const isExtractingAnswer = q.student_answer === "[Cevap çıkarılıyor...]";
            const isPending = q.feedback === "Pending evaluation" || q.feedback === "Değerlendirme bekleniyor...";
            const percentage = isPending ? 0 : (q.score / q.max_score) * 100;
            const isCorrect = !isPending && percentage >= 80;
            const isPartial = !isPending && percentage >= 50 && percentage < 80;

            return (
              <div key={q.question_number} className={`bg-white rounded-xl shadow-sm border-2 overflow-hidden hover:shadow-md transition ${
                isExtractingAnswer ? 'border-blue-300 opacity-80' : isPending ? 'border-gray-300 opacity-60' : 'border-gray-200'
              }`}>
                {/* Question Header */}
                <div className={`px-6 py-4 flex items-center justify-between ${
                  isExtractingAnswer ? 'bg-blue-50' :
                  isPending ? 'bg-gray-50' :
                  isCorrect ? 'bg-emerald-50' :
                  isPartial ? 'bg-yellow-50' :
                  'bg-red-50'
                }`}>
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                      isExtractingAnswer ? 'bg-blue-200 text-blue-900' :
                      isPending ? 'bg-gray-200 text-gray-600' :
                      isCorrect ? 'bg-emerald-200 text-emerald-900' :
                      isPartial ? 'bg-yellow-200 text-yellow-900' :
                      'bg-red-200 text-red-900'
                    }`}>
                      {q.question_number}
                    </div>
                    <div>
                      <h3 className="font-bold text-gray-900">Soru {q.question_number}</h3>
                      <div className="flex items-center gap-2 mt-1">
                        {isExtractingAnswer ? (
                          <>
                            <div className="px-2 py-1 bg-blue-100 border border-blue-300 rounded-md flex items-center gap-1.5">
                              <Loader2 className="w-3.5 h-3.5 text-blue-600 animate-spin" />
                              <span className="text-xs text-blue-700 font-semibold">PDF İşleniyor</span>
                            </div>
                          </>
                        ) : isPending ? (
                          <>
                            <div className="px-2 py-1 bg-amber-100 border border-amber-300 rounded-md flex items-center gap-1.5">
                              <Loader2 className="w-3.5 h-3.5 text-amber-600 animate-spin" />
                              <span className="text-xs text-amber-700 font-semibold">AI Puanlıyor</span>
                            </div>
                          </>
                        ) : isCorrect ? (
                          <>
                            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                            <span className="text-sm text-emerald-700 font-medium">Doğru</span>
                          </>
                        ) : isPartial ? (
                          <>
                            <AlertCircle className="w-4 h-4 text-yellow-600" />
                            <span className="text-sm text-yellow-700 font-medium">Kısmen Doğru</span>
                          </>
                        ) : (
                          <>
                            <XCircle className="w-4 h-4 text-red-600" />
                            <span className="text-sm text-red-700 font-medium">Yanlış</span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className={`text-right`}>
                    {isExtractingAnswer ? (
                      <div className="flex flex-col items-end">
                        <div className="px-3 py-1.5 bg-blue-100 rounded-lg border border-blue-200 mb-1">
                          <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
                        </div>
                        <div className="text-xs text-gray-500">/ {q.max_score}</div>
                      </div>
                    ) : isPending ? (
                      <div className="flex flex-col items-end">
                        <div className="px-3 py-1.5 bg-amber-100 rounded-lg border border-amber-200 mb-1">
                          <Loader2 className="w-5 h-5 text-amber-600 animate-spin" />
                        </div>
                        <div className="text-xs text-gray-500">/ {q.max_score}</div>
                      </div>
                    ) : (
                      <>
                        <div className={`text-3xl font-bold ${
                          isCorrect ? 'text-emerald-600' :
                          isPartial ? 'text-yellow-600' :
                          'text-red-600'
                        }`}>
                          {q.score.toFixed(1)}
                        </div>
                        <div className="text-sm text-gray-600">/ {q.max_score}</div>
                      </>
                    )}
                  </div>
                </div>

                {/* Question Content */}
                <div className="p-6 space-y-4">
                  {/* Question Text (if available) */}
                  {q.question_text && (
                    <div>
                      <div className="flex items-center gap-2 mb-2">
                        <FileText className="w-4 h-4 text-gray-600" />
                        <h4 className="text-sm font-semibold text-gray-700">Soru:</h4>
                      </div>
                      <p className="text-gray-800 leading-relaxed bg-gray-50 p-4 rounded-lg border border-gray-200">
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
                    <p className="text-gray-800 leading-relaxed bg-emerald-50/50 p-4 rounded-lg border border-emerald-100">
                      {q.expected_answer}
                    </p>
                  </div>

                  {/* Student Answer */}
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <FileText className="w-4 h-4 text-blue-600" />
                      <h4 className="text-sm font-semibold text-blue-700">Öğrenci Cevabı:</h4>
                    </div>
                    {q.student_answer === "[Cevap çıkarılıyor...]" ? (
                      <div className="bg-gradient-to-r from-blue-50 via-indigo-50 to-purple-50 border-2 border-blue-300 rounded-lg p-5 shadow-sm">
                        <div className="flex items-start gap-4">
                          <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center flex-shrink-0 shadow-sm">
                            <Loader2 className="w-5 h-5 text-white animate-spin" />
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <h4 className="font-bold text-blue-900">📄 PDF İşleniyor</h4>
                              <span className="px-2 py-0.5 bg-blue-200 text-blue-800 text-xs rounded-full font-semibold animate-pulse">
                                ÇIKARILIYOR
                              </span>
                            </div>
                            <p className="text-blue-800 text-sm mb-2">
                              Öğrencinin PDF dosyası işleniyor ve cevaplar otomatik olarak çıkarılıyor.
                            </p>
                            <div className="flex items-center gap-2 text-blue-700 text-xs bg-white/60 rounded px-2 py-1">
                              <div className="flex gap-1">
                                <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                                <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                                <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                              </div>
                              <span>PDF metni okunuyor ve parse ediliyor...</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ) : q.student_answer === "[No answer provided]" || !q.student_answer ? (
                      <div className="text-gray-500 italic bg-gray-100 p-4 rounded-lg border border-gray-300">
                        Cevap bulunamadı veya boş bırakılmış
                      </div>
                    ) : (
                      <p className="text-gray-800 leading-relaxed bg-blue-50/50 p-4 rounded-lg border border-blue-100">
                        {q.student_answer}
                      </p>
                    )}
                  </div>

                  {/* Feedback */}
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <MessageSquare className="w-4 h-4 text-gray-600" />
                      <h4 className="text-sm font-semibold text-gray-900">Geri Bildirim:</h4>
                    </div>
                    {isPending ? (
                      <div className="bg-gradient-to-r from-amber-50 via-yellow-50 to-orange-50 border-2 border-amber-300 rounded-lg p-5 shadow-md">
                        <div className="flex items-start gap-4">
                          <div className="w-10 h-10 bg-amber-500 rounded-lg flex items-center justify-center flex-shrink-0 shadow-sm">
                            <Loader2 className="w-5 h-5 text-white animate-spin" />
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <h4 className="font-bold text-amber-900">🤖 AI Değerlendirme Yapılıyor</h4>
                              <span className="px-2 py-0.5 bg-amber-200 text-amber-800 text-xs rounded-full font-semibold animate-pulse">
                                İŞLENİYOR
                              </span>
                            </div>
                            <p className="text-amber-800 text-sm mb-2">
                              Bu soru şu anda yapay zeka tarafından analiz ediliyor.
                              Detaylı geri bildirim ve puan hesaplaması birazdan hazır olacak.
                            </p>
                            <div className="flex items-center gap-2 text-amber-700 text-xs bg-white/60 rounded px-2 py-1">
                              <div className="flex gap-1">
                                <div className="w-1.5 h-1.5 bg-amber-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                                <div className="w-1.5 h-1.5 bg-amber-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                                <div className="w-1.5 h-1.5 bg-amber-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                              </div>
                              <span>Cevap analiz ediliyor ve puanlanıyor...</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                        <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">{q.feedback}</p>
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
        className="fixed bottom-6 right-6 w-14 h-14 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-full shadow-lg hover:shadow-xl transition-all hover:scale-110 flex items-center justify-center z-50"
      >
        {isChatOpen ? <X className="w-6 h-6" /> : <MessageSquare className="w-6 h-6" />}
      </button>

      {/* Slide-in Chat Window */}
      {isChatOpen && (
        <div className="fixed bottom-24 right-6 w-96 h-[500px] bg-white rounded-2xl shadow-2xl border-2 border-gray-200 flex flex-col z-50 animate-in slide-in-from-bottom">
          {/* Chat Header */}
          <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-t-2xl">
            <h3 className="font-bold text-gray-900">AI Asistan</h3>
            <p className="text-sm text-gray-600">Bu öğrencinin performansı hakkında soru sorun</p>
          </div>

          {/* Chat Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {chatMessages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] px-4 py-3 rounded-2xl ${
                    msg.role === 'user'
                      ? 'bg-blue-600 text-white rounded-br-none'
                      : 'bg-gray-100 text-gray-900 rounded-bl-none'
                  }`}
                >
                  <p className="text-sm leading-relaxed">{msg.message}</p>
                </div>
              </div>
            ))}
            {chatLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 px-4 py-3 rounded-2xl rounded-bl-none">
                  <Loader2 className="w-5 h-5 text-gray-600 animate-spin" />
                </div>
              </div>
            )}
          </div>

          {/* Chat Input */}
          <form onSubmit={handleSendMessage} className="p-4 border-t border-gray-200 bg-gray-50 rounded-b-2xl">
            <div className="flex gap-2">
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder="Bir soru sorun..."
                className="flex-1 px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-400"
              />
              <button
                type="submit"
                disabled={!newMessage.trim() || chatLoading}
                className="px-4 py-2.5 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
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
