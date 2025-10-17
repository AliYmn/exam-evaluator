'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import DashboardLayout from '@/components/DashboardLayout';
import {
  Upload, FileText, ArrowLeft, CheckCircle2, Clock, AlertCircle,
  Loader2, RefreshCw, CheckCircle, XCircle, User, TrendingUp
} from 'lucide-react';
import Link from 'next/link';
import { examApi, ExamDetail, StudentListItem } from '@/lib/api';
import { useAuthStore } from '@/lib/store';

export default function ExamDetailPage() {
  const params = useParams();
  const router = useRouter();
  const examId = params.id as string;
  const { token } = useAuthStore();

  const [exam, setExam] = useState<ExamDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  // Student upload form state
  const [studentName, setStudentName] = useState('');
  const [studentFile, setStudentFile] = useState<File | null>(null);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState(false);

  // Students list state
  const [students, setStudents] = useState<StudentListItem[]>([]);
  const [studentsLoading, setStudentsLoading] = useState(false);

  const fetchExamDetails = async () => {
    if (!token) {
      router.push('/login');
      return;
    }

    try {
      const data = await examApi.getExamDetails(token, examId);
      setExam(data);
      setError(null);
    } catch (err: any) {
      console.error('Error fetching exam:', err);
      setError(err.message || 'Sınav detayları yüklenirken bir hata oluştu');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const fetchStudents = async () => {
    if (!token || !examId) return;

    setStudentsLoading(true);
    try {
      const data = await examApi.getExamStudents(token, examId);
      setStudents(data);
    } catch (err: any) {
      console.error('Error fetching students:', err);
    } finally {
      setStudentsLoading(false);
    }
  };

  useEffect(() => {
    fetchExamDetails();
    fetchStudents();
  }, [examId, token]);

  // Auto-refresh while parsing or while students are processing
  useEffect(() => {
    const hasProcessingStudents = students.some(s => s.status === 'processing' || s.status === 'pending');
    const shouldAutoRefresh = exam?.status === 'parsing' || exam?.status === 'pending' || hasProcessingStudents;

    if (shouldAutoRefresh) {
      const interval = setInterval(() => {
        fetchExamDetails();
        fetchStudents();
      }, 3000); // Refresh every 3 seconds

      return () => clearInterval(interval);
    }
  }, [exam?.status, students]);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchExamDetails();
    fetchStudents();
  };

  const handleStudentUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    setUploadError(null);
    setUploadSuccess(false);

    if (!studentName || !studentFile) {
      setUploadError('Please fill in all fields');
      return;
    }

    if (!studentFile.name.toLowerCase().endsWith('.pdf')) {
      setUploadError('Student sheet must be a PDF file');
      return;
    }

    if (!token) {
      setUploadError('You must be logged in');
      return;
    }

    setUploadLoading(true);

    try {
      await examApi.uploadStudentSheet(token, examId, studentName, studentFile);
      setUploadSuccess(true);
      setStudentName('');
      setStudentFile(null);

      // Refresh students list to show new student
      setTimeout(() => {
        fetchStudents();
        setUploadSuccess(false);
      }, 2000);
    } catch (err: any) {
      setUploadError(err.message || 'Failed to upload student sheet');
    } finally {
      setUploadLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-emerald-100 text-emerald-700 rounded-full text-sm font-medium">
            <CheckCircle className="w-4 h-4" />
            Completed
          </span>
        );
      case 'parsing':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">
            <Loader2 className="w-4 h-4 animate-spin" />
            Processing
          </span>
        );
      case 'pending':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-yellow-100 text-yellow-700 rounded-full text-sm font-medium">
            <Clock className="w-4 h-4" />
            Pending
          </span>
        );
      case 'failed':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-medium">
            <XCircle className="w-4 h-4" />
            Failed
          </span>
        );
      default:
        return null;
    }
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-screen">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      </DashboardLayout>
    );
  }

  if (error || !exam) {
    return (
      <DashboardLayout>
        <div className="max-w-2xl mx-auto mt-20">
          <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
            <AlertCircle className="w-12 h-12 text-red-600 mx-auto mb-4" />
            <h2 className="text-xl font-bold text-red-900 mb-2">Sınav Yüklenemedi</h2>
            <p className="text-red-800 mb-6">{error}</p>
            <div className="flex items-center justify-center gap-4">
              <button
                onClick={() => {
                  setError(null);
                  setLoading(true);
                  fetchExamDetails();
                  fetchStudents();
                }}
                className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
              >
                <RefreshCw className="w-4 h-4" />
                Tekrar Dene
              </button>
              <Link
                href="/dashboard/exams"
                className="inline-flex items-center gap-2 px-6 py-3 bg-gray-200 text-gray-900 rounded-lg hover:bg-gray-300 transition"
              >
                <ArrowLeft className="w-4 h-4" />
                Sınavlara Dön
              </Link>
            </div>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Link
            href="/dashboard/exams"
            className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4 transition"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Exams
          </Link>

          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{exam.exam_title}</h1>
              <div className="flex items-center gap-3 text-sm text-gray-600">
                <span>Created: {new Date(exam.created_at).toLocaleDateString()}</span>
                {exam.total_questions && (
                  <>
                    <span>•</span>
                    <span>{exam.total_questions} Questions</span>
                  </>
                )}
              </div>
            </div>

            <div className="flex items-center gap-3">
              {getStatusBadge(exam.status)}
              <button
                onClick={handleRefresh}
                disabled={refreshing}
                className="p-2 hover:bg-gray-100 rounded-lg transition disabled:opacity-50"
                title="Refresh"
              >
                <RefreshCw className={`w-5 h-5 text-gray-600 ${refreshing ? 'animate-spin' : ''}`} />
              </button>
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        {(exam.status === 'parsing' || exam.status === 'pending') && (
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200 mb-6">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
                <div>
                  <h3 className="text-sm font-semibold text-gray-900">Processing Answer Key</h3>
                  <p className="text-xs text-gray-600 mt-0.5">{exam.current_message}</p>
                </div>
              </div>
              <span className="text-sm font-semibold text-blue-600">
                {Math.round(exam.progress_percentage)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
              <div
                className="bg-gradient-to-r from-blue-500 to-indigo-600 h-2.5 rounded-full transition-all duration-500 ease-out"
                style={{ width: `${exam.progress_percentage}%` }}
              ></div>
            </div>
          </div>
        )}

        {/* Error Message */}
        {exam.status === 'failed' && exam.error_message && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-6 mb-6">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="text-sm font-semibold text-red-900 mb-1">Processing Failed</h3>
                <p className="text-sm text-red-800">{exam.error_message}</p>
              </div>
            </div>
          </div>
        )}

        {/* Student Upload & List Section - Only show when answer key is completed */}
        {exam.status === 'completed' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            {/* Left: Student Upload Form */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
                    <Upload className="w-5 h-5 text-white" />
                  </div>
                  <h2 className="text-lg font-bold text-gray-900">Upload Student Sheet</h2>
                </div>

                <form onSubmit={handleStudentUpload} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Student Name
                    </label>
                    <input
                      type="text"
                      value={studentName}
                      onChange={(e) => setStudentName(e.target.value)}
                      placeholder="e.g., John Doe"
                      className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-400"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Answer Sheet (PDF)
                    </label>
                    <input
                      type="file"
                      id="student-file"
                      accept=".pdf"
                      onChange={(e) => e.target.files && setStudentFile(e.target.files[0])}
                      className="hidden"
                    />
                    <label
                      htmlFor="student-file"
                      className="flex items-center justify-center gap-3 w-full px-4 py-3 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:border-blue-500 transition"
                    >
                      {studentFile ? (
                        <div className="flex items-center gap-2">
                          <FileText className="w-5 h-5 text-blue-600" />
                          <span className="text-sm text-gray-900">{studentFile.name}</span>
                        </div>
                      ) : (
                        <>
                          <Upload className="w-5 h-5 text-gray-400" />
                          <span className="text-sm text-gray-600">Choose PDF file</span>
                        </>
                      )}
                    </label>
                  </div>

                  {uploadError && (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                      <div className="flex items-start justify-between gap-2">
                        <p className="text-sm text-red-800 flex-1">{uploadError}</p>
                        <button
                          onClick={() => setUploadError(null)}
                          className="text-red-600 hover:text-red-800"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  )}

                  {uploadSuccess && (
                    <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-3">
                      <p className="text-sm text-emerald-800">Student sheet uploaded successfully!</p>
                    </div>
                  )}

                  <button
                    type="submit"
                    disabled={uploadLoading || !studentName || !studentFile}
                    className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-3 rounded-lg font-medium hover:from-blue-700 hover:to-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    {uploadLoading ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        <span>Uploading...</span>
                      </>
                    ) : (
                      <>
                        <Upload className="w-5 h-5" />
                        <span>Upload Sheet</span>
                      </>
                    )}
                  </button>
                </form>
              </div>
            </div>

            {/* Right: Students List */}
            <div className="lg:col-span-2">
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-gray-50 to-white">
                  <h2 className="text-lg font-bold text-gray-900">Uploaded Students</h2>
                  <p className="text-sm text-gray-600 mt-1">Students who have submitted their answers</p>
                </div>

                <div className="p-6">
                  {studentsLoading ? (
                    <div className="flex items-center justify-center py-8">
                      <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
                    </div>
                  ) : students.length === 0 ? (
                    <div className="text-center py-8 text-gray-500">
                      <User className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                      <p className="text-sm">No students uploaded yet. Upload student sheets to see them here.</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {students.map((student) => (
                        <div
                          key={student.student_response_id}
                          className={`flex items-center justify-between p-4 border rounded-lg transition ${
                            student.status === 'failed'
                              ? 'border-red-300 bg-red-50 opacity-60'
                              : student.status === 'completed'
                              ? 'border-gray-200 hover:border-blue-400 hover:bg-blue-50 cursor-pointer'
                              : 'border-gray-200 bg-gray-50'
                          }`}
                          onClick={() => {
                            if (student.status === 'completed') {
                              router.push(`/dashboard/exams/${examId}/student/${student.student_response_id}`);
                            }
                          }}
                        >
                          <div className="flex items-center gap-4">
                            <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                              student.status === 'failed'
                                ? 'bg-gradient-to-br from-red-500 to-red-600'
                                : 'bg-gradient-to-br from-blue-500 to-indigo-600'
                            }`}>
                              <User className="w-5 h-5 text-white" />
                            </div>
                            <div>
                              <h3 className="font-semibold text-gray-900">{student.student_name}</h3>
                              <p className="text-sm text-gray-500">
                                {student.status === 'completed'
                                  ? `Puan: ${student.total_score.toFixed(1)}/${student.max_score.toFixed(1)} (${student.percentage.toFixed(1)}%)`
                                  : student.status === 'failed'
                                  ? 'Değerlendirme başarısız oldu'
                                  : 'İşleniyor...'}
                              </p>
                            </div>
                          </div>

                          <div className="flex items-center gap-3">
                            {student.status === 'completed' ? (
                              <>
                                <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-100 text-emerald-700 rounded-lg">
                                  <TrendingUp className="w-4 h-4" />
                                  <span className="text-sm font-medium">{student.percentage.toFixed(1)}%</span>
                                </div>
                                <CheckCircle className="w-5 h-5 text-emerald-600" />
                              </>
                            ) : student.status === 'processing' ? (
                              <div className="flex items-center gap-2 px-3 py-1.5 bg-blue-100 text-blue-700 rounded-lg">
                                <Loader2 className="w-4 h-4 animate-spin" />
                                <span className="text-sm font-medium">İşleniyor</span>
                              </div>
                            ) : student.status === 'failed' ? (
                              <div className="flex items-center gap-2 px-3 py-1.5 bg-red-100 text-red-700 rounded-lg">
                                <XCircle className="w-4 h-4" />
                                <span className="text-sm font-medium">Başarısız</span>
                              </div>
                            ) : (
                              <div className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 text-gray-700 rounded-lg">
                                <Clock className="w-4 h-4" />
                                <span className="text-sm font-medium">Bekliyor</span>
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Questions List */}
        {exam.status === 'completed' && exam.questions && exam.questions.length > 0 && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-bold text-gray-900">Answer Key Questions</h2>
                <span className="text-sm text-gray-600">
                  {exam.questions.length} question{exam.questions.length !== 1 ? 's' : ''}
                </span>
              </div>
            </div>

            <div className="divide-y divide-gray-200">
              {exam.questions.map((question, index) => (
                <div key={index} className="p-6 hover:bg-gray-50 transition">
                  <div className="flex items-start gap-4">
                    <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
                      <span className="text-white font-bold text-sm">{question.number}</span>
                    </div>

                    <div className="flex-1 space-y-3">
                      <div>
                        <h3 className="text-sm font-semibold text-gray-900 mb-2">Question:</h3>
                        <p className="text-gray-800 leading-relaxed">{question.question_text}</p>
                      </div>

                      <div>
                        <h4 className="text-sm font-semibold text-emerald-700 mb-2">Expected Answer:</h4>
                        <p className="text-gray-700 leading-relaxed bg-emerald-50 p-3 rounded-lg border border-emerald-100">
                          {question.expected_answer}
                        </p>
                      </div>

                      {question.keywords && question.keywords.length > 0 && (
                        <div className="flex flex-wrap gap-2 pt-2">
                          {question.keywords.map((keyword, idx) => (
                            <span
                              key={idx}
                              className="px-2.5 py-1 bg-blue-100 text-blue-700 text-xs font-medium rounded-full"
                            >
                              {keyword}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {exam.status === 'completed' && (!exam.questions || exam.questions.length === 0) && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
            <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No Questions Found</h3>
            <p className="text-gray-600">
              The answer key was processed but no questions were extracted.
            </p>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
