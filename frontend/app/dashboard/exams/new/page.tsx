'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import DashboardLayout from '@/components/DashboardLayout';
import { Upload, FileText, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function NewExamPage() {
  const router = useRouter();
  const [examName, setExamName] = useState('');
  const [answerKey, setAnswerKey] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!examName || !answerKey) {
      alert('Please fill in all fields');
      return;
    }

    setLoading(true);

    try {
      // TODO: API call to create exam
      // const formData = new FormData();
      // formData.append('exam_name', examName);
      // formData.append('answer_key', answerKey);
      // const response = await fetch('/api/exam/create', { method: 'POST', body: formData });
      // const data = await response.json();
      // router.push(`/dashboard/exams/${data.exam_id}`);

      // Temporary mock
      setTimeout(() => {
        router.push('/dashboard/exams/mock-exam-id');
      }, 1000);
    } catch (error) {
      alert('Failed to create exam');
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Link
            href="/dashboard/exams"
            className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Exams
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">Create New Exam</h1>
          <p className="text-gray-600 mt-2">Set up your exam and upload the answer key</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Exam Name */}
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
            <label className="block text-sm font-medium text-gray-900 mb-2">
              Exam Name
            </label>
            <input
              type="text"
              value={examName}
              onChange={(e) => setExamName(e.target.value)}
              placeholder="e.g., Biology Midterm Exam"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-400"
            />
          </div>

          {/* Answer Key Upload */}
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
            <label className="block text-sm font-medium text-gray-900 mb-4">
              Answer Key (PDF)
            </label>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-500 transition">
              <input
                type="file"
                id="answer-key"
                accept=".pdf"
                onChange={(e) => e.target.files && setAnswerKey(e.target.files[0])}
                className="hidden"
              />
              <label htmlFor="answer-key" className="cursor-pointer">
                {answerKey ? (
                  <div className="flex items-center justify-center gap-3">
                    <FileText className="w-8 h-8 text-blue-600" />
                    <div className="text-left">
                      <p className="text-sm font-medium text-gray-900">{answerKey.name}</p>
                      <p className="text-xs text-gray-500">
                        {(answerKey.size / 1024).toFixed(2)} KB
                      </p>
                    </div>
                  </div>
                ) : (
                  <>
                    <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-sm font-medium text-gray-900 mb-1">
                      Upload Answer Key PDF
                    </p>
                    <p className="text-xs text-gray-500">Click to browse or drag and drop</p>
                  </>
                )}
              </label>
            </div>
          </div>

          {/* Info Box */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="text-sm font-medium text-blue-900 mb-2">ℹ️ Next Steps</h3>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• After creating the exam, you can upload student answer sheets</li>
              <li>• Each student paper will be evaluated against this answer key</li>
              <li>• You can add students anytime after creating the exam</li>
            </ul>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading || !examName || !answerKey}
            className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-4 rounded-lg font-medium hover:from-blue-700 hover:to-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-blue-500/30"
          >
            {loading ? 'Creating Exam...' : 'Create Exam'}
          </button>
        </form>
      </div>
    </DashboardLayout>
  );
}
