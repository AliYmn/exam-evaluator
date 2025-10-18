# 🎓 Exam Evaluator - AI-Powered Assessment System

**Agentic AI-based exam evaluation system** that automatically scores student exams, provides detailed feedback, and analyzes performance using LangGraph and Google Gemini.

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.119-green.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2.56-red.svg)](https://langchain-ai.github.io/langgraph/)
[![Next.js](https://img.shields.io/badge/Next.js-15.5-black.svg)](https://nextjs.org/)

---

## 📋 Table of Contents

1. [What This Does](#-what-this-does)
2. [Key Features](#-key-features-agentic-architecture)
3. [Setup & Run](#-setup--run-instructions)
4. [Architecture Overview](#-architecture-overview)
5. [Grading & Feedback Logic](#-grading--feedback-logic)
6. [Follow-up Query Handling](#-follow-up-query-handling)
7. [API Usage](#-api-usage)
8. [Known Limitations](#-known-limitations--assumptions)
9. [Tech Stack](#-tech-stack)

---

## 🎯 What This Does

Upload **answer key PDF** → Upload **student answer sheet PDF** → Get **AI evaluation** with:
- Question-level scores (0-10 per question)
- Detailed Turkish feedback explaining each score
- Overall performance analysis (strengths/weaknesses)
- AI-powered Q&A chat about student performance

---

## 🤖 Key Features (Agentic Architecture)

### ✅ Multi-Step Reasoning (ReAct Pattern)
Agent iteratively thinks → chooses tools → executes → observes → repeats until task is complete.

### ✅ Self-Correction Mechanism
- **Quality check node** reviews every evaluation for fairness and consistency
- Automatically retries if quality is low (max 2 retries)
- Ensures accurate scoring

### ✅ Confidence Scoring
- Every evaluation includes **confidence score (0-1)**
- Low confidence → flags for human review
- **Reasoning trace**: Shows AI's decision-making process

### ✅ Real-time Progress
- **SSE (Server-Sent Events)** streaming for live updates
- Background processing with **Celery**
- Detailed progress percentage tracking

---

## 🚀 Setup & Run Instructions

### Prerequisites
- **Docker & Docker Compose** (required)
- **Gemini API Key** ([Get it free](https://ai.google.dev/))

### Step 1: Clone Repository
```bash
git clone https://github.com/AliYmn/exam-evaluator.git
cd exam-evaluator
```

### Step 2: Configure Environment
```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your Gemini API key
GEMINI_API_KEY=your_api_key_here
```

**Required Environment Variables:**
```bash
# Gemini API (REQUIRED)
GEMINI_API_KEY=your_gemini_api_key

# Database
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=redis_password_123

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 days
```

### Step 3: Build & Run (One Command!)
```bash
make build && make up
```

**Alternative (without Makefile):**
```bash
docker-compose build
docker-compose up -d
```

### Step 4: Access Application
- **Frontend**: http://localhost:3000
- **Backend API Docs**: http://localhost:8001/docs
- **Auth API Docs**: http://localhost:8004/docs
- **Celery Monitor**: http://localhost:5555

### Step 5: Run Database Migrations
```bash
make migrate
```

### Useful Commands
```bash
make logs          # View all logs
make down          # Stop all services
make restart       # Restart services
make ps            # Show running containers
```

---

## 🏗️ Architecture Overview

### High-Level System Architecture

```
                    ┌──────────────┐
                    │     USER     │
                    └──────┬───────┘
                           │
                           ▼
              ┌────────────────────────┐
              │   Next.js Frontend     │
              │ (TypeScript + Tailwind)│
              └───────────┬────────────┘
                          │ JWT Auth
                          ▼
              ┌────────────────────────┐
              │  FastAPI Auth Service  │
              │      (Port 8004)       │
              └────────────────────────┘
                          │
                          ▼
              ┌────────────────────────┐
              │ FastAPI Content Service│
              │      (Port 8001)       │
              │  • Upload endpoints    │
              │  • SSE streaming       │
              │  • Chat API            │
              └───────────┬────────────┘
                          │
                          ▼
              ┌────────────────────────┐
              │    Celery Workers      │
              │ (Background Processing)│
              │  • PDF parsing         │
              │  • Evaluation          │
              └───────────┬────────────┘
                          │
                          ▼
        ┌─────────────────────────────────┐
        │    LangGraph Agent System       │
        │     (Agentic AI Workflow)       │
        │                                 │
        │    ┌─────────────────┐         │
        │    │ Reasoning Node  │         │
        │    │ (Decide action) │         │
        │    └────────┬────────┘         │
        │             │                   │
        │             ▼                   │
        │    ┌─────────────────┐         │
        │    │ Tool Execution  │         │
        │    │(Parse, Evaluate)│         │
        │    └────────┬────────┘         │
        │             │                   │
        │             ▼                   │
        │    ┌─────────────────┐         │
        │    │ Quality Check   │         │
        │    │ (Self-Correct)  │         │
        │    └────────┬────────┘         │
        │             │                   │
        │      ┌──────┴──────┐           │
        │      │             │           │
        │   Issues?        OK?           │
        │      │             │           │
        │   Retry         END            │
        │  (max 2x)                      │
        └─────────────────────────────────┘
                          │
                          ▼
              ┌────────────────────────┐
              │  PostgreSQL Database   │
              │  Redis (Cache + SSE)   │
              │ RabbitMQ (Msg Broker)  │
              └────────────────────────┘
```

### Agent Workflow (LangGraph State Machine)

```
                    [ ENTRY ]
                        │
                        ▼
            ┌───────────────────────┐
            │   REASONING NODE      │
            │                       │
            │  • Analyze task       │
            │  • Choose tool        │
            │  • Plan action        │
            └───────────┬───────────┘
                        │
                        ▼
            ┌───────────────────────┐
            │  TOOL EXECUTION NODE  │
            │                       │
            │  • parse_answer_key   │
            │  • parse_student_ans  │
            │  • evaluate_answer    │
            │  • analyze_performance│
            └───────────┬───────────┘
                        │
                        ▼
                 ┌──────────┐
                 │ Is task  │
                 │ evaluate?│
                 └────┬─────┘
                      │
            ┌─────────┴─────────┐
            NO                 YES
            │                   │
            ▼                   ▼
        [ END ]     ┌───────────────────────┐
                    │  QUALITY CHECK NODE   │
                    │                       │
                    │  • Review scoring     │
                    │  • Check consistency  │
                    │  • Validate feedback  │
                    └───────────┬───────────┘
                                │
                         ┌──────┴──────┐
                         │ Issues?     │
                         └──────┬──────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
                    ▼                       ▼
            Issues Found?              No Issues?
            & retry < 2                     │
                    │                       │
                    │                       ▼
                    │                   [ END ]
                    │
                    └─────► Back to REASONING
                            (Retry evaluation)
```

### Modular Code Structure

```
backend/content_service/core/agents/
├── exam_agent.py    # Main agent orchestration + chat
├── models.py        # Pydantic schemas (type-safe)
├── state.py         # AgentState definition
├── tools.py         # 5 LangChain tools
├── nodes.py         # 3 graph nodes (reasoning, execution, QC)
└── workflow.py      # LangGraph workflow definition
```

---

## 📊 Grading & Feedback Logic

### 1. Answer Key Parsing
**Tool:** `parse_answer_key_tool`

**Process:**
1. Extract text from PDF using PyPDF
2. Clean text (remove null bytes, special chars)
3. Send to Gemini with structured prompt
4. Parse response into structured JSON:
   ```json
   {
     "questions": [
       {
         "number": 1,
         "question_text": "What is photosynthesis?",
         "expected_answer": "Photosynthesis is...",
         "max_score": 10,
         "keywords": ["light", "chlorophyll", "energy"]
       }
     ],
     "total_questions": 5,
     "max_possible_score": 50
   }
   ```

### 2. Student Answer Extraction
**Tool:** `parse_student_answer_tool`

**Process:**
1. Extract text from student PDF (verbatim)
2. Match answers to question numbers
3. Return structured list of student answers

### 3. Answer Evaluation
**Tool:** `evaluate_answer_tool`

**Grading Criteria:**
```
Score Range    Meaning               Criteria
─────────────────────────────────────────────────
90-100%   →   Excellent (A+/A)  →  All key points covered, perfect
70-89%    →   Good (B/C)        →  Most key points, minor errors
50-69%    →   Sufficient (D)    →  Some key points, notable gaps
30-49%    →   Partial (E)       →  Few key points, major issues
0-29%     →   Insufficient (F)  →  Wrong/irrelevant answer
```

**Evaluation Process:**
1. **Compare** student answer with expected answer
2. **Check keywords** for coverage
3. **Assess** accuracy, completeness, clarity
4. **Generate score** (0 to max_score)
5. **Generate Turkish feedback** explaining the score
6. **Calculate confidence** (0-1) based on answer clarity
7. **Provide reasoning** for transparency

**Example Output:**
```json
{
  "score": 8.5,
  "max_score": 10,
  "feedback": "Cevap doğru ve anahtar kavramları içeriyor. Fotosentez süreci iyi açıklanmış. Klorofil ve ışık enerjisi vurgulanmış. Küçük bir detay eksik: CO2'nin rolü belirtilmemiş.",
  "is_correct": true,
  "confidence": 0.9,
  "reasoning": "Core concepts accurate, minor detail missing"
}
```

### 4. Quality Check (Self-Correction)
**Tool:** `quality_check_tool`

**Checks:**
- Is score consistent with feedback?
- Is score within valid range (0 to max_score)?
- Is feedback detailed enough?
- Does grading follow the rubric?

**If Issues Found:**
- Log the problem
- Increment retry counter
- Return to reasoning node
- Re-evaluate (max 2 retries)

### 5. Performance Analysis
**Tool:** `analyze_performance_tool`

**Output:**
```json
{
  "strengths": [
    "Soruları detaylı açıklıyor",
    "Örnekler veriyor"
  ],
  "weaknesses": [
    "Tarihsel bağlam eksik",
    "Bazı cevaplar kısa"
  ],
  "confidence": 0.85
}
```

---

## 💬 Follow-up Query Handling

### Chat System Architecture

**Endpoint:** `POST /api/v1/exam/student/{id}/chat`

**How It Works:**

1. **Context Building**
   - Student name, total score, percentage
   - Question summaries (question text, score, feedback)
   - Previous chat history (last 3 messages)

2. **Prompt Engineering**
   ```
   System: You are a helpful education assistant.
   Context: Student scored 85% (42.5/50)...
   User: What should the student improve?
   ```

3. **LLM Call**
   - Model: `gemini-2.0-flash-exp`
   - Temperature: 0.7 (creative but focused)
   - Max tokens: 512 (concise answers)
   - Timeout: 15 seconds

4. **Response Handling**
   - Parse JSON if accidentally returned
   - Extract plain text answer
   - Return to user

5. **Chat History Storage**
   - Frontend: localStorage (persistent across page reloads)
   - Backend: Database (followup_questions table)

**Example Conversation:**
```
User: "Bu öğrencinin en büyük zayıflığı nedir?"
AI: "Öğrencinin en büyük zayıflığı tarihsel bağlamı göz ardı etmesi.
     Özellikle 3. ve 5. sorularda olayların sebep-sonuç ilişkisini
     yeterince açıklayamamış."

User: "Bunu nasıl geliştirebilir?"
AI: "Öğrenci tarih kitaplarında kronolojik okuma yapabilir,
     olayları zaman çizelgesi üzerinde görsellendirerek
     neden-sonuç ilişkilerini daha iyi kavrayabilir."
```

**Chat Features:**
- ✅ Context-aware (knows student performance)
- ✅ Multi-turn conversations
- ✅ Persistent history (localStorage + DB)
- ✅ Turkish responses
- ✅ Rate limiting (Gemini free tier: 10 req/min)

---

## 📖 API Usage

### 1. Login
```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "demo@demo.com",
  "password": "demo12345!"
}

# Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 604800  # 7 days
}
```

### 2. Upload Answer Key
```bash
POST /api/v1/exam/upload-answer-key
Authorization: Bearer {token}
Content-Type: multipart/form-data

Form Data:
  exam_title: "Biology Midterm"
  answer_key: answer_key.pdf

# Response:
{
  "evaluation_id": "eval_abc123",
  "status": "pending",
  "message": "Processing in background..."
}
```

### 3. Upload Student Sheet
```bash
POST /api/v1/exam/{evaluation_id}/upload-student-sheet
Authorization: Bearer {token}
Content-Type: multipart/form-data

Form Data:
  student_name: "Alice Johnson"
  student_sheet: student_answers.pdf

# Response:
{
  "student_response_id": 1,
  "status": "pending"
}
```

### 4. Get Student Results
```bash
GET /api/v1/exam/student/{student_response_id}
Authorization: Bearer {token}

# Response:
{
  "student_name": "Alice Johnson",
  "total_score": 42.5,
  "max_score": 50.0,
  "percentage": 85.0,
  "strengths": [...],
  "weaknesses": [...],
  "questions": [
    {
      "question_number": 1,
      "score": 8.5,
      "feedback": "Excellent answer...",
      "confidence": 0.9,
      "reasoning": "Core concepts accurate"
    }
  ]
}
```

### 5. Chat with AI
```bash
POST /api/v1/exam/student/{id}/chat
Authorization: Bearer {token}
Content-Type: application/json

{
  "question": "What should the student improve?",
  "chat_history": [...]  # Optional
}

# Response:
{
  "answer": "The student should focus on..."
}
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

## ⚠️ Known Limitations & Assumptions

### Limitations

1. **PDF Format Only**
   - Only accepts PDF files for answer keys and student sheets
   - No support for images, handwritten text, or other formats
   - Assumes text is selectable (not scanned images)

2. **Gemini API Free Tier Constraints**
   - **Rate Limit**: 10 requests per minute
   - **Daily Quota**: 50 requests per day (free tier)
   - Evaluation speed depends on number of questions
   - Example: 5 questions = ~35-40 seconds (with 7s delays between calls)

3. **Turkish Language Focus**
   - AI feedback is generated in Turkish only
   - System prompts and UI are Turkish-centric
   - May not work optimally for other languages

4. **Single-User Processing**
   - Celery workers process tasks sequentially
   - No parallel evaluation of multiple students
   - Large batches may take time (not batch-optimized)

5. **PDF Text Extraction Quality**
   - Depends on PDF structure and formatting
   - Complex layouts (tables, columns) may confuse parsing
   - Mathematical formulas may not extract correctly

6. **Confidence Scoring Accuracy**
   - Confidence scores are AI-generated estimates
   - May not always reflect actual accuracy
   - Low confidence doesn't guarantee incorrect scoring

### Assumptions

1. **Answer Key Structure**
   - Assumes answer key has clear question numbering (1, 2, 3...)
   - Assumes questions and answers are separated (e.g., blank line)
   - Assumes each question has a corresponding answer

2. **Student Answer Format**
   - Assumes student answers follow same numbering as answer key
   - Assumes answers are written in complete sentences
   - Assumes no multiple-choice bubbles or checkboxes

3. **Scoring Rubric**
   - Assumes 10 points per question by default (configurable)
   - Assumes 70% threshold for "correct" (is_correct = true)
   - Assumes Turkish feedback is acceptable for evaluation

4. **Network & Infrastructure**
   - Assumes stable internet connection for Gemini API
   - Assumes Docker/Docker Compose is available for deployment
   - Assumes PostgreSQL, Redis, RabbitMQ are correctly configured

5. **User Behavior**
   - Assumes users upload valid PDF files (not corrupted)
   - Assumes users don't spam requests (rate limiting in place)
   - Assumes JWT tokens are kept secure by users

### Future Improvements

To address these limitations:
- [ ] Support for scanned PDFs (OCR integration)
- [ ] Handwriting recognition
- [ ] Batch processing for multiple students in parallel
- [ ] Multi-language support (English, Spanish, etc.)
- [ ] Image/diagram recognition
- [ ] Paid Gemini API for higher rate limits
- [ ] Custom scoring rubrics per question
- [ ] Excel/CSV export for results

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Async Python web framework
- **LangGraph** - Stateful agentic workflows
- **LangChain** - LLM tooling and chains
- **Google Gemini 2.0 Flash** - Large language model
- **Celery** - Distributed task queue
- **PostgreSQL** - Relational database
- **Redis** - Caching + SSE progress tracking
- **RabbitMQ** - Message broker
- **SQLAlchemy** - Async ORM
- **Pydantic** - Data validation

### Frontend
- **Next.js 15** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Zustand** - State management
- **EventSource API** - SSE streaming

### DevOps
- **Docker & Docker Compose** - Containerization
- **Fly.io** - Cloud deployment
- **Makefile** - Build automation

---

## 📝 License

MIT License - See [LICENSE](LICENSE) file

## 👤 Author

**Ali Yaman** - [GitHub](https://github.com/AliYmn)

---

**Built with ❤️ and 🤖 AI**

*An intelligent, self-correcting exam evaluation system powered by LangGraph*
