from sqlalchemy import select
from sqlalchemy.orm import Session
from openai import OpenAI
import json
import re

from libs.models.body_tracker import BodyTracker
from libs.models.daily_tracker import DailyTracker
from libs.models.user import User
from libs.settings import settings


class TrackerAnalysisService:
    def __init__(self, db: Session):
        self.db = db
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def get_user_tracker(self, user_id: int) -> User:
        result = self.db.execute(select(User).where(User.id == user_id, User.deleted_date.is_(None)))
        return result.scalars().one()

    def analyze_body_tracker(self, tracker_id: int, user_id: int) -> bool:
        result = self.db.execute(
            select(BodyTracker).where(BodyTracker.id == tracker_id, BodyTracker.deleted_date.is_(None))
        )
        tracker = result.scalars().first()

        if not tracker:
            return False

        user = self.get_user_tracker(user_id)
        language = user.language or "en"

        # Get the last 5 body tracker records from the past 3 weeks (excluding the current one)
        from datetime import datetime, timedelta

        three_weeks_ago = datetime.now() - timedelta(weeks=3)

        previous_trackers_result = self.db.execute(
            select(BodyTracker)
            .where(
                BodyTracker.user_id == user_id,
                BodyTracker.id != tracker_id,
                BodyTracker.deleted_date.is_(None),
                BodyTracker.created_date >= three_weeks_ago,
            )
            .order_by(BodyTracker.created_date.desc())
            .limit(5)
        )
        previous_trackers = previous_trackers_result.scalars().all()

        body_info = self._format_body_info(tracker, user, previous_trackers)
        prompt = self.get_body_analysis_prompt(body_info, language)
        print(prompt)
        system_prompt = self.get_body_system_prompt(language)

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000,
            response_format={"type": "json_object"},
        )

        analysis_json = response.choices[0].message.content.strip()
        analysis_data = json.loads(analysis_json)

        tracker.ai_content = analysis_data.get("ai_content", "")
        tracker.rate = self._extract_numeric_value(analysis_data.get("body_rating", "0"))

        self.db.commit()
        return True

    def analyze_daily_tracker(self, tracker_id: int, user_id: int) -> bool:
        result = self.db.execute(
            select(DailyTracker).where(DailyTracker.id == tracker_id, DailyTracker.deleted_date.is_(None))
        )
        tracker = result.scalars().first()

        if not tracker:
            return False

        user = self.get_user_tracker(user_id)
        language = user.language or "en"

        daily_info = self._format_daily_info(tracker, user)
        prompt = self.get_daily_analysis_prompt(daily_info, language)
        system_prompt = self.get_daily_system_prompt(language)

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000,
            response_format={"type": "json_object"},
        )

        analysis_json = response.choices[0].message.content.strip()
        analysis_data = json.loads(analysis_json)

        tracker.ai_content = analysis_data.get("ai_content", "")
        tracker.rate = self._extract_numeric_value(analysis_data.get("wellness_rating", "0"))

        self.db.commit()
        return True

    def get_body_system_prompt(self, language: str = "tr") -> str:
        if language == "tr":
            return """
            Sen bir fitness ve vücut analizi uzmanısın. Kullanıcının vücut ölçülerini bilimsel, anlaşılır ve motive edici şekilde analiz et.
            Yanıtını yalnızca aşağıdaki JSON formatında ve **Türkçe olarak** üret:

            Mutlaka emoji kullan 📏💪🔍 ve gerçek bir fitness uzmanı gibi davran. Kullanıcının vücut ölçülerini değerlendir,
            sağlıklı yaşamı destekleyen öneriler sun ve gelişim için tavsiyelerde bulun.

            Tüm alanları doldur. Eğer bilgi eksikse, mevcut verilerden tahmin yap. Ek açıklama yapma, sadece istenen JSON çıktısını üret.
            """
        else:
            return """
            You are a fitness and body analysis expert. Analyze the user's body measurements in a scientific, clear, and motivating way.
            Return your response **only** in the following JSON format and **in English**:

            Make sure to use emojis 📏💪🔍 and act like a real fitness expert. Evaluate the user's body measurements,
            provide recommendations that support healthy lifestyle, and offer suggestions for improvement.

            Fill in all fields. If information is missing, make educated guesses from available data. Don't add extra explanations, just produce the requested JSON output.
            """

    def get_daily_system_prompt(self, language: str = "tr") -> str:
        if language == "tr":
            return """
            Sen bir sağlık ve wellness uzmanısın. Kullanıcının günlük takip verilerini bilimsel, anlaşılır ve motive edici şekilde analiz et.
            Yanıtını yalnızca aşağıdaki JSON formatında ve **Türkçe olarak** üret:

            Mutlaka emoji kullan 😴💧🧠 ve gerçek bir sağlık uzmanı gibi davran. Kullanıcının uyku, enerji, stres ve diğer günlük verilerini değerlendir,
            sağlıklı yaşamı destekleyen öneriler sun ve iyileştirme için tavsiyelerde bulun.

            Tüm alanları doldur. Eğer bilgi eksikse, mevcut verilerden tahmin yap. Ek açıklama yapma, sadece istenen JSON çıktısını üret.
            """
        else:
            return """
            You are a health and wellness expert. Analyze the user's daily tracking data in a scientific, clear, and motivating way.
            Return your response **only** in the following JSON format and **in English**:

            Make sure to use emojis 😴💧🧠 and act like a real health expert. Evaluate the user's sleep, energy, stress, and other daily metrics,
            provide recommendations that support healthy lifestyle, and offer suggestions for improvement.

            Fill in all fields. If information is missing, make educated guesses from available data. Don't add extra explanations, just produce the requested JSON output.
            """

    def get_body_analysis_prompt(self, body_info: str, language: str = "tr") -> str:
        if language == "tr":
            return f"""
            Aşağıda bir kullanıcının vücut ölçüleri ve kişisel bilgileri yer almaktadır.

            Lütfen vücut ölçülerini, BMI değerini ve genel sağlık durumunu bilimsel ve profesyonel bir bakış açısıyla analiz et.
            Yanıtını yalnızca aşağıdaki JSON formatında ve **Türkçe olarak** üret:

            {{
            "ai_content": "Vücut ölçülerinin detaylı analizi, motive edici kişisel yorum, sağlık açısından değerlendirme ve gelişim önerileri. Emoji kullan 📏💪🔍",
            "body_rating": "Vücut ölçülerinin sağlık açısından genel değerlendirmesi (1–10 arasında bir sayı)",
            "bmi_category": "BMI kategorisi (Zayıf, Normal, Fazla Kilolu, Obez)",
            "recommendations": [
                "Öneri 1",
                "Öneri 2",
                "Öneri 3"
            ]
            }}

            Ek açıklama ya da başka alan verme. Sadece bu alanları içeren JSON üret. Yanıtta tüm analiz metni `ai_content` alanında bulunmalı.

            Kullanıcı Bilgileri:
            {body_info}
            """
        else:
            return f"""
            Below are the body measurements and personal information of a user.

            Please analyze the body measurements, BMI value, and general health status with a scientific and professional approach.
            Respond **only** in the following JSON format and **in English**:

            {{
            "ai_content": "Detailed analysis of body measurements, motivational personal comment, health evaluation, and improvement suggestions. Use emojis 📏💪🔍",
            "body_rating": "Overall health assessment of body measurements (a number from 1 to 10)",
            "bmi_category": "BMI category (Underweight, Normal, Overweight, Obese)",
            "recommendations": [
                "Recommendation 1",
                "Recommendation 2",
                "Recommendation 3"
            ]
            }}

            Do not include any extra explanation or fields—just return this JSON. The entire analysis must be inside the `ai_content` field.

            User Information:
            {body_info}
            """

    def get_daily_analysis_prompt(self, daily_info: str, language: str = "tr") -> str:
        if language == "tr":
            return f"""
            Aşağıda bir kullanıcının günlük takip verileri ve kişisel bilgileri yer almaktadır.

            Lütfen enerji, uyku, stres, kas ağrısı, yorgunluk, açlık, su tüketimi, ruh hali ve antrenman kalitesi gibi günlük verileri bilimsel ve profesyonel bir bakış açısıyla analiz et.
            Yanıtını yalnızca aşağıdaki JSON formatında ve **Türkçe olarak** üret:

            {{
            "ai_content": "Günlük verilerin detaylı analizi, motive edici kişisel yorum, sağlık açısından değerlendirme ve iyileştirme önerileri. Emoji kullan 😴💧🧠",
            "wellness_rating": "Günlük verilerin sağlık açısından genel değerlendirmesi (1–10 arasında bir sayı)",
            "focus_areas": [
                "Odaklanılması gereken alan 1",
                "Odaklanılması gereken alan 2",
                "Odaklanılması gereken alan 3"
            ],
            "recommendations": [
                "Öneri 1",
                "Öneri 2",
                "Öneri 3"
            ]
            }}

            Ek açıklama ya da başka alan verme. Sadece bu alanları içeren JSON üret. Yanıtta tüm analiz metni `ai_content` alanında bulunmalı.

            Kullanıcı Bilgileri:
            {daily_info}
            """
        else:
            return f"""
            Below are the daily tracking data and personal information of a user.

            Please analyze daily metrics such as energy, sleep, stress, muscle soreness, fatigue, hunger, water intake, mood, and training quality with a scientific and professional approach.
            Respond **only** in the following JSON format and **in English**:

            {{
            "ai_content": "Detailed analysis of daily metrics, motivational personal comment, health evaluation, and improvement suggestions. Use emojis 😴💧🧠",
            "wellness_rating": "Overall health assessment of daily metrics (a number from 1 to 10)",
            "focus_areas": [
                "Focus area 1",
                "Focus area 2",
                "Focus area 3"
            ],
            "recommendations": [
                "Recommendation 1",
                "Recommendation 2",
                "Recommendation 3"
            ]
            }}

            Do not include any extra explanation or fields—just return this JSON. The entire analysis must be inside the `ai_content` field.

            User Information:
            {daily_info}
            """

    def _extract_numeric_value(self, value_str: str) -> float:
        if isinstance(value_str, (int, float)):
            return float(value_str)
        match = re.search(r"(\d+(?:\.\d+)?)", str(value_str))
        return float(match.group(1)) if match else 0

    def _format_body_info(self, tracker: BodyTracker, user: User, previous_trackers: list = None) -> str:
        language = user.language or "en"

        if language == "tr":
            body_info = "Kişisel Bilgiler:\n"
            if user.gender:
                body_info += f"Cinsiyet: {user.gender}\n"
            if user.height:
                body_info += f"Boy: {user.height} cm\n"
            if user.weight:
                body_info += f"Kilo: {user.weight} kg\n"
            if user.bmi:
                body_info += f"BMI: {user.bmi}\n"

            body_info += "\nMevcut şu an ki vücut Ölçüleri:\n"
            if tracker.weight:
                body_info += f"Kilo: {tracker.weight} kg\n"
            if tracker.neck:
                body_info += f"Boyun: {tracker.neck} cm\n"
            if tracker.waist:
                body_info += f"Bel: {tracker.waist} cm\n"
            if tracker.shoulder:
                body_info += f"Omuz: {tracker.shoulder} cm\n"
            if tracker.chest:
                body_info += f"Göğüs: {tracker.chest} cm\n"
            if tracker.hip:
                body_info += f"Kalça: {tracker.hip} cm\n"
            if tracker.thigh:
                body_info += f"Uyluk: {tracker.thigh} cm\n"
            if tracker.arm:
                body_info += f"Kol: {tracker.arm} cm\n"
            if tracker.note:
                body_info += f"\nNotlar: {tracker.note}\n"

            if previous_trackers:
                body_info += "\nÖnceki Vücut Ölçüleri:\n"
                for i, previous_tracker in enumerate(previous_trackers):
                    body_info += f"\nÖlçüm {i + 1}:\n"
                    if previous_tracker.weight:
                        body_info += f"Kilo: {previous_tracker.weight} kg\n"
                    if previous_tracker.neck:
                        body_info += f"Boyun: {previous_tracker.neck} cm\n"
                    if previous_tracker.waist:
                        body_info += f"Bel: {previous_tracker.waist} cm\n"
                    if previous_tracker.shoulder:
                        body_info += f"Omuz: {previous_tracker.shoulder} cm\n"
                    if previous_tracker.chest:
                        body_info += f"Göğüs: {previous_tracker.chest} cm\n"
                    if previous_tracker.hip:
                        body_info += f"Kalça: {previous_tracker.hip} cm\n"
                    if previous_tracker.thigh:
                        body_info += f"Uyluk: {previous_tracker.thigh} cm\n"
                    if previous_tracker.arm:
                        body_info += f"Kol: {previous_tracker.arm} cm\n"
                    if previous_tracker.note:
                        body_info += f"\nNotlar: {previous_tracker.note}\n"
        else:
            body_info = "Personal Information:\n"
            if user.gender:
                body_info += f"Gender: {user.gender}\n"
            if user.height:
                body_info += f"Height: {user.height} cm\n"
            if user.weight:
                body_info += f"Weight: {user.weight} kg\n"
            if user.bmi:
                body_info += f"BMI: {user.bmi}\n"

            body_info += "\n Current Body Measurements:\n"
            if tracker.weight:
                body_info += f"Weight: {tracker.weight} kg\n"
            if tracker.neck:
                body_info += f"Neck: {tracker.neck} cm\n"
            if tracker.waist:
                body_info += f"Waist: {tracker.waist} cm\n"
            if tracker.shoulder:
                body_info += f"Shoulder: {tracker.shoulder} cm\n"
            if tracker.chest:
                body_info += f"Chest: {tracker.chest} cm\n"
            if tracker.hip:
                body_info += f"Hip: {tracker.hip} cm\n"
            if tracker.thigh:
                body_info += f"Thigh: {tracker.thigh} cm\n"
            if tracker.arm:
                body_info += f"Arm: {tracker.arm} cm\n"
            if tracker.note:
                body_info += f"\nNotes: {tracker.note}\n"

            if previous_trackers:
                body_info += "\nPrevious Body Measurements:\n"
                for i, previous_tracker in enumerate(previous_trackers):
                    body_info += (
                        f"\nMeasurement {i + 1} - {previous_tracker.created_date.strftime('%Y-%m-%d %H:%M')}:\n"
                    )
                    if previous_tracker.weight:
                        body_info += f"Weight: {previous_tracker.weight} kg\n"
                    if previous_tracker.neck:
                        body_info += f"Neck: {previous_tracker.neck} cm\n"
                    if previous_tracker.waist:
                        body_info += f"Waist: {previous_tracker.waist} cm\n"
                    if previous_tracker.shoulder:
                        body_info += f"Shoulder: {previous_tracker.shoulder} cm\n"
                    if previous_tracker.chest:
                        body_info += f"Chest: {previous_tracker.chest} cm\n"
                    if previous_tracker.hip:
                        body_info += f"Hip: {previous_tracker.hip} cm\n"
                    if previous_tracker.thigh:
                        body_info += f"Thigh: {previous_tracker.thigh} cm\n"
                    if previous_tracker.arm:
                        body_info += f"Arm: {previous_tracker.arm} cm\n"
                    if previous_tracker.note:
                        body_info += f"\nNotes: {previous_tracker.note}\n"

        return body_info

    def _format_daily_info(self, tracker: DailyTracker, user: User) -> str:
        language = user.language or "en"

        if language == "tr":
            daily_info = "Kişisel Bilgiler:\n"
            if user.gender:
                daily_info += f"Cinsiyet: {user.gender}\n"
            if user.height:
                daily_info += f"Boy: {user.height} cm\n"
            if user.weight:
                daily_info += f"Kilo: {user.weight} kg\n"
            if user.bmi:
                daily_info += f"BMI: {user.bmi}\n"

            daily_info += "\nGünlük Takip Verileri:\n"
            if tracker.energy is not None:
                daily_info += f"Enerji Seviyesi: {tracker.energy}/10\n"
            if tracker.sleep is not None:
                daily_info += f"Uyku Kalitesi: {tracker.sleep}/10\n"
            if tracker.sleep_hours is not None:
                daily_info += f"Uyku Süresi: {tracker.sleep_hours} saat\n"
            if tracker.stress is not None:
                daily_info += f"Stres Seviyesi: {tracker.stress}/10\n"
            if tracker.muscle_soreness is not None:
                daily_info += f"Kas Ağrısı: {tracker.muscle_soreness}/10\n"
            if tracker.fatigue is not None:
                daily_info += f"Yorgunluk: {tracker.fatigue}/10\n"
            if tracker.hunger is not None:
                daily_info += f"Açlık: {tracker.hunger}/10\n"
            if tracker.water_intake_liters is not None:
                daily_info += f"Su Tüketimi: {tracker.water_intake_liters} litre\n"
            if tracker.mood:
                daily_info += f"Ruh Hali: {tracker.mood}\n"
            if tracker.bowel_movement:
                daily_info += f"Bağırsak Hareketi: {tracker.bowel_movement}\n"
            if tracker.training_quality is not None:
                daily_info += f"Antrenman Kalitesi: {tracker.training_quality}/10\n"
            if tracker.diet_compliance is not None:
                daily_info += f"Diyet Uyumu: {tracker.diet_compliance}/10\n"
            if tracker.training_compliance is not None:
                daily_info += f"Antrenman Uyumu: {tracker.training_compliance}/10\n"
            if tracker.note:
                daily_info += f"\nNotlar: {tracker.note}\n"
        else:
            daily_info = "Personal Information:\n"
            if user.gender:
                daily_info += f"Gender: {user.gender}\n"
            if user.height:
                daily_info += f"Height: {user.height} cm\n"
            if user.weight:
                daily_info += f"Weight: {user.weight} kg\n"
            if user.bmi:
                daily_info += f"BMI: {user.bmi}\n"

            daily_info += "\nDaily Tracking Data:\n"
            if tracker.energy is not None:
                daily_info += f"Energy Level: {tracker.energy}/10\n"
            if tracker.sleep is not None:
                daily_info += f"Sleep Quality: {tracker.sleep}/10\n"
            if tracker.sleep_hours is not None:
                daily_info += f"Sleep Duration: {tracker.sleep_hours} hours\n"
            if tracker.stress is not None:
                daily_info += f"Stress Level: {tracker.stress}/10\n"
            if tracker.muscle_soreness is not None:
                daily_info += f"Muscle Soreness: {tracker.muscle_soreness}/10\n"
            if tracker.fatigue is not None:
                daily_info += f"Fatigue: {tracker.fatigue}/10\n"
            if tracker.hunger is not None:
                daily_info += f"Hunger: {tracker.hunger}/10\n"
            if tracker.water_intake_liters is not None:
                daily_info += f"Water Intake: {tracker.water_intake_liters} liters\n"
            if tracker.mood:
                daily_info += f"Mood: {tracker.mood}\n"
            if tracker.bowel_movement:
                daily_info += f"Bowel Movement: {tracker.bowel_movement}\n"
            if tracker.training_quality is not None:
                daily_info += f"Training Quality: {tracker.training_quality}/10\n"
            if tracker.diet_compliance is not None:
                daily_info += f"Diet Compliance: {tracker.diet_compliance}/10\n"
            if tracker.training_compliance is not None:
                daily_info += f"Training Compliance: {tracker.training_compliance}/10\n"
            if tracker.note:
                daily_info += f"\nNotes: {tracker.note}\n"

        return daily_info
