'use client';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import DashboardLayout from '@/components/DashboardLayout';
import { Upload, FileText, ArrowLeft, CheckCircle2, Clock, User, Plus } from 'lucide-react';
import Link from 'next/link';

export default function ExamDetailPage() {
  const params = useParams();
  const examId = params.id as string;

  const [studentFile, setStudentFile] = useState<File | null>(null);
  const [studentName, setStudentName] = useState('');
  const [loading, setLoading] = useState(false);

  // Mock data - gerçekte API'den gelecek
  const exam = {
    id: examId,
    name: 'Biology Midterm Exam',
    answerKey: 'biology_answer_key.pdf',
    createdAt: '2024-01-15',
    students: [
      { id: 1, name: 'Ali Yılmaz', status: 'completed', score: 87, uploadedAt: '2024-01-15 10:30' },
      { id: 2, name: 'Ayşe Kaya', status: 'processing', score: null, uploadedAt: '2024-01-15 11:45' },
      { id: 3, name: 'Mehmet Demir', status: 'completed', score: 92, uploadedAt: '2024-01-15 09:15' },
    ]
  };

  const handleUploadStudent = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!studentName || !studentFile) {
      alert('Please fill in all fields');
      return;
    }

    setLoading(true);

    try {
      // TODO: API call
      // const formData = new FormData();
      // formData.append('student_name', studentName);
      // formData.append('student_file', studentFile);
      // await fetch(`/api/exam/${examId}/upload-student`, { method: 'POST', body: formData });

      // Mock success
      setTimeout(() => {
        setStudentName('');
        setStudentFile(null);
        alert('Student paper uploaded successfully!');
      }, 1000);
    } catch (error) {
      alert('Failed to upload student paper');
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout>
      <div>
        {/* Header */}
        <div className="mb-8">
          <Link
            href="/dashboard/exams"
            className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Exams
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">{exam.name}</h1>
          <p className="text-gray-600 mt-2">
            Answer Key: {exam.answerKey} • Created: {exam.createdAt}
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Upload Student Paper Form */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200 sticky top-6">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
                  <Plus className="w-5 h-5 text-white" />
                </div>
                <h2 className="text-lg font-bold text-gray-900">Add Student</h2>
              </div>

              <form onSubmit={handleUploadStudent} className="space-y-4">
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
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center hover:border-blue-500 transition">
                    <input
                      type="file"
                      id="student-file"
                      accept=".pdf"
                      onChange={(e) => e.target.files && setStudentFile(e.target.files[0])}
                      className="hidden"
                    />
                    <label htmlFor="student-file" className="cursor-pointer">
                      {studentFile ? (
                        <div className="flex items-center gap-2">
                          <FileText className="w-5 h-5 text-blue-600" />
                          <span className="text-sm text-gray-900">{studentFile.name}</span>
                        </div>
                      ) : (
                        <>
                          <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                          <p className="text-xs text-gray-600">Click to upload</p>
                        </>
                      )}
                    </label>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading || !studentName || !studentFile}
                  className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-3 rounded-lg font-medium hover:from-blue-700 hover:to-indigo-700 transition disabled:opacity-50 shadow-lg shadow-blue-500/30"
                >
                  {loading ? 'Uploading...' : 'Upload & Evaluate'}
                </button>
              </form>
            </div>
          </div>

          {/* Students List */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-lg border border-gray-200">
              <div className="p-6 border-b border-gray-200">
                <h2 className="text-xl font-bold text-gray-900">Students ({exam.students.length})</h2>
              </div>

              <div className="p-6">
                {exam.students.length === 0 ? (
                  <div className="text-center py-12">
                    <User className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <p className="text-gray-600">No students added yet</p>
                    <p className="text-sm text-gray-500 mt-2">Upload student papers to begin evaluation</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {exam.students.map((student) => (
                      <Link
                        key={student.id}
                        href={student.status === 'completed' ? `/dashboard/exams/${examId}/student/${student.id}` : '#'}
                        className={`flex items-center justify-between p-4 bg-gray-50 rounded-lg transition ${
                          student.status === 'completed'
                            ? 'hover:bg-gradient-to-r hover:from-blue-50 hover:to-indigo-50 cursor-pointer hover:shadow-md'
                            : 'cursor-not-allowed opacity-75'
                        }`}
                      >
                        <div className="flex items-center gap-4">
                          <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                            student.status === 'completed'
                              ? 'bg-emerald-100 text-emerald-600'
                              : 'bg-amber-100 text-amber-600'
                          }`}>
                            {student.status === 'completed' ? (
                              <CheckCircle2 className="w-5 h-5" />
                            ) : (
                              <Clock className="w-5 h-5 animate-pulse" />
                            )}
                          </div>

                          <div>
                            <h3 className="font-semibold text-gray-900">{student.name}</h3>
                            <p className="text-sm text-gray-500">{student.uploadedAt}</p>
                          </div>
                        </div>

                        <div className="flex items-center gap-4">
                          {student.score !== null && (
                            <div className="text-right">
                              <p className="text-2xl font-bold text-emerald-600">{student.score}%</p>
                              <p className="text-xs text-gray-500">Score</p>
                            </div>
                          )}
                          <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                            student.status === 'completed'
                              ? 'bg-emerald-100 text-emerald-700'
                              : 'bg-amber-100 text-amber-700'
                          }`}>
                            {student.status}
                          </span>
                        </div>
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
