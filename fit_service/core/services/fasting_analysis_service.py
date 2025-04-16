from sqlalchemy import select
from sqlalchemy.orm import Session
from openai import OpenAI
from libs.settings import settings
from libs.models.fasting import FastingMealLog, FastingWorkoutLog
import json
import re


class FastingAnalysisService:
    def __init__(self, db: Session):
        self.db = db
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def get_meal_system_prompt(self, language: str = "tr") -> str:
        if language == "tr":
            return """
            Sen bir beslenme ve diyet uzmanısın. Kullanıcının yemeğini bilimsel, anlaşılır ve motive edici şekilde analiz et.
            Yanıtı **yalnızca aşağıdaki JSON formatında** döndür. Görsel varsa onu da kullan.

            Mutlaka emoji kullan 🥗🔥✅ ve gerçek bir diyetisyen gibi davran. Kullanıcının oruç hedeflerine uygun, sağlıklı yaşamı destekleyen öneriler sun.

            Tüm alanları doldur. Eğer bilgi eksikse, görselden tahmin yap. Ek açıklama yapma, sadece istenen JSON çıktısını üret.
            """
        else:
            return """
            You are a nutrition and diet expert. Analyze the user's meal in a scientific, clear, and motivating way.
            Return your response **only in the JSON format** specified below. If there's an image, use it in your analysis.

            Make sure to use emojis 🥗🔥✅ and act like a real dietitian. Provide recommendations that support the user's fasting goals and healthy lifestyle.

            Fill in all fields. If information is missing, make educated guesses from the image. Don't add extra explanations, just produce the requested JSON output.
            """

    def get_workout_system_prompt(self, language: str = "tr") -> str:
        if language == "tr":
            return """
            Sen bir spor ve fitness uzmanısın. Kullanıcının antrenmanını bilimsel, anlaşılır ve motive edici şekilde analiz et.
            Yanıtı **yalnızca aşağıdaki JSON formatında** döndür.

            Mutlaka emoji kullan 🏋️‍♂️💪🔥 ve gerçek bir spor uzmanı gibi davran. Kullanıcının fitness hedeflerine uygun, sağlıklı yaşamı destekleyen öneriler sun.

            Tüm alanları doldur. Eğer bilgi eksikse, notlardan tahmin yap. Ek açıklama yapma, sadece istenen JSON çıktısını üret.
            """
        else:
            return """
            You are a sports and fitness expert. Analyze the user's workout in a scientific, clear, and motivating way.
            Return your response **only in the JSON format** specified below.

            Make sure to use emojis 🏋️‍♂️💪🔥 and act like a real fitness trainer. Provide recommendations that support the user's fitness goals and healthy lifestyle.

            Fill in all fields. If information is missing, make educated guesses from the notes. Don't add extra explanations, just produce the requested JSON output.
            """

    def get_meal_analysis_prompt(self, meal_info: str, language: str = "tr") -> str:
        if language == "tr":
            return f"""
            Aşağıda bir kullanıcının günlük yemek günlüğü bilgileri yer almaktadır.
            Yemeğin tahmini makro ve mikro besin değerlerini analiz et, sağlık açısından uygunluğunu değerlendir ve motive edici,
            kişisel bir açıklama yaz. Lütfen açıklamada emoji kullan 🥦🍗💬.

            Yanıtını yalnızca aşağıdaki JSON formatında ve Türkçe olarak oluştur:

            {{
            "ai_content": "Yemeğin içeriği ve sağlık açısından değerlendirilmesi, motive edici bir kişisel yorum (emoji kullanarak)",
            "health_rating": "Yemeğin sağlık açısından değerlendirilmesi (1–10 scale, e.g., 8)",
            "calories": "Toplam tahmini kalori (örnek: 450 kcal)",
            "macros": {{
                "protein": "Tahmini protein miktarı (örnek: 30g)",
                "carbohydrates": {{
                    "total": "Toplam karbonhidrat (örnek: 50g)",
                    "fiber": "Lif (örnek: 7g)",
                    "sugar": "Şeker (örnek: 6g)"
                }},
                "fats": {{
                    "total": "Toplam yağ (örnek: 15g)",
                    "saturated": "Doymuş yağ (örnek: 3g)",
                    "unsaturated": {{
                        "monounsaturated": "Tekli doymamış yağ (örnek: 7g)",
                        "polyunsaturated": "Çoklu doymamış yağ (örnek: 5g)"
                    }},
                    "trans": "Trans yağ (örnek: 0g)"
                }}
            }},
            "micros": {{
                "vitamins": [
                    {{ "name": "Vitamin A", "amount": "700 IU" }},
                    {{ "name": "Vitamin C", "amount": "60 mg" }}
                ],
                "minerals": [
                    {{ "name": "Kalsiyum", "amount": "250 mg" }},
                    {{ "name": "Demir", "amount": "8 mg" }}
                ]
            }}
            }}

            Yemek Bilgileri:
            {meal_info}
            """
        else:
            return f"""
            Below are the details from a user's daily meal log.
            Analyze the estimated macro and micro nutrients of the meal, evaluate its health suitability, and write a motivating,
            personalized comment. Please use emojis in your explanation 🥦🍗💬.

            Create your response only in the following JSON format and in English:

            {{
            "ai_content": "Analysis of the meal content and health evaluation, a motivating personal comment (using emojis)",
            "health_rating": "Overall health rating of the meal (1–10 scale, e.g., 8)",
            "calories": "Total estimated calories (example: 450 kcal)",
            "macros": {{
                "protein": "Estimated protein amount (example: 30g)",
                "carbohydrates": {{
                    "total": "Total carbohydrates (example: 50g)",
                    "fiber": "Fiber (example: 7g)",
                    "sugar": "Sugar (example: 6g)"
                }},
                "fats": {{
                    "total": "Total fat (example: 15g)",
                    "saturated": "Saturated fat (example: 3g)",
                    "unsaturated": {{
                        "monounsaturated": "Monounsaturated fat (example: 7g)",
                        "polyunsaturated": "Polyunsaturated fat (example: 5g)"
                    }},
                    "trans": "Trans fat (example: 0g)"
                }}
            }},
            "micros": {{
                "vitamins": [
                    {{ "name": "Vitamin A", "amount": "700 IU" }},
                    {{ "name": "Vitamin C", "amount": "60 mg" }}
                ],
                "minerals": [
                    {{ "name": "Calcium", "amount": "250 mg" }},
                    {{ "name": "Iron", "amount": "8 mg" }}
                ]
            }}
            }}

            Meal Information:
            {meal_info}
            """

    def get_workout_analysis_prompt(self, workout_info: str, language: str = "tr") -> str:
        if language == "tr":
            return f"""
            Aşağıda kullanıcının spor günlüğü verileri yer almaktadır.

            Lütfen antrenmanın türünü, süresini, zorluk seviyesini ve genel sağlık üzerindeki etkilerini bilimsel ve profesyonel bir bakış açısıyla analiz et.
            Yanıtını yalnızca aşağıdaki JSON formatında ve **Türkçe olarak** üret:

            {{
            "ai_content": "Antrenmanın tüm değerlendirmesi, motive edici kişisel yorum ve kalori doğruluğu, zorluk seviyesi, faydalar gibi tüm detaylar bu alanda açıklanmalı. Emoji kullan 🏃‍♀️💪🔥",
            "workout_rating": "Antrenmanın sağlık açısından genel değerlendirmesi (1–10 arasında bir sayı)",
            "estimated_calories": "Tahmini yakılan kalori miktarı (örnek: 320 kcal)",
            }}

            Ek açıklama ya da başka alan verme. Sadece bu iki alanı içeren JSON üret. Yanıtta tüm analiz metni `ai_content` alanında bulunmalı.

            Spor Bilgileri:
            {workout_info}
            """
        else:
            return f"""
            Below is a user's workout log information.

            Please analyze the type, duration, intensity, and health effects of the workout with a professional and scientific approach.
            Respond **only** in the following JSON format and **in English**:

            {{
            "ai_content": "Full workout evaluation, motivational personal comment, including intensity, calorie accuracy, benefits, and suggestions. Use emojis 🏃‍♂️🔥💪",
            "workout_rating": "Overall workout health and effectiveness score (a number from 1 to 10)",
            "estimated_calories": "Estimated calories burned (e.g., 320 kcal)"
            }}

            Do not include any extra explanation or fields—just return this JSON. The entire analysis must be inside the `ai_content` field.

            Workout Information:
            {workout_info}
            """

    def analyze_workout_log(self, log_id: int, language: str = "tr") -> bool:
        log = self.db.execute(
            select(FastingWorkoutLog).where(FastingWorkoutLog.id == log_id, FastingWorkoutLog.deleted_date.is_(None))
        ).scalar_one()

        workout_info = self._format_workout_info(log, language)
        prompt = self.get_workout_analysis_prompt(workout_info, language)
        system_prompt = self.get_workout_system_prompt(language)

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000,
            response_format={"type": "json_object"},
        )

        analysis_json = response.choices[0].message.content.strip()
        analysis_data = json.loads(analysis_json)

        log.ai_content = analysis_data.get("ai_content", "")
        log.rate = self._extract_numeric_value(analysis_data.get("workout_rating", "0"))

        calories_estimate = self._extract_numeric_value(analysis_data.get("estimated_calories", "0"))
        if not log.calories_burned:
            log.calories_burned = calories_estimate

        self.db.commit()
        return True

    def analyze_meal_log(self, log_id: int, language: str = "tr") -> bool:
        log = self.db.execute(
            select(FastingMealLog).where(FastingMealLog.id == log_id, FastingMealLog.deleted_date.is_(None))
        ).scalar_one()

        prompt = self.get_meal_analysis_prompt(self._format_meal_info(log, language), language)
        system_prompt = self.get_meal_system_prompt(language)

        content = [{"type": "text", "text": prompt}]
        if log.photo_url and log.photo_url.strip():
            content.append({"type": "image_url", "image_url": {"url": log.photo_url.strip()}})

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": content}],
            temperature=0.7,
            max_tokens=1000,
            response_format={"type": "json_object"},
        )

        analysis_data = json.loads(response.choices[0].message.content.strip())
        log.ai_content = analysis_data.get("ai_content", "")
        log.calories = self._extract_numeric_value(analysis_data.get("calories", "0"))
        log.protein = self._extract_numeric_value(analysis_data.get("macros", {}).get("protein", "0"))
        log.carbs = self._extract_numeric_value(
            analysis_data.get("macros", {}).get("carbohydrates", {}).get("total", "0")
        )
        log.rate = self._extract_numeric_value(analysis_data.get("health_rating", "0"))
        log.fat = self._extract_numeric_value(analysis_data.get("macros", {}).get("fats", {}).get("total", "0"))
        log.detailed_macros = analysis_data.get("macros", {})
        self.db.commit()
        return True

    def _extract_numeric_value(self, value_str: str) -> float:
        match = re.search(r"(\d+(?:\.\d+)?)", value_str)
        return float(match.group(1)) if match else 0

    def _format_workout_info(self, log: FastingWorkoutLog, language: str = "tr") -> str:
        if language == "tr":
            workout_info = f"Antrenman Adı: {log.workout_name}\n"
            workout_info += f"Süre: {log.duration_minutes} dakika\n"
            workout_info += f"Zorluk Seviyesi: {log.intensity}\n"
            if log.notes:
                workout_info += f"Notlar: {log.notes}\n"
            return workout_info
        else:
            workout_info = f"Workout Name: {log.workout_name}\n"
            workout_info += f"Duration: {log.duration_minutes} minutes\n"
            workout_info += f"Intensity: {log.intensity}\n"
            if log.notes:
                workout_info += f"Notes: {log.notes}\n"
            return workout_info

    def _format_meal_info(self, log: FastingMealLog, language: str = "tr") -> str:
        if language == "tr":
            meal_info = ""
            if log.title:
                meal_info += f"Yemek Başlığı: {log.title}\n"
            if log.photo_url:
                meal_info += f"Fotoğraf URL: {log.photo_url}\n"
            if log.notes:
                meal_info += f"Notlar: {log.notes}\n"
            return meal_info
        else:
            meal_info = ""
            if log.title:
                meal_info += f"Meal Title: {log.title}\n"
            if log.photo_url:
                meal_info += f"Image URL: {log.photo_url}\n"
            if log.notes:
                meal_info += f"Notes: {log.notes}\n"
            return meal_info
