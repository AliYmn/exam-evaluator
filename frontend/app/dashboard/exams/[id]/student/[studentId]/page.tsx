'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import DashboardLayout from '@/components/DashboardLayout';
import {
  ArrowLeft, CheckCircle2, XCircle, AlertCircle,
  MessageSquare, Send, X, Loader2, FileText, Award, Target
} from 'lucide-react';
import Link from 'next/link';
import { examApi, StudentDetailResponse } from '@/lib/api';
import { useAuthStore } from '@/lib/store';

export default function StudentResultPage() {
  const params = useParams();
  const router = useRouter();
  const examId = params.id as string;
  const studentId = parseInt(params.studentId as string);
  const { token } = useAuthStore();

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
    if (token && studentId) {
      fetchStudentDetail();
    }
  }, [studentId, token]);

  const fetchStudentDetail = async () => {
    if (!token) {
      router.push('/login');
      return;
    }

    try {
      const data = await examApi.getStudentDetail(token, studentId);
      setStudent(data);
      setError(null);
    } catch (err: any) {
      console.error('Error fetching student detail:', err);
      setError(err.message || 'Failed to load student details');
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

  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto px-4 py-6">
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
            const percentage = (q.score / q.max_score) * 100;
            const isCorrect = percentage >= 80;
            const isPartial = percentage >= 50 && percentage < 80;

            return (
              <div key={q.question_number} className="bg-white rounded-xl shadow-sm border-2 border-gray-200 overflow-hidden hover:shadow-md transition">
                {/* Question Header */}
                <div className={`px-6 py-4 flex items-center justify-between ${
                  isCorrect ? 'bg-emerald-50' :
                  isPartial ? 'bg-yellow-50' :
                  'bg-red-50'
                }`}>
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                      isCorrect ? 'bg-emerald-200 text-emerald-900' :
                      isPartial ? 'bg-yellow-200 text-yellow-900' :
                      'bg-red-200 text-red-900'
                    }`}>
                      {q.question_number}
                    </div>
                    <div>
                      <h3 className="font-bold text-gray-900">Soru {q.question_number}</h3>
                      <div className="flex items-center gap-2 mt-1">
                        {isCorrect ? (
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
                    <div className={`text-3xl font-bold ${
                      isCorrect ? 'text-emerald-600' :
                      isPartial ? 'text-yellow-600' :
                      'text-red-600'
                    }`}>
                      {q.score.toFixed(1)}
                    </div>
                    <div className="text-sm text-gray-600">/ {q.max_score}</div>
                  </div>
                </div>

                {/* Question Content */}
                <div className="p-6 space-y-4">
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
                    <p className="text-gray-800 leading-relaxed bg-blue-50/50 p-4 rounded-lg border border-blue-100">
                      {q.student_answer}
                    </p>
                  </div>

                  {/* Feedback */}
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <MessageSquare className="w-4 h-4 text-gray-600" />
                      <h4 className="text-sm font-semibold text-gray-900">Geri Bildirim:</h4>
                    </div>
                    <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                      <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">{q.feedback}</p>
                    </div>
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
