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
7. [API Endpoints](#-api-endpoints)
8. [Limitations & Assumptions](#-limitations--assumptions)
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
- `GEMINI_API_KEY` - Your Google Gemini API key (required)
- `JWT_SECRET_KEY` - Secret key for JWT tokens
- Database and Redis settings (see .env.example)

### Step 3: Build & Run
```bash
make build && make up
```

### Step 4: Access Application
- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8001/docs and http://localhost:8002/docs

### Step 5: Run Database Migrations
```bash
make migrate
```

**That's it!** Your exam evaluation system is ready to use.

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

### AI Agent System
The system uses LangGraph agents with self-correction capabilities to ensure accurate and consistent grading.

**Agent Flow:**
```
Upload PDF → Parse Text → AI Reasoning → Tool Execution → Quality Check → Results
     ↓              ↓           ↓            ↓              ↓
  Answer Key    Extract     Choose Tool   Evaluate      Self-Correct
  Student PDF   Content     Parse/Score   Answers       (Max 2 retries)
```

---

## 📊 Grading & Feedback Logic

**Scoring Scale:**
- 90-100%: Excellent (A+/A) - All key points covered
- 70-89%: Good (B/C) - Most key points, minor errors
- 50-69%: Sufficient (D) - Some key points, notable gaps
- 30-49%: Partial (E) - Few key points, major issues
- 0-29%: Insufficient (F) - Wrong/irrelevant answer

**Process:**
1. **Parse** answer key PDF → extract questions & expected answers
2. **Parse** student PDF → extract student answers
3. **Compare** answers using AI → generate scores (0-10 per question)
4. **Generate** Turkish feedback explaining each score
5. **Quality check** → self-correct if needed (max 2 retries)
6. **Analyze** overall performance → strengths/weaknesses

---

## 💬 Follow-up Query Handling

**Chat System:**
- **Endpoint:** `POST /api/v1/exam/student/{id}/chat`
- **Context-aware:** Knows student performance, scores, feedback
- **Multi-turn:** Maintains conversation history
- **Turkish responses:** AI answers in Turkish
- **Rate limited:** 10 requests/minute (Gemini free tier)

**Example:**
```
User: "Bu öğrencinin en büyük zayıflığı nedir?"
AI: "Öğrencinin en büyük zayıflığı tarihsel bağlamı göz ardı etmesi..."
```

---

## ⚠️ Limitations & Assumptions

**Limitations:**
- **PDF only** - No images, handwriting, or other formats
- **Gemini free tier** - 10 req/min, 50 req/day limit
- **Turkish focus** - AI feedback in Turkish only
- **Sequential processing** - No parallel student evaluation

**Assumptions:**
- Answer keys have clear question numbering (1, 2, 3...)
- Student answers follow same numbering as answer key
- 10 points per question by default
- Text is selectable (not scanned images)

---

## 📖 API Endpoints

- `POST /api/v1/auth/login` - User authentication
- `POST /api/v1/exam/upload-answer-key` - Upload answer key PDF
- `POST /api/v1/exam/{id}/upload-student-sheet` - Upload student answer PDF
- `GET /api/v1/exam/student/{id}` - Get student results
- `POST /api/v1/exam/student/{id}/chat` - Chat with AI about student performance
- `GET /api/v1/exam/{id}/progress-stream` - Real-time progress updates (SSE)

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
