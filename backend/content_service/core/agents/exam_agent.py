"""
Main Exam Evaluation Agent - Refactored with Self-Correction
"""

from typing import Dict, Any, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json

from libs.settings import settings
from .state import AgentState
from .workflow import exam_evaluation_graph


class ExamEvaluationAgent:
    """
    Agentic Exam Evaluation Service using LangGraph.

    Features:
    - Multi-step reasoning with ReAct pattern
    - Self-correction via quality check node
    - Confidence scores for all evaluations
    - Reasoning trace and tool call logging
    - Automatic retry on quality issues (max 2 retries)
    - Human review flagging for low-confidence results
    """

    def __init__(self):
        self.graph = exam_evaluation_graph

    def parse_answer_key(self, pdf_text: str) -> Dict[str, Any]:
        """
        Parse answer key using agentic approach.

        Returns:
            {
                "questions": [...],
                "total_questions": N,
                "max_possible_score": X,
                "_agent_trace": {...}  # Optional: reasoning trace
            }
        """
        initial_state: AgentState = {
            "task": "parse_answer_key",
            "pdf_text": pdf_text,
            "context": {},
            "thoughts": [],
            "actions": [],
            "observations": [],
            "intermediate_results": {},
            "quality_checks": [],
            "retry_count": 0,
            "needs_review": False,
            "final_output": {},
            "status": "processing",
            "error": "",
            "confidence_scores": [],
            "tool_call_logs": [],
        }

        final_state = self.graph.invoke(initial_state)

        if final_state["status"] == "failed":
            raise Exception(f"Failed to parse answer key: {final_state['error']}")

        # Add agent trace for transparency
        result = final_state["final_output"]
        result["_agent_trace"] = {
            "thoughts": final_state["thoughts"],
            "observations": final_state["observations"],
            "tool_calls": final_state["tool_call_logs"],
        }

        return result

    def parse_student_answer(self, pdf_text: str, question_count: int) -> List[Dict[str, Any]]:
        """
        Parse student answers using agentic approach.
        """
        initial_state: AgentState = {
            "task": "parse_student",
            "pdf_text": pdf_text,
            "context": {"question_count": question_count},
            "thoughts": [],
            "actions": [],
            "observations": [],
            "intermediate_results": {},
            "quality_checks": [],
            "retry_count": 0,
            "needs_review": False,
            "final_output": {},
            "status": "processing",
            "error": "",
            "confidence_scores": [],
            "tool_call_logs": [],
        }

        final_state = self.graph.invoke(initial_state)

        if final_state["status"] == "failed":
            raise Exception(f"Failed to parse student answer: {final_state['error']}")

        return final_state["final_output"].get("answers", [])

    def evaluate_student(self, answer_key: Dict[str, Any], student_answers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate student answers with self-correction.

        Returns:
            {
                "evaluations": [...],  # Each with confidence, reasoning
                "needs_review": bool,
                "avg_confidence": float,
                "_agent_trace": {...}
            }
        """
        initial_state: AgentState = {
            "task": "evaluate",
            "pdf_text": "",
            "context": {"answer_key": answer_key, "student_answers": student_answers},
            "thoughts": [],
            "actions": [],
            "observations": [],
            "intermediate_results": {},
            "quality_checks": [],
            "retry_count": 0,
            "needs_review": False,
            "final_output": {},
            "status": "processing",
            "error": "",
            "confidence_scores": [],
            "tool_call_logs": [],
        }

        final_state = self.graph.invoke(initial_state)

        if final_state["status"] == "failed":
            raise Exception(f"Failed to evaluate student: {final_state['error']}")

        # Enhance output with metadata
        result = {
            "evaluations": final_state["final_output"].get("evaluations", []),
            "needs_review": final_state.get("needs_review", False),
            "avg_confidence": (
                sum(final_state["confidence_scores"]) / len(final_state["confidence_scores"])
                if final_state["confidence_scores"]
                else 0.8
            ),
            "retry_count": final_state.get("retry_count", 0),
            "_agent_trace": {
                "thoughts": final_state["thoughts"],
                "observations": final_state["observations"],
                "quality_checks": final_state["quality_checks"],
                "tool_calls": final_state["tool_call_logs"],
            },
        }

        return result

    def analyze_student_performance(
        self,
        student_name: str,
        total_score: float,
        max_score: float,
        percentage: float,
        questions_data: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Analyze student performance with confidence.
        """
        initial_state: AgentState = {
            "task": "analyze",
            "pdf_text": "",
            "context": {
                "student_name": student_name,
                "total_score": total_score,
                "max_score": max_score,
                "percentage": percentage,
                "questions_data": questions_data,
            },
            "thoughts": [],
            "actions": [],
            "observations": [],
            "intermediate_results": {},
            "quality_checks": [],
            "retry_count": 0,
            "needs_review": False,
            "final_output": {},
            "status": "processing",
            "error": "",
            "confidence_scores": [],
            "tool_call_logs": [],
        }

        final_state = self.graph.invoke(initial_state)

        if final_state["status"] == "failed":
            raise Exception(f"Failed to analyze performance: {final_state['error']}")

        return final_state["final_output"]

    def chat_about_student(
        self,
        question: str,
        student_name: str,
        total_score: float,
        max_score: float,
        percentage: float,
        summary: str,
        questions_data: List[Dict[str, Any]],
        chat_history: List[Dict[str, str]] = None,
    ) -> str:
        """
        Chat about student using simple LLM (not agent, as this is simpler task).
        """
        from google.generativeai.types import HarmCategory, HarmBlockThreshold

        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.7,
            max_output_tokens=1024,
            safety_settings={
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            },
        )

        # Build context
        context_parts = [
            f"ÖĞRENCİ: {student_name}",
            f"PUAN: {total_score:.1f}/{max_score:.1f} (%{percentage:.1f})",
            f"ÖZET: {summary[:200] if summary else 'Yok'}",
            f"\nSORULAR (toplam {len(questions_data)}):",
        ]

        # Add question summaries (first 3)
        for q in questions_data[:3]:
            context_parts.append(
                f"Q{q['number']}: Puan {q['score']:.1f}/{q['max_score']:.1f} - "
                f"{'Doğru' if q['is_correct'] else 'Yanlış'}\n"
                f"Feedback: {q['feedback'][:100]}..."
            )

        context = "\n".join(context_parts)

        # Build chat history
        history_messages = []
        if chat_history:
            for msg in chat_history[-5:]:
                role = "user" if msg["role"] == "user" else "assistant"
                history_messages.append((role, msg["content"]))

        # Create prompt
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """Sen yardımcı bir eğitim danışmanısın. Öğrencinin sınav performansı hakkında doğrudan konuşarak yanıt veriyorsun.

ÖNEMLİ: ASLA JSON, NESNE veya YAPILANDIRILMIŞ VERI KULLANMA!
Sadece normal konuşma metni ile yanıt ver.

YANIT KURALLARI:
✓ Normal konuşma dili kullan (sanki birine anlatıyormuş gibi)
✓ Maksimum 3-4 cümle
✓ Gerekirse madde işaretleri kullan (•)
✓ Türkçe yaz
✗ JSON, dictionary, key-value formatı KULLANMA
✗ Süslü parantez {{ }} KULLANMA

BAĞLAM:
{context}""",
                ),
                *history_messages,
                ("user", "{question}"),
            ]
        )

        chain = prompt | llm | StrOutputParser()

        try:
            result = chain.invoke({"context": context, "question": question})

            # Check if accidentally returned JSON
            if result.startswith("{") or result.startswith("["):
                try:
                    data = json.loads(result)
                    if isinstance(data, dict):
                        return (
                            data.get("durumu")
                            or data.get("yanit")
                            or " ".join(str(v) for v in data.values() if isinstance(v, str))
                        )
                except (json.JSONDecodeError, KeyError, ValueError):
                    pass

            return result.strip()
        except Exception as e:
            print(f"❌ Chat error: {str(e)}")
            import traceback

            traceback.print_exc()
            return "Üzgünüm, şu anda yanıt veremiyorum. Lütfen daha sonra tekrar deneyin."
