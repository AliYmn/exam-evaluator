'use client';

import { useState } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import {
  Search, Filter, Calendar, FileText, CheckCircle2, Clock,
  XCircle, Eye, Download, MoreVertical, TrendingUp, Users,
  ChevronDown, ArrowUpDown
} from 'lucide-react';
import Link from 'next/link';

export default function EvaluationsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<'all' | 'completed' | 'processing' | 'failed'>('all');
  const [sortBy, setSortBy] = useState<'date' | 'score' | 'students'>('date');

  // Dummy data - backend'den gelecek
  const allEvaluations = [
    {
      id: 1,
      title: 'Biology Midterm Exam',
      class: 'Class 10A',
      subject: 'Biology',
      students: 5,
      avgScore: 87,
      maxScore: 100,
      status: 'completed',
      date: '2024-01-15',
      createdAt: '2 hours ago',
    },
    {
      id: 2,
      title: 'Physics Quiz - Mechanics',
      class: 'Class 9B',
      subject: 'Physics',
      students: 8,
      avgScore: 92,
      maxScore: 50,
      status: 'completed',
      date: '2024-01-14',
      createdAt: '1 day ago',
    },
    {
      id: 3,
      title: 'Math Final Exam',
      class: 'Class 11C',
      subject: 'Mathematics',
      students: 3,
      avgScore: null,
      maxScore: 100,
      status: 'processing',
      date: '2024-01-12',
      createdAt: '3 days ago',
    },
    {
      id: 4,
      title: 'Chemistry Lab Report',
      class: 'Class 10B',
      subject: 'Chemistry',
      students: 6,
      avgScore: 78,
      maxScore: 50,
      status: 'completed',
      date: '2024-01-10',
      createdAt: '5 days ago',
    },
    {
      id: 5,
      title: 'English Literature Essay',
      class: 'Class 12A',
      subject: 'English',
      students: 10,
      avgScore: 85,
      maxScore: 100,
      status: 'completed',
      date: '2024-01-08',
      createdAt: '1 week ago',
    },
    {
      id: 6,
      title: 'History Midterm',
      class: 'Class 11A',
      subject: 'History',
      students: 7,
      avgScore: null,
      maxScore: 100,
      status: 'failed',
      date: '2024-01-05',
      createdAt: '2 weeks ago',
    },
  ];

  // Filter and search
  const filteredEvaluations = allEvaluations.filter((evaluation) => {
    const matchesSearch = evaluation.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         evaluation.class.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         evaluation.subject.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFilter = filterStatus === 'all' || evaluation.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

  // Stats
  const stats = {
    total: allEvaluations.length,
    completed: allEvaluations.filter(e => e.status === 'completed').length,
    processing: allEvaluations.filter(e => e.status === 'processing').length,
    failed: allEvaluations.filter(e => e.status === 'failed').length,
    totalStudents: allEvaluations.reduce((sum, e) => sum + e.students, 0),
    avgScore: Math.round(
      allEvaluations
        .filter(e => e.avgScore !== null)
        .reduce((sum, e) => sum + (e.avgScore || 0), 0) /
      allEvaluations.filter(e => e.avgScore !== null).length
    ),
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-emerald-100 text-emerald-700 border-emerald-200';
      case 'processing':
        return 'bg-amber-100 text-amber-700 border-amber-200';
      case 'failed':
        return 'bg-red-100 text-red-700 border-red-200';
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="w-4 h-4" />;
      case 'processing':
        return <Clock className="w-4 h-4 animate-pulse" />;
      case 'failed':
        return <XCircle className="w-4 h-4" />;
      default:
        return <FileText className="w-4 h-4" />;
    }
  };

  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">All Evaluations</h1>
          <p className="text-gray-600">Manage and review all your exam evaluations</p>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-xl p-5 border border-gray-200 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Total Evaluations</p>
                <p className="text-3xl font-bold text-gray-900">{stats.total}</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <FileText className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl p-5 border border-gray-200 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Completed</p>
                <p className="text-3xl font-bold text-emerald-600">{stats.completed}</p>
              </div>
              <div className="w-12 h-12 bg-emerald-100 rounded-lg flex items-center justify-center">
                <CheckCircle2 className="w-6 h-6 text-emerald-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl p-5 border border-gray-200 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Average Score</p>
                <p className="text-3xl font-bold text-indigo-600">{stats.avgScore}%</p>
              </div>
              <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-indigo-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl p-5 border border-gray-200 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Total Students</p>
                <p className="text-3xl font-bold text-purple-600">{stats.totalStudents}</p>
              </div>
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <Users className="w-6 h-6 text-purple-600" />
              </div>
            </div>
          </div>
        </div>

        {/* Filters and Search */}
        <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm mb-6">
          <div className="flex flex-col lg:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search by title, class, or subject..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-400"
                />
              </div>
            </div>

            {/* Filter by Status */}
            <div className="flex gap-2">
              <button
                onClick={() => setFilterStatus('all')}
                className={`px-4 py-3 rounded-lg font-medium transition-all ${
                  filterStatus === 'all'
                    ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/30'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                All
              </button>
              <button
                onClick={() => setFilterStatus('completed')}
                className={`px-4 py-3 rounded-lg font-medium transition-all ${
                  filterStatus === 'completed'
                    ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-500/30'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Completed
              </button>
              <button
                onClick={() => setFilterStatus('processing')}
                className={`px-4 py-3 rounded-lg font-medium transition-all ${
                  filterStatus === 'processing'
                    ? 'bg-amber-600 text-white shadow-lg shadow-amber-500/30'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Processing
              </button>
            </div>
          </div>
        </div>

        {/* Evaluations Table */}
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
          {/* Table Header */}
          <div className="bg-gradient-to-r from-gray-50 to-white px-6 py-4 border-b border-gray-200">
            <div className="grid grid-cols-12 gap-4 text-xs font-medium text-gray-600 uppercase tracking-wide">
              <div className="col-span-4">Evaluation Details</div>
              <div className="col-span-2">Status</div>
              <div className="col-span-2 text-center">Students</div>
              <div className="col-span-2 text-center">Avg Score</div>
              <div className="col-span-2 text-right">Actions</div>
            </div>
          </div>

          {/* Table Body */}
          <div className="divide-y divide-gray-200">
            {filteredEvaluations.length === 0 ? (
              <div className="text-center py-12">
                <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-600">No evaluations found</p>
              </div>
            ) : (
              filteredEvaluations.map((evaluation) => (
                <div
                  key={evaluation.id}
                  className="grid grid-cols-12 gap-4 px-6 py-5 hover:bg-gradient-to-r hover:from-blue-50 hover:to-indigo-50 transition-all group"
                >
                  {/* Details */}
                  <div className="col-span-4 flex items-center gap-4">
                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                      evaluation.status === 'completed' ? 'bg-emerald-100 text-emerald-600' :
                      evaluation.status === 'processing' ? 'bg-amber-100 text-amber-600' :
                      'bg-red-100 text-red-600'
                    }`}>
                      {getStatusIcon(evaluation.status)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-gray-900 truncate group-hover:text-blue-600 transition-colors">
                        {evaluation.title}
                      </h3>
                      <div className="flex items-center gap-2 text-sm text-gray-600 mt-1">
                        <span>{evaluation.class}</span>
                        <span>•</span>
                        <span className="text-xs bg-gray-100 px-2 py-0.5 rounded">
                          {evaluation.subject}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Status */}
                  <div className="col-span-2 flex items-center">
                    <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border ${getStatusColor(evaluation.status)}`}>
                      {getStatusIcon(evaluation.status)}
                      <span className="capitalize">{evaluation.status}</span>
                    </span>
                  </div>

                  {/* Students */}
                  <div className="col-span-2 flex items-center justify-center">
                    <div className="flex items-center gap-2">
                      <Users className="w-4 h-4 text-gray-400" />
                      <span className="font-semibold text-gray-900">{evaluation.students}</span>
                    </div>
                  </div>

                  {/* Avg Score */}
                  <div className="col-span-2 flex items-center justify-center">
                    {evaluation.avgScore !== null ? (
                      <div className="text-center">
                        <div className="text-lg font-bold text-gray-900">
                          {evaluation.avgScore}%
                        </div>
                        <div className="text-xs text-gray-500">
                          of {evaluation.maxScore}
                        </div>
                      </div>
                    ) : (
                      <span className="text-gray-400 text-sm">-</span>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="col-span-2 flex items-center justify-end gap-2">
                    <span className="text-xs text-gray-500">{evaluation.createdAt}</span>
                    <Link
                      href={`/dashboard/results?id=${evaluation.id}`}
                      className="w-9 h-9 rounded-lg bg-blue-50 border border-blue-200 flex items-center justify-center hover:bg-blue-100 transition-all group-hover:scale-110"
                    >
                      <Eye className="w-4 h-4 text-blue-600" />
                    </Link>
                    <button className="w-9 h-9 rounded-lg bg-gray-50 border border-gray-200 flex items-center justify-center hover:bg-gray-100 transition-all">
                      <Download className="w-4 h-4 text-gray-600" />
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Pagination Footer */}
          {filteredEvaluations.length > 0 && (
            <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex items-center justify-between">
              <div className="text-sm text-gray-600">
                Showing <span className="font-semibold text-gray-900">{filteredEvaluations.length}</span> of{' '}
                <span className="font-semibold text-gray-900">{allEvaluations.length}</span> evaluations
              </div>
              <div className="flex gap-2">
                <button className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-100 transition-all">
                  Previous
                </button>
                <button className="px-4 py-2 bg-blue-600 border border-blue-600 rounded-lg text-sm font-medium text-white hover:bg-blue-700 transition-all">
                  1
                </button>
                <button className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-100 transition-all">
                  Next
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
