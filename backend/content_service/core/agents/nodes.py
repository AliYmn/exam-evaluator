"""
Agent nodes for LangGraph workflow
Includes: Reasoning, Tool Execution, Quality Check (Self-Correction)
"""

import time
from typing import Literal
from .state import AgentState
from .tools import (
    parse_answer_key_tool,
    parse_student_answer_tool,
    evaluate_answer_tool,
    quality_check_tool,
    analyze_performance_tool,
)


def agent_reasoning_node(state: AgentState) -> AgentState:
    """
    Agent reasoning node - decides what action to take next.
    This is the "thinking" part of ReAct pattern.
    """
    task = state["task"]
    context = state.get("context", {})
    retry_count = state.get("retry_count", 0)

    # Build reasoning based on task
    if task == "parse_answer_key":
        thought = "I need to parse the answer key PDF to extract questions and expected answers."
        action = "use parse_answer_key_tool"
    elif task == "parse_student":
        thought = (
            f"I need to parse student answer sheet. Expected {context.get('question_count', 'unknown')} questions."
        )
        action = "use parse_student_answer_tool"
    elif task == "evaluate":
        if retry_count > 0:
            thought = f"Previous evaluation had quality issues. Retrying with corrections (attempt {retry_count + 1})."
        else:
            thought = "I need to evaluate each student answer against the answer key."
        action = "use evaluate_answer_tool for each question"
    elif task == "analyze":
        thought = "I need to analyze overall performance and identify strengths/weaknesses."
        action = "use analyze_performance_tool"
    else:
        thought = "Unknown task"
        action = "none"

    state["thoughts"].append(thought)
    state["actions"].append(action)

    return state


def tool_execution_node(state: AgentState) -> AgentState:
    """
    Execute tools based on agent's decision.
    This is the "acting" part of ReAct pattern.

    NOW WITH TOOL CALL LOGGING!
    """
    task = state["task"]
    pdf_text = state.get("pdf_text", "")
    context = state.get("context", {})

    try:
        if task == "parse_answer_key":
            # Log tool call
            start_time = time.time()
            result = parse_answer_key_tool.invoke({"pdf_text": pdf_text})
            duration = time.time() - start_time

            state["tool_call_logs"].append(
                {
                    "tool": "parse_answer_key_tool",
                    "duration_seconds": round(duration, 2),
                    "success": "error" not in result,
                    "timestamp": time.time(),
                }
            )

            state["intermediate_results"]["answer_key"] = result
            state["observations"].append(
                f"Successfully parsed {result.get('total_questions', 0)} questions from answer key"
            )
            state["status"] = "completed"
            state["final_output"] = result

        elif task == "parse_student":
            # Log tool call
            start_time = time.time()
            question_count = context.get("question_count", 5)
            result = parse_student_answer_tool.invoke({"pdf_text": pdf_text, "question_count": question_count})
            duration = time.time() - start_time

            state["tool_call_logs"].append(
                {
                    "tool": "parse_student_answer_tool",
                    "duration_seconds": round(duration, 2),
                    "question_count": question_count,
                    "answers_found": len(result),
                    "timestamp": time.time(),
                }
            )

            state["intermediate_results"]["student_answers"] = result
            state["observations"].append(f"Successfully parsed {len(result)} student answers")
            state["status"] = "completed"
            state["final_output"] = {"answers": result}

        elif task == "evaluate":
            answer_key = context.get("answer_key", {})
            student_answers = context.get("student_answers", [])

            evaluations = []
            low_confidence_count = 0

            for q in answer_key.get("questions", []):
                # Find corresponding student answer
                student_ans = next((s for s in student_answers if s["number"] == q["number"]), None)
                if not student_ans:
                    continue

                # Evaluate
                start_time = time.time()
                eval_result = evaluate_answer_tool.invoke(
                    {
                        "question_number": q["number"],
                        "question_text": q["question_text"],
                        "expected_answer": q["expected_answer"],
                        "student_answer": student_ans["student_answer"],
                        "max_score": q["max_score"],
                        "keywords": ", ".join(q.get("keywords", [])),
                    }
                )
                duration = time.time() - start_time

                # Log tool call
                state["tool_call_logs"].append(
                    {
                        "tool": "evaluate_answer_tool",
                        "question_number": q["number"],
                        "duration_seconds": round(duration, 2),
                        "confidence": eval_result.get("confidence", 0.8),
                        "timestamp": time.time(),
                    }
                )

                # Track confidence
                confidence = eval_result.get("confidence", 0.8)
                state["confidence_scores"].append(confidence)

                # Flag low confidence
                if confidence < 0.6:
                    low_confidence_count += 1

                evaluations.append(
                    {
                        "question_number": q["number"],
                        "question_text": q["question_text"],
                        "expected_answer": q["expected_answer"],
                        "student_answer": student_ans["student_answer"],
                        "max_score": q["max_score"],
                        **eval_result,
                    }
                )

            # Check if human review is needed
            avg_confidence = (
                sum(state["confidence_scores"]) / len(state["confidence_scores"]) if state["confidence_scores"] else 0.8
            )
            if avg_confidence < 0.6 or low_confidence_count > len(evaluations) * 0.3:
                state["needs_review"] = True
                state["observations"].append(
                    f"⚠️ Low confidence detected (avg: {avg_confidence:.2f}). Human review recommended."
                )

            state["intermediate_results"]["evaluations"] = evaluations
            state["observations"].append(
                f"Successfully evaluated {len(evaluations)} questions. Avg confidence: {avg_confidence:.2f}"
            )
            state["status"] = "quality_check"  # Move to quality check next
            state["final_output"] = {"evaluations": evaluations}

        elif task == "analyze":
            student_name = context.get("student_name", "Unknown")
            total_score = context.get("total_score", 0)
            max_score = context.get("max_score", 100)
            percentage = context.get("percentage", 0)
            questions_data = context.get("questions_data", [])

            # Build questions summary
            questions_summary = "\n\n".join(
                [
                    f"Soru {q['question_number']}: {q['score']:.1f}/{q['max_score']:.1f} - "
                    f"{'Doğru' if q.get('is_correct') else 'Yanlış'}\n"
                    f"Feedback: {q['feedback'][:150]}..."
                    for q in questions_data[:10]
                ]
            )

            start_time = time.time()
            result = analyze_performance_tool.invoke(
                {
                    "student_name": student_name,
                    "total_score": total_score,
                    "max_score": max_score,
                    "percentage": percentage,
                    "questions_summary": questions_summary,
                }
            )
            duration = time.time() - start_time

            # Log tool call
            state["tool_call_logs"].append(
                {
                    "tool": "analyze_performance_tool",
                    "duration_seconds": round(duration, 2),
                    "confidence": result.get("confidence", 0.8),
                    "timestamp": time.time(),
                }
            )

            # Track confidence
            if "confidence" in result:
                state["confidence_scores"].append(result["confidence"])

            state["intermediate_results"]["analysis"] = result
            state["observations"].append("Successfully analyzed student performance")
            state["status"] = "completed"
            state["final_output"] = result

        else:
            state["observations"].append(f"Unknown task: {task}")
            state["status"] = "failed"
            state["error"] = f"Unknown task: {task}"

    except Exception as e:
        state["observations"].append(f"Error executing task: {str(e)}")
        state["status"] = "failed"
        state["error"] = str(e)

    return state


