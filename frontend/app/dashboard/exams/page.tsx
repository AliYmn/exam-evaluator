'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import DashboardLayout from '@/components/DashboardLayout';
import {
  Plus, FileText, CheckCircle, Clock, Loader2, XCircle, AlertCircle
} from 'lucide-react';
import Link from 'next/link';
import { examApi, ExamListItem } from '@/lib/api';
import { useAuthStore } from '@/lib/store';

export default function ExamsListPage() {
  const router = useRouter();
  const { token } = useAuthStore();

  const [exams, setExams] = useState<ExamListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchExams();
  }, []);

  const fetchExams = async () => {
    if (!token) {
      router.push('/login');
      return;
    }

    try {
      const response = await examApi.getAllExams(token);
      setExams(response.exams);
      setError(null);
    } catch (err: any) {
      console.error('Error fetching exams:', err);
      setError(err.message || 'Failed to load exams');
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-emerald-500" />;
      case 'parsing':
        return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />;
      case 'pending':
        return <Clock className="w-5 h-5 text-yellow-500" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return null;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return 'Completed';
      case 'parsing':
        return 'Processing';
      case 'pending':
        return 'Pending';
      case 'failed':
        return 'Failed';
      default:
        return status;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'parsing':
        return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'pending':
        return 'bg-yellow-50 text-yellow-700 border-yellow-200';
      case 'failed':
        return 'bg-red-50 text-red-700 border-red-200';
      default:
        return 'bg-gray-50 text-gray-700 border-gray-200';
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

  return (
    <DashboardLayout>
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">All Exams</h1>
            <p className="text-gray-600 mt-2">Manage and view all your exams</p>
          </div>
          <Link
            href="/dashboard/exams/new"
            className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 transition shadow-lg shadow-blue-500/30 font-medium"
          >
            <Plus className="w-5 h-5" />
            Create New Exam
          </Link>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-6 mb-6">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0" />
              <div>
                <h3 className="text-sm font-semibold text-red-900 mb-1">Error</h3>
                <p className="text-sm text-red-800">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Exams List */}
        {exams.length > 0 ? (
          <div className="space-y-4">
            {exams.map((exam) => (
              <Link
                key={exam.evaluation_id}
                href={`/dashboard/exams/${exam.evaluation_id}`}
                className="block bg-white rounded-xl border border-gray-200 p-6 hover:shadow-lg hover:border-blue-200 transition group"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-start gap-4 flex-1">
                    <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                      <FileText className="w-6 h-6 text-white" />
                    </div>

                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 mb-1 group-hover:text-blue-600 transition">
                        {exam.exam_title}
                      </h3>

                      <div className="flex items-center gap-4 text-sm text-gray-600">
                        <span>Created: {new Date(exam.created_at).toLocaleDateString()}</span>
                        {exam.total_questions && (
                          <>
                            <span>•</span>
                            <span>{exam.total_questions} Questions</span>
                          </>
                        )}
                      </div>

                      {/* Progress Bar for Processing */}
                      {(exam.status === 'parsing' || exam.status === 'pending') && exam.progress_percentage > 0 && (
                        <div className="mt-3 w-full max-w-xs">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-xs text-gray-600">Processing</span>
                            <span className="text-xs font-semibold text-blue-600">
                              {Math.round(exam.progress_percentage)}%
                            </span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-1.5">
                            <div
                              className="bg-gradient-to-r from-blue-500 to-indigo-600 h-1.5 rounded-full transition-all"
                              style={{ width: `${exam.progress_percentage}%` }}
                            ></div>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg border font-medium text-sm ${getStatusColor(exam.status)}`}>
                      {getStatusIcon(exam.status)}
                      {getStatusText(exam.status)}
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        ) : (
          // Empty State
          <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <FileText className="w-8 h-8 text-blue-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">No Exams Yet</h3>
            <p className="text-gray-600 mb-6">
              Create your first exam to get started with AI-powered evaluation
            </p>
            <Link
              href="/dashboard/exams/new"
              className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 transition shadow-lg shadow-blue-500/30 font-medium"
            >
              <Plus className="w-5 h-5" />
              Create Your First Exam
            </Link>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
