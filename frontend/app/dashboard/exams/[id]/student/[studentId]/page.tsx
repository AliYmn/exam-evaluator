'use client';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import DashboardLayout from '@/components/DashboardLayout';
import { ArrowLeft, CheckCircle2, XCircle, AlertCircle, TrendingUp, TrendingDown, MessageSquare, Send, X } from 'lucide-react';
import Link from 'next/link';

export default function StudentResultPage() {
  const params = useParams();
  const examId = params.id as string;
  const studentId = params.studentId as string;

  const [chatMessages, setChatMessages] = useState<Array<{ role: 'user' | 'ai', message: string }>>([
    {
      role: 'ai',
      message: 'Hi! I\'m your AI assistant. Ask me anything about this student\'s performance, specific questions, or how to improve their score.'
    }
  ]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);

  // Mock data - gerçekte API'den gelecek
  const result = {
    student: {
      id: studentId,
      name: 'Ali Yılmaz',
      totalScore: 87,
      maxScore: 100,
      percentage: 87,
      evaluatedAt: '2024-01-15 10:30'
    },
    exam: {
      id: examId,
      name: 'Biology Midterm Exam'
    },
    questions: [
      {
        number: 1,
        studentAnswer: 'DNA is a double helix structure composed of nucleotides...',
        expectedAnswer: 'DNA is a double helix structure made of nucleotides containing adenine, thymine, cytosine, and guanine.',
        score: 9,
        maxScore: 10,
        feedback: 'Excellent answer! You correctly identified the structure. Minor improvement: mention the specific base pairs.',
        status: 'excellent'
      },
      {
        number: 2,
        studentAnswer: 'Mitosis has 4 stages',
        expectedAnswer: 'Mitosis consists of four main phases: prophase, metaphase, anaphase, and telophase. During these phases, the cell divides its nucleus.',
        score: 5,
        maxScore: 10,
        feedback: 'Partially correct. You identified the number of stages but did not name them or explain the process.',
        status: 'partial'
      },
      {
        number: 3,
        studentAnswer: 'Photosynthesis is the process where plants make food using sunlight, water, and carbon dioxide to produce glucose and oxygen.',
        expectedAnswer: 'Photosynthesis is the process by which plants convert light energy into chemical energy, using CO2 and H2O to produce glucose and O2.',
        score: 10,
        maxScore: 10,
        feedback: 'Perfect answer! Comprehensive and accurate explanation.',
        status: 'perfect'
      },
      {
        number: 4,
        studentAnswer: 'Ribosomes make proteins',
        expectedAnswer: 'Ribosomes are cellular organelles responsible for protein synthesis through translation of mRNA.',
        score: 6,
        maxScore: 10,
        feedback: 'Basic understanding shown but lacks detail about the mechanism (translation, mRNA).',
        status: 'partial'
      },
      {
        number: 5,
        studentAnswer: 'I dont know',
        expectedAnswer: 'The cell membrane is a selectively permeable barrier composed of a phospholipid bilayer with embedded proteins.',
        score: 0,
        maxScore: 10,
        feedback: 'No answer provided. Study the structure and function of cell membranes.',
        status: 'poor'
      }
    ],
    summary: {
      strengths: ['Strong understanding of DNA structure', 'Excellent grasp of photosynthesis'],
      weaknesses: ['Lacks detail in cellular processes', 'Needs improvement in organelle functions'],
      topicGaps: ['Cell membrane structure', 'Mitosis phases', 'Ribosome function details']
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'perfect': return 'bg-emerald-100 text-emerald-700 border-emerald-300';
      case 'excellent': return 'bg-blue-100 text-blue-700 border-blue-300';
      case 'partial': return 'bg-amber-100 text-amber-700 border-amber-300';
      case 'poor': return 'bg-red-100 text-red-700 border-red-300';
      default: return 'bg-gray-100 text-gray-700 border-gray-300';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'perfect':
      case 'excellent':
        return <CheckCircle2 className="w-5 h-5" />;
      case 'partial':
        return <AlertCircle className="w-5 h-5" />;
      case 'poor':
        return <XCircle className="w-5 h-5" />;
      default:
        return null;
    }
  };

  const handleSendMessage = async () => {
    if (!newMessage.trim()) return;

    setLoading(true);
    const userMsg = newMessage;
    setNewMessage('');

    // Add user message
    setChatMessages(prev => [...prev, { role: 'user', message: userMsg }]);

    try {
      // TODO: API call to backend
      // const response = await fetch('/api/chat', { ... });

      // Mock AI response
      setTimeout(() => {
        const mockResponse = `Based on the student's performance, I can help you with that. ${userMsg.includes('question') ? 'This question requires understanding of the fundamental concepts.' : 'The student shows good understanding in some areas but needs improvement in others.'}`;

        setChatMessages(prev => [...prev, { role: 'ai', message: mockResponse }]);
        setLoading(false);
      }, 1000);
    } catch (error) {
      setLoading(false);
      setChatMessages(prev => [...prev, { role: 'ai', message: 'Sorry, I encountered an error. Please try again.' }]);
    }
  };

  return (
    <DashboardLayout>
      <div>
        {/* Header */}
        <div className="mb-8">
          <Link
            href={`/dashboard/exams/${examId}`}
            className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to {result.exam.name}
          </Link>

          <div>
            <h1 className="text-3xl font-bold text-gray-900">{result.student.name}</h1>
            <p className="text-gray-600 mt-2">Evaluated on {result.student.evaluatedAt}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content - Questions */}
          <div className="lg:col-span-2 space-y-4">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Question Analysis</h2>

            {result.questions.map((q) => (
              <div key={q.number} className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
                {/* Header */}
                <div className="bg-gradient-to-r from-gray-50 to-white p-4 border-b border-gray-200 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center text-white font-bold shadow-lg shadow-blue-500/30">
                      {q.number}
                    </div>
                    <span className="font-semibold text-gray-900">Question {q.number}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(q.status)} flex items-center gap-1`}>
                      {getStatusIcon(q.status)}
                      {q.status}
                    </span>
                    <span className="text-2xl font-bold text-gray-900">
                      {q.score}<span className="text-sm text-gray-500">/{q.maxScore}</span>
                    </span>
                  </div>
                </div>

                {/* Content */}
                <div className="p-6 space-y-4">
                  {/* Student Answer */}
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <div className="w-2 h-2 rounded-full bg-blue-500"></div>
                      <span className="text-sm font-semibold text-gray-700 uppercase tracking-wider">Student Answer</span>
                    </div>
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <p className="text-gray-900">{q.studentAnswer}</p>
                    </div>
                  </div>

                  {/* Expected Answer */}
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
                      <span className="text-sm font-semibold text-gray-700 uppercase tracking-wider">Expected Answer</span>
                    </div>
                    <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4">
                      <p className="text-gray-900">{q.expectedAnswer}</p>
                    </div>
                  </div>

                  {/* AI Feedback */}
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <div className="w-2 h-2 rounded-full bg-indigo-500"></div>
                      <span className="text-sm font-semibold text-gray-700 uppercase tracking-wider">AI Feedback</span>
                    </div>
                    <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
                      <p className="text-gray-900 italic">{q.feedback}</p>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Sidebar - Summary */}
          <div className="lg:col-span-1">
            {/* Score Badge - Sticky */}
            <div className="sticky top-24 mb-6 z-10">
              <div className="bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl p-6 text-white shadow-xl shadow-blue-500/30">
                <div className="text-center">
                  <div className="text-5xl font-bold mb-1">{result.student.percentage}%</div>
                  <div className="text-blue-100 text-sm">
                    {result.student.totalScore} / {result.student.maxScore} points
                  </div>
                </div>
              </div>
            </div>

            {/* Performance Summary - Sticky */}
            <div className="sticky top-60 z-10">
              <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6 max-h-[calc(100vh-18rem)] overflow-y-auto">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Performance Summary</h3>

              {/* Strengths */}
              <div className="mb-6">
                <div className="flex items-center gap-2 mb-3">
                  <TrendingUp className="w-5 h-5 text-emerald-600" />
                  <span className="font-semibold text-gray-900">Strengths</span>
                </div>
                <ul className="space-y-2">
                  {result.summary.strengths.map((strength, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-sm text-gray-700">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 mt-0.5 flex-shrink-0" />
                      <span>{strength}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Weaknesses */}
              <div className="mb-6">
                <div className="flex items-center gap-2 mb-3">
                  <TrendingDown className="w-5 h-5 text-amber-600" />
                  <span className="font-semibold text-gray-900">Areas for Improvement</span>
                </div>
                <ul className="space-y-2">
                  {result.summary.weaknesses.map((weakness, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-sm text-gray-700">
                      <AlertCircle className="w-4 h-4 text-amber-600 mt-0.5 flex-shrink-0" />
                      <span>{weakness}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Topic Gaps */}
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <XCircle className="w-5 h-5 text-red-600" />
                  <span className="font-semibold text-gray-900">Topics to Review</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {result.summary.topicGaps.map((topic, idx) => (
                    <span key={idx} className="px-3 py-1 bg-red-50 text-red-700 rounded-full text-xs font-medium border border-red-200">
                      {topic}
                    </span>
                  ))}
                </div>
              </div>

                {/* Download Button */}
                <div className="mt-6 pt-6 border-t border-gray-200">
                  <button className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-3 rounded-lg font-medium hover:from-blue-700 hover:to-indigo-700 shadow-lg shadow-blue-500/30 transition">
                    Download Report PDF
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Floating Chat Button */}
        <button
          onClick={() => setIsChatOpen(!isChatOpen)}
          className="fixed bottom-6 right-6 w-16 h-16 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-full shadow-2xl hover:shadow-3xl hover:scale-110 transition-all z-40 flex items-center justify-center group"
        >
          <MessageSquare className="w-7 h-7 group-hover:scale-110 transition-transform" />
          {chatMessages.length > 1 && (
            <div className="absolute -top-1 -right-1 w-6 h-6 bg-red-500 rounded-full flex items-center justify-center text-xs font-bold animate-pulse">
              {chatMessages.length - 1}
            </div>
          )}
        </button>

        {/* Floating Chat Window */}
        <div className={`fixed bottom-24 right-6 w-96 bg-white rounded-2xl shadow-2xl border-2 border-gray-200 overflow-hidden z-50 transition-all duration-300 ${
          isChatOpen ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8 pointer-events-none'
        }`}>
          {/* Header */}
          <div className="bg-gradient-to-r from-indigo-600 to-purple-600 p-4 flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2 text-white">
                <MessageSquare className="w-5 h-5" />
                <h3 className="font-bold">AI Assistant</h3>
              </div>
              <p className="text-xs text-indigo-100 mt-1">Ask me about this evaluation</p>
            </div>
            <button
              onClick={() => setIsChatOpen(false)}
              className="text-white hover:bg-white/20 rounded-lg p-2 transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Chat Messages */}
          <div className="h-96 overflow-y-auto p-4 space-y-3 bg-gray-50">
            {chatMessages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] rounded-2xl px-4 py-3 ${
                  msg.role === 'user'
                    ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white'
                    : 'bg-white border border-gray-200 text-gray-900'
                }`}>
                  {msg.role === 'ai' && (
                    <div className="flex items-center gap-2 mb-2">
                      <div className="w-6 h-6 rounded-full bg-gradient-to-r from-indigo-500 to-purple-600 flex items-center justify-center">
                        <MessageSquare className="w-3 h-3 text-white" />
                      </div>
                      <span className="text-xs font-semibold text-gray-600">AI</span>
                    </div>
                  )}
                  <p className="text-sm leading-relaxed">{msg.message}</p>
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex justify-start">
                <div className="bg-white border border-gray-200 rounded-2xl px-4 py-3">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <div className="p-4 border-t-2 border-gray-200 bg-white">
            <div className="flex gap-2 mb-3">
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="Type your question..."
                className="flex-1 px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-gray-900 placeholder-gray-400 text-sm"
              />
              <button
                onClick={handleSendMessage}
                disabled={loading || !newMessage.trim()}
                className="px-4 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl hover:from-indigo-700 hover:to-purple-700 transition disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-indigo-500/30"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>

            {/* Quick Questions */}
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => setNewMessage('Why did the student lose points on Question 2?')}
                className="text-xs px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-full text-gray-700 transition"
              >
                💡 Why Q2?
              </button>
              <button
                onClick={() => setNewMessage('How can this student improve their score?')}
                className="text-xs px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-full text-gray-700 transition"
              >
                📈 Improve?
              </button>
              <button
                onClick={() => setNewMessage('What topics should they review?')}
                className="text-xs px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-full text-gray-700 transition"
              >
                📚 Review?
              </button>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
