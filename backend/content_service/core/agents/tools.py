"""
LangChain tools for exam evaluation agent
"""

from typing import Dict, Any, List
import time
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from libs.settings import settings
from .models import AnswerKeyOutput, StudentAnswersOutput, EvaluationResult, PerformanceAnalysis, QualityCheckResult


@tool
def parse_answer_key_tool(pdf_text: str) -> Dict[str, Any]:
    """
    Parse answer key PDF and extract questions and answers.

    Args:
        pdf_text: Raw text extracted from PDF

    Returns:
        Dictionary with questions, total_questions, and max_possible_score
    """
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.0,  # ZERO creativity - exact copying only
        max_output_tokens=8192,
    )

    parser = JsonOutputParser(pydantic_object=AnswerKeyOutput)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a precise PDF text extractor. Extract questions and answers EXACTLY as written.

CRITICAL RULES:
- Copy text WORD-FOR-WORD (verbatim)
- Do NOT paraphrase, summarize, or rewrite
- Preserve ALL punctuation and formatting
- Include question numbers exactly as shown

HOW TO SEPARATE:
- question_text: Everything that ASKS (including context, ends with ?)
- expected_answer: The RESPONSE/EXPLANATION (starts after blank line)

{format_instructions}

RETURN ONLY JSON.""",
            ),
            ("user", "Extract the following text VERBATIM (word-for-word):\n\n{pdf_text}"),
        ]
    )

    chain = (
        {"pdf_text": lambda x: x, "format_instructions": lambda _: parser.get_format_instructions()}
        | prompt
        | llm
        | parser
    )

    try:
        # Rate limiting for free tier (10 requests/min)
        time.sleep(7)

        # Clean PDF text to avoid JSON parsing issues
        cleaned_text = pdf_text.replace("\r\n", "\n").replace("\r", "\n")
        # Remove null bytes and other problematic characters
        cleaned_text = cleaned_text.replace("\x00", "").replace("\ufffd", "")

        result = chain.invoke(cleaned_text)

        # Ensure all questions have required fields
        for q in result["questions"]:
            if "max_score" not in q:
                q["max_score"] = 10
            if "keywords" not in q:
                q["keywords"] = []

        # Calculate totals if missing
        if "total_questions" not in result:
            result["total_questions"] = len(result["questions"])
        if "max_possible_score" not in result:
            result["max_possible_score"] = sum(q.get("max_score", 10) for q in result["questions"])

        return result
    except Exception:
        return {"error": "An error occurred", "questions": [], "total_questions": 0, "max_possible_score": 0}


@tool
def parse_student_answer_tool(pdf_text: str, question_count: int) -> List[Dict[str, Any]]:
    """
    Parse student answer sheet and extract student responses.

    Args:
        pdf_text: Raw text extracted from student PDF
        question_count: Expected number of questions

    Returns:
        List of student answers with question numbers
    """
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.0,  # ZERO creativity - exact copying only
        max_output_tokens=8192,
    )

    parser = JsonOutputParser(pydantic_object=StudentAnswersOutput)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a precise student answer extractor. Extract answers EXACTLY as written.

CRITICAL RULES:
- Copy WORD-FOR-WORD (verbatim) including spelling errors
- Do NOT correct grammar or spelling
- Do NOT paraphrase or improve text
- Preserve ALL punctuation and formatting
- If no answer: "[No answer provided]"

EXPECTED QUESTIONS: {question_count}

{format_instructions}

RETURN ONLY JSON.""",
            ),
            ("user", "Extract the student's answers VERBATIM (word-for-word):\n\n{pdf_text}"),
        ]
    )

    chain = (
        {
            "pdf_text": lambda x: x["pdf_text"],
            "question_count": lambda x: x["question_count"],
            "format_instructions": lambda _: parser.get_format_instructions(),
        }
        | prompt
        | llm
        | parser
    )

    try:
        # Rate limiting for free tier (10 requests/min)
        time.sleep(7)

        # Clean PDF text to avoid JSON parsing issues
        cleaned_text = pdf_text.replace("\r\n", "\n").replace("\r", "\n")
        # Remove null bytes and other problematic characters
        cleaned_text = cleaned_text.replace("\x00", "").replace("\ufffd", "")

        result = chain.invoke({"pdf_text": cleaned_text, "question_count": question_count})
        return result.get("answers", [])
    except Exception:
        return [{"number": i + 1, "student_answer": "[Error parsing]"} for i in range(question_count)]