def quality_check_node(state: AgentState) -> AgentState:
    """
    NEW NODE: Quality check / self-correction node.
    Reviews evaluation results and decides if they're acceptable or need retry.
    """
    evaluations = state["intermediate_results"].get("evaluations", [])
    retry_count = state.get("retry_count", 0)
    max_retries = 2

    if not evaluations or retry_count >= max_retries:
        # Skip quality check if no evaluations or max retries reached
        state["status"] = "completed"
        state["observations"].append("Quality check skipped (no evaluations or max retries reached)")
        return state

    # Perform quality check on evaluations
    quality_issues = []
    needs_retry = False

    for eval_data in evaluations:
        start_time = time.time()
        quality_result = quality_check_tool.invoke(
            {"evaluation_data": eval_data, "max_score": eval_data.get("max_score", 10)}
        )
        duration = time.time() - start_time

        # Log quality check
        state["tool_call_logs"].append(
            {
                "tool": "quality_check_tool",
                "question_number": eval_data.get("question_number"),
                "duration_seconds": round(duration, 2),
                "is_acceptable": quality_result.get("is_acceptable", True),
                "timestamp": time.time(),
            }
        )

        # Store quality check result
        state["quality_checks"].append({"question_number": eval_data.get("question_number"), "result": quality_result})

        if not quality_result.get("is_acceptable", True):
            needs_retry = True
            quality_issues.extend(quality_result.get("issues", []))

    if needs_retry and retry_count < max_retries:
        # Retry evaluation with corrections
        state["retry_count"] = retry_count + 1
        state["status"] = "processing"
        state["observations"].append(
            f"Quality check found issues. Retrying evaluation (attempt {retry_count + 2}/{max_retries + 1})"
        )
        state["observations"].append(f"Issues found: {', '.join(quality_issues[:3])}")

        # Loop back to tool_execution for retry
        # Note: The graph will handle this via conditional edges
    else:
        # Quality check passed or max retries reached
        if needs_retry:
            state["observations"].append(
                f"⚠️ Quality issues persist after {max_retries} retries. Proceeding with current results."
            )
            state["needs_review"] = True
        else:
            state["observations"].append("✅ Quality check passed. All evaluations are acceptable.")

        state["status"] = "completed"

    return state


def should_continue_after_execution(state: AgentState) -> Literal["quality_check", "end"]:
    """
    Determine next step after tool execution.
    - If evaluation task → go to quality_check
    - Otherwise → end
    """
    if state["status"] == "quality_check" and state["task"] == "evaluate":
        return "quality_check"
    return "end"


def should_retry_after_quality_check(state: AgentState) -> Literal["retry", "end"]:
    """
    Determine if evaluation should be retried after quality check.
    - If retry needed and within limits → retry (go back to reasoning)
    - Otherwise → end
    """
    if state["status"] == "processing" and state.get("retry_count", 0) > 0:
        return "retry"
    return "end"
