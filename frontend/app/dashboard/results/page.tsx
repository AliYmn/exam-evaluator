'use client';

import { useState, useEffect } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { MessageCircle, Send, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { examAPI } from '@/lib/api';

export default function ResultsPage() {
  const [results, setResults] = useState<any>(null);
  const [chatMessages, setChatMessages] = useState<
    Array<{ role: 'user' | 'assistant'; content: string }>
  >([]);
  const [chatInput, setChatInput] = useState('');

  useEffect(() => {
    // Load dummy results
    examAPI.getResults('dummy-123').then(setResults);
  }, []);

  const handleChatSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    const userMessage = chatInput;
    setChatMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setChatInput('');

    // Simulate AI response
    setTimeout(() => {
      let response = '';
      if (userMessage.toLowerCase().includes('question 2') || userMessage.toLowerCase().includes('q2')) {
        response =
          'For Question 2, the student received 7/10 points because while they correctly identified DNA as genetic material, they did not elaborate on its structure (double helix) or function in detail. A more complete answer would include information about nucleotides, base pairs, and how DNA stores hereditary information.';
      } else if (
        userMessage.toLowerCase().includes('improve') ||
        userMessage.toLowerCase().includes('better')
      ) {
        response =
          'To improve the score, the student should: 1) Provide more detailed explanations, 2) Include scientific terminology where appropriate, 3) Explain processes step-by-step, and 4) Connect concepts to real-world examples when relevant.';
      } else {
        response =
          "I can help you understand the grading. You can ask questions like 'Why did question 2 get 7 points?' or 'How can the student improve their score?'";
      }

      setChatMessages((prev) => [...prev, { role: 'assistant', content: response }]);
    }, 1000);
  };

  if (!results) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-96">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-600"></div>
        </div>
      </DashboardLayout>
    );
  }

  const scorePercentage = (results.total_score / results.max_score) * 100;

  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Evaluation Results</h1>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Results Section */}
          <div className="lg:col-span-2 space-y-6">
            {/* Summary Card */}
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Student Summary</h2>
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h3 className="text-2xl font-bold text-gray-900">{results.student_name}</h3>
                  <p className="text-gray-600">Biology Midterm Exam</p>
                </div>
                <div className="text-right">
                  <p className="text-4xl font-bold text-indigo-600">
                    {results.total_score}/{results.max_score}
                  </p>
                  <p className="text-sm text-gray-600">{scorePercentage.toFixed(0)}%</p>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="mb-4">
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className="bg-indigo-600 h-3 rounded-full transition-all"
                    style={{ width: `${scorePercentage}%` }}
                  ></div>
                </div>
              </div>

              {/* Overall Feedback */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="font-medium text-blue-900 mb-2">Overall Feedback</h4>
                <p className="text-sm text-blue-800">{results.summary}</p>
              </div>
            </div>

            {/* Question Breakdown */}
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Question Breakdown</h2>
              <div className="space-y-4">
                {results.questions.map((q: any) => (
                  <div key={q.question_number} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-semibold text-gray-900">Question {q.question_number}</h3>
                      <div className="flex items-center gap-2">
                        <span className="text-lg font-bold text-indigo-600">
                          {q.score}/{q.max_score}
                        </span>
                        {q.score === q.max_score ? (
                          <CheckCircle className="w-5 h-5 text-green-500" />
                        ) : q.score >= q.max_score * 0.7 ? (
                          <AlertCircle className="w-5 h-5 text-yellow-500" />
                        ) : (
                          <XCircle className="w-5 h-5 text-red-500" />
                        )}
                      </div>
                    </div>

                    <div className="space-y-3">
                      <div>
                        <p className="text-xs font-medium text-gray-500 uppercase mb-1">
                          Student Answer
                        </p>
                        <p className="text-sm text-gray-700 bg-gray-50 p-3 rounded">
                          {q.student_answer}
                        </p>
                      </div>

                      <div>
                        <p className="text-xs font-medium text-gray-500 uppercase mb-1">
                          Expected Answer
                        </p>
                        <p className="text-sm text-gray-700 bg-green-50 p-3 rounded">
                          {q.expected_answer}
                        </p>
                      </div>

                      <div>
                        <p className="text-xs font-medium text-gray-500 uppercase mb-1">
                          AI Feedback
                        </p>
                        <p className="text-sm text-gray-700 bg-blue-50 p-3 rounded">{q.feedback}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Chat Section */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 sticky top-8">
              <div className="p-4 border-b border-gray-200 flex items-center gap-3">
                <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center">
                  <MessageCircle className="w-5 h-5 text-indigo-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">Ask Questions</h3>
                  <p className="text-xs text-gray-600">Get detailed explanations</p>
                </div>
              </div>

              <div className="h-96 overflow-y-auto p-4 space-y-4">
                {chatMessages.length === 0 ? (
                  <div className="text-center text-gray-500 text-sm py-8">
                    <MessageCircle className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                    <p>Ask about specific questions or</p>
                    <p>how to improve the score</p>
                  </div>
                ) : (
                  chatMessages.map((msg, idx) => (
                    <div
                      key={idx}
                      className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[80%] rounded-lg p-3 ${
                          msg.role === 'user'
                            ? 'bg-indigo-600 text-white'
                            : 'bg-gray-100 text-gray-900'
                        }`}
                      >
                        <p className="text-sm">{msg.content}</p>
                      </div>
                    </div>
                  ))
                )}
              </div>

              <form onSubmit={handleChatSubmit} className="p-4 border-t border-gray-200">
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    placeholder="Ask a question..."
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm"
                  />
                  <button
                    type="submit"
                    className="bg-indigo-600 text-white p-2 rounded-lg hover:bg-indigo-700 transition"
                  >
                    <Send className="w-5 h-5" />
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
