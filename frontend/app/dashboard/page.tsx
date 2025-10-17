'use client';

import DashboardLayout from '@/components/DashboardLayout';
import { FileText, Upload, Clock, CheckCircle2, ArrowRight, FolderOpen, BarChart3, Eye, TrendingUp, Users, Award } from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function DashboardPage() {
  const router = useRouter();

  // Mock statistics - bu kısım backend'den gelecek
  const stats = {
    totalExams: 12,
    totalStudents: 45,
    avgScore: 86.5,
    completedToday: 8
  };

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
    {
      id: 4,
      title: 'Chemistry Lab Test',
      class: 'Class 12A',
      students: 12,
      avgScore: 78,
      status: 'completed',
      date: '5 days ago',
      color: 'blue'
    },
    {
      id: 5,
      title: 'English Literature Exam',
      class: 'Class 10B',
      students: 6,
      avgScore: 85,
      status: 'completed',
      date: '1 week ago',
      color: 'emerald'
    },
  ];

  const isEmpty = recentEvaluations.length === 0;

  return (
    <DashboardLayout>
      <div>
        {/* Header */}
        <div className="mb-10">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-2">
                Welcome Back! 👋
              </h1>
              <p className="text-lg text-gray-600">Here's what's happening with your exams today.</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-500">Today</p>
              <p className="text-xl font-bold text-gray-900">
                {new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
              </p>
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
          <div className="group relative bg-white rounded-2xl shadow-md border border-gray-200 p-6 hover:shadow-xl transition-all hover:-translate-y-1 overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-blue-50 rounded-full blur-3xl -mr-16 -mt-16 group-hover:bg-blue-100 transition-colors"></div>
            <div className="relative">
              <div className="flex items-center justify-between mb-4">
                <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/30">
                  <FolderOpen className="w-7 h-7 text-white" />
                </div>
                <span className="text-xs text-emerald-600 font-semibold bg-emerald-50 px-3 py-1 rounded-full">+3 this week</span>
              </div>
              <h3 className="text-4xl font-bold text-gray-900 mb-1">{stats.totalExams}</h3>
              <p className="text-sm text-gray-600 font-medium">Total Exams</p>
            </div>
          </div>

          <div className="group relative bg-white rounded-2xl shadow-md border border-gray-200 p-6 hover:shadow-xl transition-all hover:-translate-y-1 overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-50 rounded-full blur-3xl -mr-16 -mt-16 group-hover:bg-indigo-100 transition-colors"></div>
            <div className="relative">
              <div className="flex items-center justify-between mb-4">
                <div className="w-14 h-14 bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-500/30">
                  <Users className="w-7 h-7 text-white" />
                </div>
                <span className="text-xs text-blue-600 font-semibold bg-blue-50 px-3 py-1 rounded-full">{stats.completedToday} today</span>
              </div>
              <h3 className="text-4xl font-bold text-gray-900 mb-1">{stats.totalStudents}</h3>
              <p className="text-sm text-gray-600 font-medium">Students Evaluated</p>
            </div>
          </div>

          <div className="group relative bg-white rounded-2xl shadow-md border border-gray-200 p-6 hover:shadow-xl transition-all hover:-translate-y-1 overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-50 rounded-full blur-3xl -mr-16 -mt-16 group-hover:bg-emerald-100 transition-colors"></div>
            <div className="relative">
              <div className="flex items-center justify-between mb-4">
                <div className="w-14 h-14 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl flex items-center justify-center shadow-lg shadow-emerald-500/30">
                  <Award className="w-7 h-7 text-white" />
                </div>
                <span className="text-xs text-emerald-600 font-semibold bg-emerald-50 px-3 py-1 rounded-full flex items-center gap-1">
                  <TrendingUp className="w-3 h-3" />
                  +2.5%
                </span>
              </div>
              <h3 className="text-4xl font-bold text-gray-900 mb-1">{stats.avgScore}%</h3>
              <p className="text-sm text-gray-600 font-medium">Average Score</p>
            </div>
          </div>

          <div className="group relative bg-white rounded-2xl shadow-md border border-gray-200 p-6 hover:shadow-xl transition-all hover:-translate-y-1 overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-amber-50 rounded-full blur-3xl -mr-16 -mt-16 group-hover:bg-amber-100 transition-colors"></div>
            <div className="relative">
              <div className="flex items-center justify-between mb-4">
                <div className="w-14 h-14 bg-gradient-to-br from-amber-500 to-amber-600 rounded-xl flex items-center justify-center shadow-lg shadow-amber-500/30">
                  <Clock className="w-7 h-7 text-white" />
                </div>
                <span className="text-xs text-gray-500 font-semibold bg-gray-100 px-3 py-1 rounded-full">In progress</span>
              </div>
              <h3 className="text-4xl font-bold text-gray-900 mb-1">2</h3>
              <p className="text-sm text-gray-600 font-medium">Processing Now</p>
            </div>
          </div>
        </div>

        {/* Quick Actions - Compact Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-10">
          {/* Create New Exam */}
          <Link
            href="/dashboard/exams/new"
            className="group relative bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-600 rounded-2xl p-6 text-white shadow-xl shadow-blue-500/30 hover:shadow-2xl hover:shadow-blue-500/40 transition-all hover:scale-[1.02] cursor-pointer overflow-hidden"
          >
            <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl -mr-32 -mt-32 group-hover:bg-white/20 transition-colors"></div>
            <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/5 rounded-full blur-3xl -ml-24 -mb-24"></div>
            <div className="relative">
              <div className="w-16 h-16 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 group-hover:rotate-3 transition-all">
                <Upload className="w-8 h-8" />
              </div>
              <h2 className="text-2xl font-bold mb-2">Create New Exam</h2>
              <p className="text-blue-100 mb-4 text-base leading-relaxed">Set up a new exam with answer key and add students for AI-powered evaluation</p>
              <div className="flex items-center gap-2 text-sm font-semibold bg-white/20 backdrop-blur-sm w-fit px-4 py-2 rounded-lg group-hover:bg-white/30 transition-colors">
                <span>Get Started</span>
                <ArrowRight className="w-4 h-4 group-hover:translate-x-2 transition-transform" />
              </div>
            </div>
          </Link>

          {/* View All Exams */}
          <Link
            href="/dashboard/exams"
            className="group relative bg-white rounded-2xl p-6 shadow-lg border-2 border-gray-200 hover:shadow-xl hover:border-blue-300 transition-all hover:scale-[1.02] cursor-pointer overflow-hidden"
          >
            <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 rounded-full blur-3xl -mr-32 -mt-32 group-hover:from-blue-100 group-hover:via-indigo-100 group-hover:to-purple-100 transition-colors"></div>
            <div className="relative">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 via-indigo-600 to-purple-600 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 group-hover:-rotate-3 transition-all shadow-lg shadow-blue-500/30">
                <BarChart3 className="w-8 h-8 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">View All Exams</h2>
              <p className="text-gray-600 mb-4 text-base leading-relaxed">Browse through all exams and student evaluations with detailed analytics</p>
              <div className="flex items-center gap-2 text-sm font-semibold text-blue-600 bg-blue-50 w-fit px-4 py-2 rounded-lg group-hover:bg-blue-100 transition-colors">
                <span>Browse Exams</span>
                <ArrowRight className="w-4 h-4 group-hover:translate-x-2 transition-transform" />
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
                href="/dashboard/exams"
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
                  href="/dashboard/exams/new"
                  className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-3 rounded-xl font-medium hover:from-blue-700 hover:to-indigo-700 shadow-lg shadow-blue-500/30 transition-all"
                >
                  <Upload className="w-4 h-4" />
                  Create First Exam
                </Link>
              </div>
            ) : (
              // Evaluations List
              <div className="space-y-3">
                {recentEvaluations.map((evaluation) => (
                  <div
                    key={evaluation.id}
                    onClick={() => router.push(`/dashboard/exams/${evaluation.id}`)}
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
                  href="/dashboard/exams/new"
                  className="text-blue-600 hover:text-blue-700 font-medium flex items-center gap-1"
                >
                  <Upload className="w-4 h-4" />
                  New Exam
                </Link>
              </div>
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