@tool
def evaluate_answer_tool(
    question_number: int,
    question_text: str,
    expected_answer: str,
    student_answer: str,
    max_score: float,
    keywords: str = "",
) -> Dict[str, Any]:
    """
    Evaluate a single student answer against the expected answer.
    NOW WITH CONFIDENCE SCORE!

    Args:
        question_number: Question number
        question_text: The question text
        expected_answer: Expected answer from answer key
        student_answer: Student's actual answer
        max_score: Maximum score possible
        keywords: Key concepts to look for (comma-separated)

    Returns:
        Dictionary with score, feedback, is_correct, confidence, and reasoning
    """
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.2,
        max_output_tokens=2048,
    )

    parser = JsonOutputParser(pydantic_object=EvaluationResult)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """Sen bir uzman sınav değerlendiricisisin. Görevin öğrencinin cevabını adil bir şekilde değerlendirmektir.

DEĞERLENDİRME KRİTERLERİ:
1. Doğruluk: Cevap beklenen cevapla eşleşiyor mu?
2. Tamlık: Tüm ana noktalar kapsanmış mı?
3. Kesinlik: Bilgiler gerçeklere uygun mu?
4. Açıklık: Cevap iyi açıklanmış mı?

PUANLAMA REHBERİ:
- %90-100: Mükemmel, tüm noktalar doğru şekilde ele alınmış
- %70-89: İyi, çoğu nokta küçük eksiklerle ele alınmış
- %50-69: Yeterli, bazı anahtar noktalar eksik
- %30-49: Kısmi anlayış
- %0-29: Yanlış veya yetersiz

GÜVENİLİRLİK SKORU (confidence):
- 0.9-1.0: Çok emin (net doğru/yanlış cevap)
- 0.7-0.9: Emin (objektif değerlendirme mümkün)
- 0.5-0.7: Orta güven (subjektif unsurlar var)
- 0.0-0.5: Düşük güven (belirsiz, insan kontrolü gerekebilir)

{format_instructions}

ADİL ve YAPICI ol. Eğer öğrenci cevabı "[No answer provided]" ise, 0 puan ver.
FEEDBACK ve REASONING MUTLAKA TÜRKÇE OLMALIDIR.""",
            ),
            (
                "user",
                """SORU #{question_number}:
{question_text}

BEKLENİLEN CEVAP (Cevap Anahtarı):
{expected_answer}

ÖĞRENCİNİN CEVABI:
{student_answer}

ARANACAK ANAHTAR KAVRAMLAR: {keywords}
MAKSİMUM PUAN: {max_score}

ÇIKTI İÇERMELİ:
- score: Verilen puan
- feedback: Türkçe açıklama
- is_correct: Doğru mu?
- confidence: Güven skoru (0-1)
- reasoning: Kısa gerekçe (Türkçe)""",
            ),
        ]
    )

    chain = (
        {
            "question_number": lambda x: x["question_number"],
            "question_text": lambda x: x["question_text"],
            "expected_answer": lambda x: x["expected_answer"],
            "student_answer": lambda x: x["student_answer"],
            "keywords": lambda x: x["keywords"],
            "max_score": lambda x: x["max_score"],
            "format_instructions": lambda _: parser.get_format_instructions(),
        }
        | prompt
        | llm
        | parser
    )

    # Retry logic with exponential backoff for rate limits
    max_retries = 3
    base_delay = 7  # Free tier: 10 requests/min = 6 seconds + buffer

    for attempt in range(max_retries):
        try:
            # Rate limiting: Wait between requests to avoid quota exceeded
            if attempt > 0:
                wait_time = base_delay * (2**attempt)  # Exponential backoff
                time.sleep(wait_time)
            else:
                # Always wait to respect free tier limits (10 req/min)
                time.sleep(base_delay)

            # Clean text inputs to avoid JSON parsing issues
            def clean_text(text):
                if not isinstance(text, str):
                    return text
                return text.replace("\r\n", "\n").replace("\r", "\n").replace("\x00", "").replace("\ufffd", "")

            input_data = {
                "question_number": question_number,
                "question_text": clean_text(question_text),
                "expected_answer": clean_text(expected_answer),
                "student_answer": clean_text(student_answer),
                "keywords": keywords,
                "max_score": max_score,
            }
            result = chain.invoke(input_data)

            # Ensure score is within bounds
            result["score"] = min(max(result["score"], 0), max_score)

            # Ensure required fields
            if "is_correct" not in result:
                result["is_correct"] = result["score"] >= (max_score * 0.7)
            if "confidence" not in result:
                result["confidence"] = 0.8  # Default confidence
            if "reasoning" not in result:
                result["reasoning"] = "Standart değerlendirme"

            return result

        except Exception as e:
            error_msg = str(e)

            # Check if it's a rate limit error
            if "429" in error_msg or "quota" in error_msg.lower():
                if attempt < max_retries - 1:
                    continue  # Retry with exponential backoff
                else:
                    print(f"❌ Rate limit exceeded after {max_retries} attempts")

            # If not rate limit or final attempt, return error
            return {
                "score": 0,
                "feedback": "Değerlendirme hatası: API limiti aşıldı. Lütfen birkaç dakika bekleyin veya API planınızı yükseltin.",
                "is_correct": False,
                "confidence": 0.0,
                "reasoning": "API rate limit",
            }

    # Fallback (should never reach here)
    return {
        "score": 0,
        "feedback": "Değerlendirme tamamlanamadı",
        "is_correct": False,
        "confidence": 0.0,
        "reasoning": "Bilinmeyen hata",
    }


