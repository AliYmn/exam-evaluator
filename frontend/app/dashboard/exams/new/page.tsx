'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import DashboardLayout from '@/components/DashboardLayout';
import { Upload, FileText, ArrowLeft, CheckCircle2, AlertCircle } from 'lucide-react';
import Link from 'next/link';
import { examApi } from '@/lib/api';
import { useAuthStore } from '@/lib/store';

export default function NewExamPage() {
  const router = useRouter();
  const { token } = useAuthStore();

  const [examName, setExamName] = useState('');
  const [answerKey, setAnswerKey] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(false);

    // Validation
    if (!examName || !answerKey) {
      setError('Please fill in all fields');
      return;
    }

    if (examName.length < 3) {
      setError('Exam name must be at least 3 characters');
      return;
    }

    if (!answerKey.name.toLowerCase().endsWith('.pdf')) {
      setError('Answer key must be a PDF file');
      return;
    }

    if (!token) {
      setError('You must be logged in to create an exam');
      router.push('/login');
      return;
    }

    setLoading(true);

    try {
      // Call API to upload answer key
      const response = await examApi.uploadAnswerKey(token, examName, answerKey);

      console.log('Upload response:', response);
      setSuccess(true);

      // Show success message briefly, then redirect
      setTimeout(() => {
        router.push(`/dashboard/exams/${response.evaluation_id}`);
      }, 1500);

    } catch (err: any) {
      console.error('Upload error:', err);
      setError(err.message || 'Failed to create exam. Please try again.');
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

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="text-sm font-medium text-red-900 mb-1">Error</h3>
                <p className="text-sm text-red-800">{error}</p>
              </div>
            </div>
          )}

          {/* Success Message */}
          {success && (
            <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4 flex items-start gap-3">
              <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="text-sm font-medium text-emerald-900 mb-1">Success!</h3>
                <p className="text-sm text-emerald-800">
                  Answer key uploaded successfully. Processing in background...
                </p>
              </div>
            </div>
          )}

          {/* Info Box */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="text-sm font-medium text-blue-900 mb-2">ℹ️ Next Steps</h3>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• After creating the exam, you can upload student answer sheets</li>
              <li>• AI will parse the answer key and extract questions automatically</li>
              <li>• Each student paper will be evaluated against this answer key</li>
              <li>• You can add students anytime after creating the exam</li>
            </ul>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading || !examName || !answerKey}
            className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-4 rounded-lg font-medium hover:from-blue-700 hover:to-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-blue-500/30 flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
                <span>Creating Exam...</span>
              </>
            ) : (
              <>
                <Upload className="w-5 h-5" />
                <span>Create Exam</span>
              </>
            )}
          </button>
        </form>
      </div>
    </DashboardLayout>
  );
}
