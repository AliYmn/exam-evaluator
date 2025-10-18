"""
LangChain tools for exam evaluation agent
"""

from typing import Dict, Any, List
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
                """You are a TEXT EXTRACTION tool, NOT an AI assistant. Your ONLY job is EXACT VERBATIM COPY.

🚨 CRITICAL - READ CAREFULLY:
You are FORBIDDEN from:
❌ Paraphrasing or rewording ANY text
❌ Summarizing or condensing content
❌ "Improving" or "clarifying" text
❌ Translating or changing language
❌ Adding your own interpretations
❌ Fixing grammar or typos in the original
❌ Omitting ANY words, sentences, or details

You MUST:
✅ Copy EVERY SINGLE WORD exactly as written
✅ Preserve ALL punctuation marks (commas, periods, etc.)
✅ Keep ALL formatting (line breaks, bullet points, numbering)
✅ Include ALL examples, formulas, and explanations
✅ Maintain exact spelling (even if it has typos)
✅ Copy question numbers EXACTLY as shown (1, 2, 3 or a, b, c, etc.)

EXAMPLE:
Original: "Fotosentez nedir? Bitkilerin güneş ışığını kullanarak glikoz üretme sürecidir."
❌ WRONG: "Fotosentez, bitkilerin ışığı kullanarak şeker üretmesidir."
✅ CORRECT: "Fotosentez nedir? Bitkilerin güneş ışığını kullanarak glikoz üretme sürecidir."

Think of yourself as a COPY-PASTE function, NOT a writer.

{format_instructions}

RETURN ONLY THE JSON. ZERO INTERPRETATION.""",
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
        result = chain.invoke(pdf_text)

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
    except Exception as e:
        return {"error": str(e), "questions": [], "total_questions": 0, "max_possible_score": 0}


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
                """You are a TEXT EXTRACTION tool, NOT an AI assistant. Your ONLY job is EXACT VERBATIM COPY of student answers.

🚨 CRITICAL - READ CAREFULLY:
You are FORBIDDEN from:
❌ Paraphrasing or rewording ANY text
❌ Summarizing student answers
❌ "Improving" or "clarifying" student text
❌ Fixing student's grammar or spelling errors
❌ Adding your own interpretations
❌ Omitting ANY words or sentences

You MUST:
✅ Copy EVERY SINGLE WORD the student wrote
✅ Preserve ALL punctuation marks
✅ Keep ALL formatting (line breaks, bullet points)
✅ Include ALL examples and explanations student provided
✅ Maintain exact spelling (even student's mistakes)
✅ Copy question numbers EXACTLY as shown
✅ If question has NO answer, write: "[No answer provided]"

EXAMPLE:
Student wrote: "Fotosentes bitkinin gunes ile gida yapmasidir."
❌ WRONG: "Fotosentez, bitkilerin güneş ile gıda yapmasıdır." (you corrected it!)
✅ CORRECT: "Fotosentes bitkinin gunes ile gida yapmasidir." (exact copy with student's mistakes)

Think of yourself as a COPY-PASTE function, NOT a grader or writer.

EXPECTED NUMBER OF QUESTIONS: {question_count}

{format_instructions}

RETURN ONLY THE JSON. ZERO INTERPRETATION. EXACT COPY ONLY.""",
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
        result = chain.invoke({"pdf_text": pdf_text, "question_count": question_count})
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

    try:
        input_data = {
            "question_number": question_number,
            "question_text": question_text,
            "expected_answer": expected_answer,
            "student_answer": student_answer,
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
        return {
            "score": 0,
            "feedback": f"Değerlendirme hatası: {str(e)}",
            "is_correct": False,
            "confidence": 0.0,
            "reasoning": "Hata oluştu",
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
