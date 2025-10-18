"""
Gemini Service - Answer Key Parser
Handles PDF content parsing using Google Gemini API to extract Q&A pairs.
"""

import json
from typing import Dict, Any, List
import google.generativeai as genai
from libs.settings import settings
from google.generativeai.types import HarmCategory, HarmBlockThreshold


class GeminiService:
    """
    Service for parsing answer keys using Google Gemini.

    Main function: Extract structured Q&A pairs from PDF text.
    """

    def __init__(self):
        # Configure Gemini API
        genai.configure(api_key=settings.GEMINI_API_KEY)

        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config={
                "temperature": 0.1,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
                "response_mime_type": "application/json",
            },
        )

    def parse_answer_key(self, pdf_text: str) -> Dict[str, Any]:
        """
        Parse answer key PDF text and extract Q&A pairs.

        Args:
            pdf_text: Extracted text from PDF

        Returns:
            {
                "questions": [
                    {
                        "number": 1,
                        "question_text": "What is photosynthesis?",
                        "expected_answer": "Process by which plants...",
                        "max_score": 10,
                        "keywords": ["chloroplast", "light", "glucose"]
                    },
                    ...
                ],
                "total_questions": 5,
                "max_possible_score": 50
            }
        """

        prompt = f"""You are a precise exam answer key parser. Your ONLY job is to extract questions and answers EXACTLY as they appear in the document.

CRITICAL RULES:
1. DO NOT interpret, summarize, or rephrase
2. Extract WORD-FOR-WORD from the document
3. If a question says "Q1: Fotosentez nedir?", extract exactly "Fotosentez nedir?"
4. If answer says "Fotosentez, bitkilerin...", extract exactly "Fotosentez, bitkilerin..."
5. Keep ALL original text including examples, formulas, bullet points
6. Maintain exact question numbering (1, 2, 3... or a, b, c... as shown)
7. DO NOT add scores, keywords, or any extra fields - ONLY question and answer

EXAMPLE INPUT:
"1. Fotosentez nedir?
Cevap: Fotosentez, yeşil bitkilerin ışık enerjisini kimyasal enerjiye dönüştürdüğü süreçtir.

2. DNA'nın yapı taşları nelerdir?
Cevap: DNA nükleotitlerden oluşur."

EXAMPLE OUTPUT:
{{
    "questions": [
        {{
            "number": 1,
            "question_text": "Fotosentez nedir?",
            "expected_answer": "Fotosentez, yeşil bitkilerin ışık enerjisini kimyasal enerjiye dönüştürdüğü süreçtir."
        }},
        {{
            "number": 2,
            "question_text": "DNA'nın yapı taşları nelerdir?",
            "expected_answer": "DNA nükleotitlerden oluşur."
        }}
    ],
    "total_questions": 2
}}

NOW PARSE THIS ANSWER KEY - Extract ONLY question number, question text, and answer:

{pdf_text}

RETURN ONLY THE JSON. NO EXPLANATIONS. NO EXTRA FIELDS."""

        try:
            # Safety settings - allow educational content
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }

            # Generate response
            response = self.model.generate_content(prompt, safety_settings=safety_settings)

            # Check if response is valid
            if not response.candidates:
                raise ValueError("No response candidates returned from Gemini")

            candidate = response.candidates[0]

            # Check finish reason
            if candidate.finish_reason == 2:  # SAFETY
                raise ValueError(
                    "Content was blocked by safety filters. Please try with different content or contact support."
                )

            # Extract text from response
            if not hasattr(candidate.content, "parts") or not candidate.content.parts:
                raise ValueError("No content parts in response")

            result_text = candidate.content.parts[0].text

            # Parse JSON from response
            result = json.loads(result_text)

            # Validate structure
            if "questions" not in result or not isinstance(result["questions"], list):
                raise ValueError("Invalid response format from Gemini")

            # Set defaults for optional fields
            if "total_questions" not in result:
                result["total_questions"] = len(result["questions"])

            # Add default values for DB compatibility if missing
            for question in result["questions"]:
                if "max_score" not in question:
                    question["max_score"] = 10  # Default score
                if "keywords" not in question:
                    question["keywords"] = []  # Empty keywords

            # Calculate max possible score
            if "max_possible_score" not in result:
                result["max_possible_score"] = sum(q.get("max_score", 10) for q in result["questions"])

            return result

        except Exception as e:
            raise Exception(f"Failed to parse answer key with Gemini: {str(e)}")

    def parse_student_answer(self, pdf_text: str, question_count: int) -> List[Dict[str, Any]]:
        """
        Parse student answer sheet and extract their responses.

        Args:
            pdf_text: Extracted text from student PDF
            question_count: Expected number of questions

        Returns:
            [
                {
                    "number": 1,
                    "student_answer": "Student's written answer..."
                },
                ...
            ]
        """

        prompt = f"""You are a precise student answer sheet parser. Your ONLY job is to extract student answers EXACTLY as they appear.

CRITICAL RULES:
1. DO NOT interpret, summarize, or rephrase
2. Extract WORD-FOR-WORD from the document
3. If answer says "1. Fotosentez, bitkilerin...", extract exactly "Fotosentez, bitkilerin..."
4. Keep ALL original text including examples, formulas, diagrams descriptions
5. Maintain exact question numbering (1, 2, 3... or a, b, c... as shown)
6. If a question has no answer, use "[No answer provided]"

EXPECTED NUMBER OF QUESTIONS: {question_count}

EXAMPLE INPUT:
"1. Fotosentez, yeşil bitkilerin ışık enerjisini kullanarak glikoz üretmesidir.

2. DNA'nın yapı taşları nükleotitlerdir. Şeker, fosfat ve baz içerir."

EXAMPLE OUTPUT:
{{
    "answers": [
        {{
            "number": 1,
            "student_answer": "Fotosentez, yeşil bitkilerin ışık enerjisini kullanarak glikoz üretmesidir."
        }},
        {{
            "number": 2,
            "student_answer": "DNA'nın yapı taşları nükleotitlerdir. Şeker, fosfat ve baz içerir."
        }}
    ]
}}

NOW PARSE THIS STUDENT ANSWER SHEET - Extract ONLY question numbers and student answers:

{pdf_text}

RETURN ONLY THE JSON. NO EXPLANATIONS. ENSURE {question_count} answers."""

        try:
            # Safety settings - allow educational content
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }

            # Generate response
            response = self.model.generate_content(prompt, safety_settings=safety_settings)

            # Check if response is valid
            if not response.candidates:
                raise ValueError("No response candidates returned from Gemini")

            candidate = response.candidates[0]

            # Check finish reason
            if candidate.finish_reason == 2:  # SAFETY
                raise ValueError(
                    "Content was blocked by safety filters. Please try with different content or contact support."
                )

            # Extract text from response
            if not hasattr(candidate.content, "parts") or not candidate.content.parts:
                raise ValueError("No content parts in response")

            result_text = candidate.content.parts[0].text

            # Parse JSON from response
            result = json.loads(result_text)

            # Validate structure
            if "answers" not in result or not isinstance(result["answers"], list):
                raise ValueError("Invalid response format from Gemini")

            return result["answers"]

        except Exception as e:
            raise Exception(f"Failed to parse student answer with Gemini: {str(e)}")

    def evaluate_answer(
        self,
        question_number: int,
        question_text: str,
        expected_answer: str,
        student_answer: str,
        max_score: float,
        keywords: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate a single student answer against expected answer.

        Args:
            question_number: Question number
            question_text: The question text
            expected_answer: Expected answer from answer key
            student_answer: Student's answer
            max_score: Maximum score for this question
            keywords: Key concepts/terms to look for

        Returns:
            {
                "score": 8.5,
                "feedback": "Good answer but missing...",
                "is_correct": True/False
            }
        """

        keywords_str = ", ".join(keywords) if keywords else "None specified"

        prompt = f"""Sen bir uzman sınav değerlendiricisisin. Görevin öğrencinin cevabını adil bir şekilde değerlendirmektir.

SORU #{question_number}:
{question_text}

BEKLENİLEN CEVAP (Cevap Anahtarı):
{expected_answer}

ÖĞRENCİNİN CEVABI:
{student_answer}

ARANACAK ANAHTAR KAVRAMLAR: {keywords_str}
MAKSİMUM PUAN: {max_score}

DEĞERLENDİRME KRİTERLERİ:
1. Doğruluk: Cevap beklenen cevapla eşleşiyor mu?
2. Tamlık: Tüm ana noktalar kapsanmış mı?
3. Kesinlik: Bilgiler gerçeklere uygun mu?
4. Açıklık: Cevap iyi açıklanmış mı?

PUANLAMA REHBERİ:
- %90-100 ({max_score * 0.9}-{max_score}): Mükemmel, tüm noktalar doğru şekilde ele alınmış
- %70-89 ({max_score * 0.7}-{max_score * 0.89}): İyi, çoğu nokta küçük eksiklerle ele alınmış
- %50-69 ({max_score * 0.5}-{max_score * 0.69}): Yeterli, bazı anahtar noktalar eksik
- %30-49 ({max_score * 0.3}-{max_score * 0.49}): Kısmi anlayış
- %0-29 (0-{max_score * 0.29}): Yanlış veya yetersiz

SADECE bu formatta geçerli JSON döndür:
{{
    "score": 8.5,
    "feedback": "Puanı açıklayan detaylı ve yapıcı geri bildirim. Neyin iyi olduğunu ve neyin eksik veya yanlış olduğunu belirt. Spesifik ve eğitici ol. TÜRKÇE yaz.",
    "is_correct": true
}}

ADİL ve YAPICI ol. Eğer öğrenci cevabı "[No answer provided]" ise, 0 puan ver.
SADECE JSON DÖNDÜR. FEEDBACK MUTLAKA TÜRKÇE OLMALIDIR."""

        try:
            # Safety settings
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }

            response = self.model.generate_content(prompt, safety_settings=safety_settings)

            # Check if response is valid
            if not response.candidates:
                raise ValueError("No response candidates returned from Gemini")

            candidate = response.candidates[0]

            # Check finish reason
            if candidate.finish_reason == 2:  # SAFETY
                raise ValueError("Content was blocked by safety filters")

            # Extract text from response
            if not hasattr(candidate.content, "parts") or not candidate.content.parts:
                raise ValueError("No content parts in response")

            result_text = candidate.content.parts[0].text
            result = json.loads(result_text)

            # Validate structure
            if "score" not in result or "feedback" not in result:
                raise ValueError("Invalid evaluation response from Gemini")

            # Ensure score is within bounds
            result["score"] = min(max(result["score"], 0), max_score)

            # Ensure required fields
            if "is_correct" not in result:
                result["is_correct"] = result["score"] >= (max_score * 0.7)

            return result

        except Exception as e:
            raise Exception(f"Failed to evaluate answer with Gemini: {str(e)}")

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
        Chat about student performance with context.

        Args:
            question: User's question
            student_name: Student name
            total_score: Student's total score
            max_score: Maximum possible score
            percentage: Percentage score
            summary: Performance summary
            questions_data: List of questions with answers and feedback
            chat_history: Previous chat messages [{"role": "user/assistant", "content": "..."}]

        Returns:
            AI response text (streaming via generator)
        """

        # Build context from student data (shortened to avoid safety issues)
        context = f"""ÖĞRENCİ: {student_name}
PUAN: {total_score:.1f}/{max_score:.1f} (%{percentage:.1f})
ÖZET: {summary[:200] if summary else "Yok"}

SORULAR (toplam {len(questions_data)}):
"""

        # Only include essential info, limit to 3 questions max for context
        for q in questions_data[:3]:
            context += f"""
Q{q["number"]}: Puan {q["score"]:.1f}/{q["max_score"]:.1f} - {"Doğru" if q["is_correct"] else "Yanlış"}
Feedback: {q["feedback"][:100]}...
"""

        # Build chat history
        history_text = ""
        if chat_history:
            history_text = "\n\nÖNCEKİ KONUŞMA:\n"
            for msg in chat_history[-5:]:  # Last 5 messages for context
                role = "Kullanıcı" if msg["role"] == "user" else "AI Asistan"
                history_text += f"{role}: {msg['content']}\n"

        prompt = f"""Sen yardımcı bir eğitim danışmanısın. Öğrencinin sınav performansı hakkında doğrudan konuşarak yanıt veriyorsun.

{context}
{history_text}

KULLANICI SORUSU: {question}

ÖNEMLİ: ASLA JSON, NESNE veya YAPILANDIRILMIŞ VERI KULLANMA!
Sadece normal konuşma metni ile yanıt ver.

YANIT KURALLARI:
✓ Normal konuşma dili kullan (sanki birine anlatıyormuş gibi)
✓ Maksimum 3-4 cümle
✓ Gerekirse madde işaretleri kullan (•)
✓ Türkçe yaz
✗ JSON, dictionary, key-value formatı KULLANMA
✗ Süslü parantez {{ }} KULLANMA
✗ "ogrenci_adi", "durumu" gibi anahtar kelimeler KULLANMA

ÖRNEK İYİ YANIT:
"Öğrencinin genel performansı düşük (%10). En büyük sorunu tarihsel kavramları yanlış yorumlaması. Özellikle Soru 1 ve 4'te metinleri tamamen yanlış anlamış. Temel tarih kavramlarını tekrar çalışması gerekiyor."

ŞİMDİ SEN YANIT VER (sadece düz metin):"""

        try:
            # Configure for shorter, more concise responses
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 500,  # Increased for better responses
            }

            # Safety settings - more permissive for educational content
            from google.generativeai.types import HarmCategory, HarmBlockThreshold

            safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }

            response = self.model.generate_content(
                prompt, generation_config=generation_config, safety_settings=safety_settings
            )

            # Check if response has valid text
            if not response.candidates:
                return "Üzgünüm, şu anda yanıt veremiyorum. Lütfen sorunuzu farklı şekilde sormayı deneyin."

            candidate = response.candidates[0]

            # Check finish reason first
            if candidate.finish_reason == 2:  # SAFETY
                return "Üzgünüm, sorunuzu farklı bir şekilde sormanızı rica ediyorum."

            # Try to get text safely
            try:
                if hasattr(candidate.content, "parts") and candidate.content.parts:
                    answer = candidate.content.parts[0].text.strip()
                else:
                    return "Üzgünüm, yanıt alınamadı. Lütfen tekrar deneyin."
            except Exception as e:
                print(f"Error extracting text: {e}")
                return "Üzgünüm, yanıt işlenirken bir sorun oluştu."

            # Check if response is JSON and convert to plain text
            if answer.startswith("{") or answer.startswith("["):
                try:
                    import json

                    data = json.loads(answer)
                    # Extract text from common JSON structures
                    if isinstance(data, dict):
                        # Try common keys
                        text_value = data.get("durumu") or data.get("yanit") or data.get("cevap") or data.get("mesaj")
                        if text_value:
                            return text_value
                        # If no common key, join all string values
                        return " ".join(str(v) for v in data.values() if isinstance(v, str))
                except Exception as e:
                    print(f"Error extracting text: {e}")

            return answer

        except Exception as e:
            print(f"Chat error: {str(e)}")
            # Return user-friendly error instead of raising
            return "Üzgünüm, şu anda yanıt veremiyorum. Lütfen daha sonra tekrar deneyin."

    def analyze_student_performance(
        self,
        student_name: str,
        total_score: float,
        max_score: float,
        percentage: float,
        questions_data: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Öğrencinin genel performansını analiz eder ve güçlü/zayıf yönlerini belirler.

        Returns:
            {
                "strengths": ["Güçlü yön 1", "Güçlü yön 2", ...],
                "weaknesses": ["Zayıf yön 1", "Zayıf yön 2", ...]
            }
        """
        # Prepare questions summary
        questions_summary = []
        for q in questions_data:
            q_summary = f"""
Soru {q["question_number"]}: {q["score"]:.1f}/{q["max_score"]:.1f} - {"Doğru" if q.get("is_correct") else "Yanlış"}
Beklenen: {q["expected_answer"][:100]}...
Öğrenci: {q["student_answer"][:100]}...
Feedback: {q["feedback"][:150]}...
"""
            questions_summary.append(q_summary)

        context = f"""ÖĞRENCİ ANALİZİ:
Öğrenci: {student_name}
Toplam Puan: {total_score:.1f}/{max_score:.1f} (%{percentage:.1f})

SORULAR VE CEVAPLAR:
{"".join(questions_summary[:10])}

GÖREV:
Yukarıdaki sınav performansını analiz ederek öğrencinin:
1. GÜÇLÜ YÖNLERİNİ (strengths) - Ne yapıyor iyi? Hangi becerileri güçlü?
2. ZAYIF YÖNLERİNİ (weaknesses) - Nerelerde zorlanıyor? Hangi eksiklikleri var?

KURALLARI belirle.

ÖNEMLİ KURALLAR:
- Her liste için 2-4 madde yaz
- Kısa ve net cümleler kullan (maksimum 10-15 kelime)
- Türkçe yaz
- Spesifik ol (örneğin: "Genel olarak iyi" değil, "Tarihsel olayları kronolojik sıraya koyuyor")
- SADECE aşağıdaki JSON formatında yanıt ver, başka hiçbir şey yazma:

{{
    "strengths": ["Güçlü yön 1", "Güçlü yön 2", "Güçlü yön 3"],
    "weaknesses": ["Zayıf yön 1", "Zayıf yön 2", "Zayıf yön 3"]
}}

SADECE JSON DÖNDÜR. HİÇBİR AÇIKLAMA EKLEME."""

        try:
            # Safety settings
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }

            response = self.model.generate_content(context, safety_settings=safety_settings)

            # Check if response is valid
            if not response.candidates:
                raise ValueError("No response candidates returned from Gemini")

            candidate = response.candidates[0]

            # Check finish reason
            if candidate.finish_reason == 2:  # SAFETY
                raise ValueError("Content was blocked by safety filters")

            # Extract text from response
            if not hasattr(candidate.content, "parts") or not candidate.content.parts:
                raise ValueError("No content parts in response")

            result_text = candidate.content.parts[0].text.strip()

            # Parse JSON response
            result = json.loads(result_text)

            # Validate structure
            if not isinstance(result.get("strengths"), list):
                result["strengths"] = []
            if not isinstance(result.get("weaknesses"), list):
                result["weaknesses"] = []

            return result

        except Exception as e:
            print(f"Error analyzing student performance: {str(e)}")
            # Return default structure
            return {
                "strengths": ["Bazı sorulara doğru yanıt verdi"],
                "weaknesses": ["Genel performans düşük, daha fazla çalışma gerekiyor"],
            }
