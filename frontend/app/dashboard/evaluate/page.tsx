'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import DashboardLayout from '@/components/DashboardLayout';
import { Upload, FileText, X } from 'lucide-react';
import toast from 'react-hot-toast';
import { examAPI } from '@/lib/api';

export default function EvaluatePage() {
  const router = useRouter();
  const [answerKey, setAnswerKey] = useState<File | null>(null);
  const [studentSheets, setStudentSheets] = useState<File[]>([]);
  const [loading, setLoading] = useState(false);

  const handleAnswerKeyChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setAnswerKey(e.target.files[0]);
    }
  };

  const handleStudentSheetsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setStudentSheets(Array.from(e.target.files));
    }
  };

  const removeStudentSheet = (index: number) => {
    setStudentSheets(studentSheets.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!answerKey || studentSheets.length === 0) {
      toast.error('Please upload answer key and at least one student sheet');
      return;
    }

    setLoading(true);

    try {
      const formData = new FormData();
      formData.append('answer_key', answerKey);
      studentSheets.forEach((sheet) => {
        formData.append('student_sheets', sheet);
      });

      await examAPI.uploadFiles(formData);
      toast.success('Evaluation started! Redirecting to results...');
      setTimeout(() => {
        router.push('/dashboard/results');
      }, 1500);
    } catch (error) {
      toast.error('Failed to start evaluation');
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">New Evaluation</h1>
          <p className="text-gray-600 mt-2">Upload exam files to start AI-powered evaluation</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Answer Key Upload */}
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Answer Key</h2>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-indigo-500 transition">
              <input
                type="file"
                id="answer-key"
                accept=".pdf"
                onChange={handleAnswerKeyChange}
                className="hidden"
              />
              <label htmlFor="answer-key" className="cursor-pointer">
                <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-sm font-medium text-gray-900 mb-1">
                  {answerKey ? answerKey.name : 'Upload Answer Key PDF'}
                </p>
                <p className="text-xs text-gray-500">Click to browse or drag and drop</p>
              </label>
            </div>
          </div>

          {/* Student Sheets Upload */}
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Student Answer Sheets</h2>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-indigo-500 transition mb-4">
              <input
                type="file"
                id="student-sheets"
                accept=".pdf"
                multiple
                onChange={handleStudentSheetsChange}
                className="hidden"
              />
              <label htmlFor="student-sheets" className="cursor-pointer">
                <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-sm font-medium text-gray-900 mb-1">
                  Upload Student Sheets (Multiple PDFs)
                </p>
                <p className="text-xs text-gray-500">Click to browse or drag and drop</p>
              </label>
            </div>

            {/* Uploaded Files List */}
            {studentSheets.length > 0 && (
              <div className="space-y-2">
                <p className="text-sm font-medium text-gray-700 mb-2">
                  {studentSheets.length} file(s) selected:
                </p>
                {studentSheets.map((file, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <div className="flex items-center gap-3">
                      <FileText className="w-5 h-5 text-indigo-600" />
                      <span className="text-sm text-gray-900">{file.name}</span>
                    </div>
                    <button
                      type="button"
                      onClick={() => removeStudentSheet(index)}
                      className="text-red-500 hover:text-red-700 transition"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading || !answerKey || studentSheets.length === 0}
            className="w-full bg-indigo-600 text-white py-4 rounded-lg font-medium hover:bg-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Starting Evaluation...' : 'Start Evaluation'}
          </button>

          {/* Info Box */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="text-sm font-medium text-blue-900 mb-2">💡 How it works</h3>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Upload your answer key with correct answers and grading scheme</li>
              <li>• Upload one or more student answer sheets</li>
              <li>• AI will evaluate each answer question by question</li>
              <li>• Get detailed feedback and scores within minutes</li>
            </ul>
          </div>
        </form>
      </div>
    </DashboardLayout>
  );
}
