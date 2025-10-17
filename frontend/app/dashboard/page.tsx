'use client';

import DashboardLayout from '@/components/DashboardLayout';
import { FileText, Upload, Clock, CheckCircle2, ArrowRight, FolderOpen, BarChart3, Eye } from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function DashboardPage() {
  const router = useRouter();

  // Dummy recent evaluations - bu kısım backend'den gelecek
  const recentEvaluations = [
    {
      id: 1,
      title: 'Biology Midterm Exam',
      class: 'Class 10A',
      students: 5,
      avgScore: 87,
      status: 'completed',
      date: '2 hours ago',
      color: 'emerald'
    },
    {
      id: 2,
      title: 'Physics Quiz',
      class: 'Class 9B',
      students: 8,
      avgScore: 92,
      status: 'completed',
      date: '1 day ago',
      color: 'blue'
    },
    {
      id: 3,
      title: 'Math Final Exam',
      class: 'Class 11C',
      students: 3,
      avgScore: null,
      status: 'processing',
      date: '3 days ago',
      color: 'amber'
    },
  ];

  const isEmpty = recentEvaluations.length === 0;

  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
          <p className="text-gray-600">Welcome back! Ready to evaluate some exams?</p>
        </div>

        {/* Quick Actions - Large Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Upload New Evaluation */}
          <Link
            href="/dashboard/evaluate"
            className="group relative bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl p-8 text-white shadow-xl shadow-blue-500/30 hover:shadow-2xl hover:shadow-blue-500/40 transition-all hover:scale-[1.02] cursor-pointer overflow-hidden"
          >
            <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl -mr-32 -mt-32"></div>
            <div className="relative">
              <div className="w-16 h-16 bg-white/20 backdrop-blur rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <Upload className="w-8 h-8" />
              </div>
              <h2 className="text-2xl font-bold mb-2">Start New Evaluation</h2>
              <p className="text-blue-100 mb-4">Upload answer key and student responses to begin automated grading</p>
              <div className="flex items-center gap-2 text-sm font-medium">
                <span>Upload Files</span>
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </div>
            </div>
          </Link>

          {/* View All Evaluations */}
          <Link
            href="/dashboard/evaluations"
            className="group relative bg-white rounded-2xl p-8 shadow-lg border border-gray-200 hover:shadow-xl transition-all hover:scale-[1.02] cursor-pointer overflow-hidden"
          >
            <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-full blur-3xl -mr-32 -mt-32"></div>
            <div className="relative">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform shadow-lg shadow-blue-500/30">
                <BarChart3 className="w-8 h-8 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">View All Evaluations</h2>
              <p className="text-gray-600 mb-4">Browse through all evaluated exams and detailed analytics</p>
              <div className="flex items-center gap-2 text-sm font-medium text-blue-600">
                <span>Browse Evaluations</span>
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </div>
            </div>
          </Link>
        </div>

        {/* Recent Evaluations List */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
          <div className="p-6 border-b border-gray-200 bg-gradient-to-r from-gray-50 to-white">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center shadow-lg shadow-blue-500/30">
                  <FileText className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-gray-900">Recent Evaluations</h2>
                  <p className="text-sm text-gray-600">Your latest exam evaluations</p>
                </div>
              </div>
              <Link
                href="/dashboard/evaluations"
                className="text-sm font-medium text-blue-600 hover:text-blue-700 flex items-center gap-1 hover:gap-2 transition-all"
              >
                View All
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>

          <div className="p-6">
            {isEmpty ? (
              // Empty State
              <div className="text-center py-16">
                <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <FolderOpen className="w-10 h-10 text-gray-400" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">No evaluations yet</h3>
                <p className="text-gray-600 mb-6 max-w-md mx-auto">
                  Start by uploading your first exam files to see the magic of AI-powered grading
                </p>
                <Link
                  href="/dashboard/evaluate"
                  className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-3 rounded-xl font-medium hover:from-blue-700 hover:to-indigo-700 shadow-lg shadow-blue-500/30 transition-all"
                >
                  <Upload className="w-4 h-4" />
                  Upload First Exam
                </Link>
              </div>
            ) : (
              // Evaluations List
              <div className="space-y-3">
                {recentEvaluations.map((evaluation) => (
                  <div
                    key={evaluation.id}
                    onClick={() => router.push(`/dashboard/results?id=${evaluation.id}`)}
                    className="group flex items-center justify-between p-5 bg-gray-50 hover:bg-gradient-to-r hover:from-blue-50 hover:to-indigo-50 rounded-xl cursor-pointer transition-all border border-transparent hover:border-blue-200"
                  >
                    <div className="flex items-center gap-4 flex-1">
                      {/* Status Icon */}
                      <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                        evaluation.status === 'completed'
                          ? 'bg-emerald-100 text-emerald-600'
                          : 'bg-amber-100 text-amber-600'
                      }`}>
                        {evaluation.status === 'completed' ? (
                          <CheckCircle2 className="w-6 h-6" />
                        ) : (
                          <Clock className="w-6 h-6 animate-pulse" />
                        )}
                      </div>

                      {/* Info */}
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900 mb-1 group-hover:text-blue-600 transition-colors">
                          {evaluation.title}
                        </h3>
                        <div className="flex items-center gap-4 text-sm text-gray-600">
                          <span className="flex items-center gap-1">
                            <FileText className="w-4 h-4" />
                            {evaluation.class}
                          </span>
                          <span>•</span>
                          <span>{evaluation.students} students</span>
                          {evaluation.avgScore && (
                            <>
                              <span>•</span>
                              <span className="font-medium text-emerald-600">
                                Avg: {evaluation.avgScore}%
                              </span>
                            </>
                          )}
                        </div>
                      </div>

                      {/* Date & Action */}
                      <div className="flex items-center gap-4">
                        <span className="text-sm text-gray-500">{evaluation.date}</span>
                        <button className="w-9 h-9 rounded-lg bg-white border border-gray-200 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all hover:border-blue-300 hover:bg-blue-50">
                          <Eye className="w-4 h-4 text-gray-600" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Footer Stats */}
          {!isEmpty && (
            <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-6">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
                    <span className="text-gray-600">
                      <span className="font-semibold text-gray-900">
                        {recentEvaluations.filter(e => e.status === 'completed').length}
                      </span> Completed
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></div>
                    <span className="text-gray-600">
                      <span className="font-semibold text-gray-900">
                        {recentEvaluations.filter(e => e.status === 'processing').length}
                      </span> Processing
                    </span>
                  </div>
                </div>
                <Link
                  href="/dashboard/evaluate"
                  className="text-blue-600 hover:text-blue-700 font-medium flex items-center gap-1"
                >
                  <Upload className="w-4 h-4" />
                  New Evaluation
                </Link>
              </div>
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