@tool
def quality_check_tool(evaluation_data: Dict[str, Any], max_score: float) -> Dict[str, Any]:
    """
    NEW TOOL: Quality check / self-correction for evaluations.
    Reviews the evaluation to ensure it's fair and accurate.

    Args:
        evaluation_data: The evaluation result to check
        max_score: Maximum possible score

    Returns:
        Quality check result with is_acceptable, issues, and suggested_corrections
    """
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.1,
        max_output_tokens=1024,
    )

    parser = JsonOutputParser(pydantic_object=QualityCheckResult)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """Sen bir kalite kontrol uzmanısın. Görevin sınav değerlendirmelerinin adil ve tutarlı olup olmadığını kontrol etmek.

KONTROL KRİTERLERİ:
1. Puan feedback ile uyumlu mu?
2. Puan aralığı mantıklı mı? (0 ile max_score arası)
3. Feedback yeterince açıklayıcı mı?
4. Puanlama rehberine uyuluyor mu?

KABUL EDİLEBİLİR DEĞİL ise issues listesinde belirt.

{format_instructions}""",
            ),
            (
                "user",
                """DEĞERLENDİRME KONTROL:

Verilen Puan: {score}/{max_score}
Feedback: {feedback}
Confidence: {confidence}
Reasoning: {reasoning}

Bu değerlendirme kaliteli ve adil mi?""",
            ),
        ]
    )

    chain = (
        {
            "score": lambda x: x["score"],
            "max_score": lambda x: x["max_score"],
            "feedback": lambda x: x["feedback"],
            "confidence": lambda x: x.get("confidence", 0.8),
            "reasoning": lambda x: x.get("reasoning", "Yok"),
            "format_instructions": lambda _: parser.get_format_instructions(),
        }
        | prompt
        | llm
        | parser
    )

    try:
        input_data = {
            "score": evaluation_data.get("score", 0),
            "max_score": max_score,
            "feedback": evaluation_data.get("feedback", ""),
            "confidence": evaluation_data.get("confidence", 0.8),
            "reasoning": evaluation_data.get("reasoning", "Yok"),
        }
        result = chain.invoke(input_data)

        return result
    except Exception:
        return {
            "is_acceptable": True,  # Default to acceptable if check fails
            "issues": [],
            "suggested_corrections": None,
            "confidence": 0.5,
        }


