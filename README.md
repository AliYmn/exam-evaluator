# 🎓 Exam Evaluator - AI-Powered Assessment System

**Agentic AI-based exam evaluation system** that automatically scores student exams, provides detailed feedback, and analyzes performance using LangGraph and Google Gemini.

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.119-green.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2.56-red.svg)](https://langchain-ai.github.io/langgraph/)
[![Next.js](https://img.shields.io/badge/Next.js-15.5-black.svg)](https://nextjs.org/)

---

## 🎯 What This Project Does

Upload **answer key PDF** → Upload **student answer sheet PDF** → Get **AI evaluation** with scores, Turkish feedback, and performance analysis.

### Demo Credentials
```
Email: demo@demo.com
Password: demo12345!
```

---

## 🤖 Key Features (Agentic Architecture)

### ✅ Multi-Step Reasoning (ReAct Pattern)
- Agent thinks → chooses tools → executes → observes → repeats
- **Stateful workflow** with LangGraph state machine
- **Tool calling**: parse_answer_key, parse_student_answer, evaluate_answer, analyze_performance

### ✅ Self-Correction Mechanism
- **Quality check node** reviews every evaluation
- Automatically retries if quality is low (max 2 retries)
- Ensures fair and consistent scoring

### ✅ Confidence Scoring
- Every evaluation includes **confidence score (0-1)**
- Low confidence → flags for human review
- **Reasoning trace**: Shows AI's thought process

### ✅ AI-Driven Features
- **Question-level scoring** (0-10 points per question)
- **Turkish feedback** with detailed explanations
- **Strengths & weaknesses** analysis
- **Follow-up Q&A chat** with context awareness

### ✅ Real-time Progress
- **SSE streaming** for live updates
- Background processing with **Celery**
- Progress percentage tracking

---

## 🏗️ Architecture

```
┌─────────────────┐
│   Next.js UI    │  ← Modern React frontend
└────────┬────────┘
         │ JWT Auth
         ▼
┌─────────────────┐
│   FastAPI       │  ← REST API + SSE
│   Auth Service  │
└─────────────────┘

┌─────────────────┐
│   FastAPI       │  ← Main evaluation service
│ Content Service │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LangGraph      │  ← Agentic AI workflow
│  Agent System   │     • Reasoning Node
│                 │     • Tool Execution Node
│                 │     • Quality Check Node
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Celery Workers  │  ← Background tasks
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  PostgreSQL     │  ← Database
│  Redis          │  ← Caching + Progress
│  RabbitMQ       │  ← Message broker
└─────────────────┘
```

### Agent Workflow (LangGraph State Machine)

```
Entry
  │
  ▼
[Reasoning Node]  ← Agent thinks: "What task? Which tool?"
  │
  ▼
[Tool Execution]  ← Executes: parse_answer_key_tool()
  │
  ▼
[Quality Check]   ← Reviews output quality
  │
  ├─→ Issues? → Retry (max 2x) → Back to Reasoning
  │
  └─→ OK? → END
```

### Modular Code Structure

```
backend/content_service/core/agents/
├── exam_agent.py    # Main agent interface
├── models.py        # Pydantic schemas (type-safe)
├── state.py         # AgentState definition
├── tools.py         # LangChain tools (5 tools)
├── nodes.py         # Graph nodes (reasoning, execution, QC)
└── workflow.py      # LangGraph workflow definition
```

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Gemini API Key ([Get it free](https://ai.google.dev/))

### 1. Clone & Setup
```bash
git clone https://github.com/AliYmn/exam-evaluator.git
cd exam-evaluator

# Create .env file
cp .env.example .env
# Add your GEMINI_API_KEY to .env
```

### 2. Run with Docker (One Command!)
```bash
make build && make up
```

### 3. Access Points
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001/docs (Swagger)
- **Auth API**: http://localhost:8004/docs
- **Celery Monitor**: http://localhost:5555

---

## 📖 API Usage Example

### 1. Login
```bash
POST /api/v1/auth/login
{
  "email": "demo@demo.com",
  "password": "demo12345!"
}
# Returns: { "access_token": "..." }
```

### 2. Upload Answer Key (PDF)
```bash
POST /api/v1/exam/upload-answer-key
Headers: Authorization: Bearer {token}
Form Data:
  - exam_title: "Biology Midterm"
  - answer_key: answer_key.pdf

# Returns: { "evaluation_id": "eval_abc123", "status": "pending" }
```

### 3. Upload Student Sheet (PDF)
```bash
POST /api/v1/exam/{evaluation_id}/upload-student-sheet
Headers: Authorization: Bearer {token}
Form Data:
  - student_name: "Alice Johnson"
  - student_sheet: student_answers.pdf

# AI automatically evaluates in background
```

### 4. Get Results
```bash
GET /api/v1/exam/student/{student_response_id}
Headers: Authorization: Bearer {token}

# Returns:
{
  "student_name": "Alice Johnson",
  "total_score": 42.5,
  "max_score": 50.0,
  "percentage": 85.0,
  "strengths": ["Detailed explanations", "Good examples"],
  "weaknesses": ["Missing context in Q3"],
  "questions": [
    {
      "question_number": 1,
      "score": 8.5,
      "max_score": 10.0,
      "feedback": "Excellent answer. Key concepts are correct.",
      "confidence": 0.9,  // AI's confidence in this score
      "reasoning": "Core concepts accurate, minor detail missing"
    }
  ]
}
```

### 5. Chat (Follow-up Questions)
```bash
POST /api/v1/exam/student/{student_response_id}/chat
{
  "question": "What should the student improve?"
}
# Returns: { "answer": "The student should focus on..." }
```

### 6. Real-time Progress (SSE)
```javascript
const eventSource = new EventSource(
  `/api/v1/exam/${evalId}/progress-stream?token=${token}`
);

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(`${data.percentage}% - ${data.message}`);
};
```

---

## 🧠 Agentic System Details

### Tools (LangChain)
1. **parse_answer_key_tool**: Extracts questions & answers from PDF
2. **parse_student_answer_tool**: Extracts student responses
3. **evaluate_answer_tool**: Scores + feedback + confidence
4. **quality_check_tool**: Self-correction validation
5. **analyze_performance_tool**: Strengths/weaknesses extraction

### Agent State (LangGraph)
```python
AgentState:
  - task: str                    # Current task (e.g., "evaluate_student")
  - pdf_text: str                # Input data
  - thoughts: List[str]          # Agent's reasoning process
  - actions: List[str]           # Actions taken
  - observations: List[str]      # Results observed
  - retry_count: int             # Retry attempts
  - confidence_scores: List[float]
  - tool_call_logs: List[Dict]   # Transparency
```

### Self-Correction Flow
```python
1. Evaluate answer → Get score + feedback
2. Quality check → Analyze if fair & consistent
3. If issues found:
   - Log the problem
   - Increment retry_count
   - Return to reasoning node
   - Try again (max 2 retries)
4. If quality OK → Proceed to next question
```

---

## 🛠️ Development

### Useful Commands
```bash
make build          # Build containers
make up             # Start all services
make down           # Stop all services
make logs           # View logs
make migrate        # Run DB migrations
```

### Tech Stack Summary
- **Backend**: FastAPI, LangGraph, LangChain, Celery
- **Database**: PostgreSQL, Redis, RabbitMQ
- **AI**: Google Gemini 2.0 Flash
- **Frontend**: Next.js 15, TypeScript, Tailwind CSS
- **Deployment**: Docker Compose

---

## 📊 Project Highlights

✅ **Agentic AI**: ReAct pattern with multi-step reasoning
✅ **Self-Correction**: Quality checks with automatic retry
✅ **Confidence Scores**: Transparency in AI decisions
✅ **Modular Design**: Clean separation (agents, tools, nodes)
✅ **Real-time Updates**: SSE streaming for progress
✅ **Production-Ready**: JWT auth, rate limiting, error handling
✅ **Type-Safe**: Pydantic schemas everywhere
✅ **Async**: FastAPI + SQLAlchemy async

---

## 📝 License

MIT License - See [LICENSE](LICENSE) file

## 👤 Author

**Ali Yaman** - [GitHub](https://github.com/AliYmn/exam-evaluator)

---

**Built with ❤️ and 🤖 AI**

*An intelligent, self-correcting exam evaluation system powered by LangGraph*
