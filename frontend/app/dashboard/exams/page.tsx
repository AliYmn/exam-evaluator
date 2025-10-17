'use client';

import { useRouter } from 'next/navigation';
import DashboardLayout from '@/components/DashboardLayout';
import { Plus, FileText, Users, Calendar } from 'lucide-react';
import Link from 'next/link';

export default function ExamsListPage() {
  const router = useRouter();

  // Mock data - gerçekte API'den gelecek
  const exams = [
    {
      id: '1',
      name: 'Biology Midterm Exam',
      createdAt: '2024-01-15',
      studentsCount: 12,
      completedCount: 10
    },
    {
      id: '2',
      name: 'Physics Final Exam',
      createdAt: '2024-01-18',
      studentsCount: 8,
      completedCount: 8
    },
    {
      id: '3',
      name: 'Math Quiz',
      createdAt: '2024-01-20',
      studentsCount: 5,
      completedCount: 3
    },
  ];

  return (
    <DashboardLayout>
      <div>
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Exams</h1>
            <p className="text-gray-600 mt-2">Manage your exam answer keys and student evaluations</p>
          </div>
          <Link
            href="/dashboard/exams/new"
            className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-3 rounded-xl font-medium hover:from-blue-700 hover:to-indigo-700 shadow-lg shadow-blue-500/30 transition"
          >
            <Plus className="w-5 h-5" />
            Create Exam
          </Link>
        </div>

        {/* Exams Grid */}
        {exams.length === 0 ? (
          <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-12 text-center">
            <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No exams yet</h3>
            <p className="text-gray-600 mb-6">Create your first exam to start evaluating students</p>
            <Link
              href="/dashboard/exams/new"
              className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-3 rounded-xl font-medium hover:from-blue-700 hover:to-indigo-700 shadow-lg shadow-blue-500/30"
            >
              <Plus className="w-5 h-5" />
              Create First Exam
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {exams.map((exam) => (
              <div
                key={exam.id}
                onClick={() => router.push(`/dashboard/exams/${exam.id}`)}
                className="bg-white rounded-xl shadow-lg border border-gray-200 p-6 hover:shadow-xl transition cursor-pointer group"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/30 group-hover:scale-110 transition">
                    <FileText className="w-6 h-6 text-white" />
                  </div>
                  <span className="px-3 py-1 bg-blue-100 text-blue-700 text-xs font-medium rounded-full">
                    {exam.completedCount}/{exam.studentsCount} evaluated
                  </span>
                </div>

                <h3 className="text-lg font-bold text-gray-900 mb-3 group-hover:text-blue-600 transition">
                  {exam.name}
                </h3>

                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Calendar className="w-4 h-4" />
                    <span>Created: {exam.createdAt}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Users className="w-4 h-4" />
                    <span>{exam.studentsCount} students</span>
                  </div>
                </div>

                <div className="mt-4 pt-4 border-t border-gray-200">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Progress</span>
                    <span className="font-medium text-gray-900">
                      {Math.round((exam.completedCount / exam.studentsCount) * 100)}%
                    </span>
                  </div>
                  <div className="mt-2 h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-blue-500 to-indigo-600"
                      style={{ width: `${(exam.completedCount / exam.studentsCount) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
