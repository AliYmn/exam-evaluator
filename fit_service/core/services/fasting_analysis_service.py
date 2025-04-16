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

    def get_meal_system_prompt(self) -> str:
        return """
        Sen bir beslenme ve diyet uzmanısın. Kullanıcının yemeğini bilimsel, anlaşılır ve motive edici şekilde analiz et.
        Yanıtı **yalnızca aşağıdaki JSON formatında** döndür. Görsel varsa onu da kullan.

        Mutlaka emoji kullan 🥗🔥✅ ve gerçek bir diyetisyen gibi davran. Kullanıcının oruç hedeflerine uygun, sağlıklı yaşamı destekleyen öneriler sun.

        Tüm alanları doldur. Eğer bilgi eksikse, görselden tahmin yap. Ek açıklama yapma, sadece istenen JSON çıktısını üret.
        """

    def get_workout_system_prompt(self) -> str:
        return """
        Sen bir spor ve fitness uzmanısın. Kullanıcının antrenmanını bilimsel, anlaşılır ve motive edici şekilde analiz et.
        Yanıtı **yalnızca aşağıdaki JSON formatında** döndür.

        Mutlaka emoji kullan 🏋️‍♂️💪🔥 ve gerçek bir spor uzmanı gibi davran. Kullanıcının fitness hedeflerine uygun, sağlıklı yaşamı destekleyen öneriler sun.

        Tüm alanları doldur. Eğer bilgi eksikse, notlardan tahmin yap. Ek açıklama yapma, sadece istenen JSON çıktısını üret.
        """

    def get_meal_analysis_prompt(self, meal_info: str) -> str:
        return f"""
        Aşağıda bir kullanıcının günlük yemek günlüğü bilgileri yer almaktadır.
        Yemeğin tahmini makro ve mikro besin değerlerini analiz et, sağlık açısından uygunluğunu değerlendir ve motive edici, kişisel bir açıklama yaz. Lütfen açıklamada emoji kullan 🥦🍗💬.

        Yanıtını yalnızca aşağıdaki JSON formatında ve Türkçe olarak oluştur:

        {{
        "ai_content": "Yemeğin içeriği ve sağlık açısından değerlendirilmesi, motive edici bir kişisel yorum (emoji kullanarak)",
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

    def get_workout_analysis_prompt(self, workout_info: str) -> str:
        return f"""
        Aşağıda kullanıcının spor günlüğü verileri bulunmaktadır.

        Lütfen antrenmanın türünü, süresini, zorluk seviyesini ve genel sağlık üzerindeki etkilerini bilimsel ve profesyonel bir bakış açısıyla analiz et.
        Yanıtı yalnızca aşağıdaki JSON formatında ve Türkçe olarak oluştur:

        {{
        "ai_content": "Antrenman analizi ve motive edici kişisel yorum (emoji kullanarak)",
        "calories_accuracy": "Yakılan kalori tahmini doğruluğu (düşük/orta/yüksek)",
        "intensity_evaluation": "Antrenman yoğunluğu değerlendirmesi",
        "training_effect": "Antrenmanın vücut üzerindeki etkileri",
        "recommendations": "İyileştirme önerileri",
        "benefits": {{
            "cardiovascular": "Kardiyovasküler sistem üzerindeki faydalar",
            "muscular": "Kas sistemi üzerindeki faydalar",
            "metabolic": "Metabolik faydalar",
            "mental": "Zihinsel faydalar"
        }}
        }}

        Spor Bilgileri:
        {workout_info}
        """

    def analyze_workout_log(self, log_id: int) -> bool:
        log = self.db.execute(
            select(FastingWorkoutLog).where(FastingWorkoutLog.id == log_id, FastingWorkoutLog.deleted_date.is_(None))
        ).scalar_one()

        workout_info = self._format_workout_info(log)
        prompt = self.get_workout_analysis_prompt(workout_info)
        system_prompt = self.get_workout_system_prompt()

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

        calories_estimate = analysis_data.get("calories", analysis_data.get("estimated_calories", None))
        if calories_estimate:
            log.calories_burned = self._extract_numeric_value(str(calories_estimate))

        self.db.commit()
        return True

    def analyze_meal_log(self, log_id: int) -> bool:
        log = self.db.execute(
            select(FastingMealLog).where(FastingMealLog.id == log_id, FastingMealLog.deleted_date.is_(None))
        ).scalar_one()

        prompt = self.get_meal_analysis_prompt(self._format_meal_info(log))
        system_prompt = self.get_meal_system_prompt()

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
        log.fat = self._extract_numeric_value(analysis_data.get("macros", {}).get("fats", {}).get("total", "0"))
        log.detailed_macros = analysis_data.get("macros", {})
        self.db.commit()
        return True

    def _extract_numeric_value(self, value_str: str) -> float:
        match = re.search(r"(\d+(?:\.\d+)?)", value_str)
        return float(match.group(1)) if match else 0

    def _format_workout_info(self, log: FastingWorkoutLog) -> str:
        workout_info = f"Antrenman Adı: {log.workout_name}\n"
        workout_info += f"Süre: {log.duration_minutes} dakika\n"
        workout_info += f"Zorluk Seviyesi: {log.intensity}\n"
        workout_info += f"Yakılan Kalori: {log.calories_burned}\n"
        if log.notes:
            workout_info += f"Notlar: {log.notes}\n"
        return workout_info

    def _format_meal_info(self, log: FastingMealLog) -> str:
        meal_info = ""
        if log.title:
            meal_info += f"Yemek Başlığı: {log.title}\n"
        if log.photo_url:
            meal_info += f"Fotoğraf URL: {log.photo_url}\n"
        if log.notes:
            meal_info += f"Notlar: {log.notes}\n"
        return meal_info