@tool
def analyze_performance_tool(
    student_name: str, total_score: float, max_score: float, percentage: float, questions_summary: str
) -> Dict[str, Any]:
    """
    Analyze overall student performance and identify strengths/weaknesses.
    NOW WITH CONFIDENCE!

    Args:
        student_name: Student's name
        total_score: Total score achieved
        max_score: Maximum possible score
        percentage: Percentage score
        questions_summary: Summary of all question evaluations

    Returns:
        Dictionary with strengths, weaknesses, and confidence
    """
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.3,
        max_output_tokens=2048,
    )

    parser = JsonOutputParser(pydantic_object=PerformanceAnalysis)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """Sen bir eğitim analistisin. Öğrencinin sınav performansını analiz edip güçlü/zayıf yönlerini belirle.

ÖNEMLİ KURALLAR:
- Her liste için 2-4 madde yaz
- Kısa ve net cümleler kullan (maksimum 10-15 kelime)
- Türkçe yaz
- Spesifik ol (örneğin: "Genel olarak iyi" değil, "Tarihsel olayları kronolojik sıraya koyuyor")
- confidence: Analizine ne kadar güveniyorsun? (0-1)

{format_instructions}""",
            ),
            (
                "user",
                """ÖĞRENCİ ANALİZİ:
Öğrenci: {student_name}
Toplam Puan: {total_score}/{max_score} (%{percentage})

SORULAR VE CEVAPLAR:
{questions_summary}

GÖREV:
Yukarıdaki sınav performansını analiz ederek öğrencinin:
1. GÜÇLÜ YÖNLERİNİ (strengths) - Ne yapıyor iyi? Hangi becerileri güçlü?
2. ZAYIF YÖNLERİNİ (weaknesses) - Nerelerde zorlanıyor? Hangi eksiklikleri var?
3. CONFIDENCE - Analizine ne kadar güveniyorsun?

belirle.""",
            ),
        ]
    )

    chain = (
        {
            "student_name": lambda x: x["student_name"],
            "total_score": lambda x: x["total_score"],
            "max_score": lambda x: x["max_score"],
            "percentage": lambda x: x["percentage"],
            "questions_summary": lambda x: x["questions_summary"],
            "format_instructions": lambda _: parser.get_format_instructions(),
        }
        | prompt
        | llm
        | parser
    )

    try:
        # Rate limiting for free tier (10 requests/min)
        time.sleep(7)

        result = chain.invoke(
            {
                "student_name": student_name,
                "total_score": total_score,
                "max_score": max_score,
                "percentage": percentage,
                "questions_summary": questions_summary,
            }
        )

        # Validate structure
        if not isinstance(result.get("strengths"), list):
            result["strengths"] = []
        if not isinstance(result.get("weaknesses"), list):
            result["weaknesses"] = []
        if "confidence" not in result:
            result["confidence"] = 0.8

        return result
    except Exception:
        return {
            "strengths": ["Bazı sorulara doğru yanıt verdi"],
            "weaknesses": ["Genel performans düşük, daha fazla çalışma gerekiyor"],
            "confidence": 0.5,
        }
