from sqlalchemy import select
from sqlalchemy.orm import Session

from libs.models.body_tracker import BodyTracker
from libs.models.daily_tracker import DailyTracker


class TrackerAnalysisService:
    def __init__(self, db: Session):
        self.db = db

    def analyze_body_tracker(self, tracker_id: int) -> bool:
        """
        Analyze body tracker data and generate AI content

        Args:
            tracker_id: ID of the body tracker to analyze

        Returns:
            bool: True if analysis was successful, False otherwise
        """
        # Get the body tracker data
        result = self.db.execute(
            select(BodyTracker).where(BodyTracker.id == tracker_id, BodyTracker.deleted_date.is_(None))
        )
        tracker = result.scalars().first()

        if not tracker:
            return False

        # In the future, this will call OpenAI API
        # For now, generate static analysis based on the data
        ai_content = self._generate_body_tracker_analysis(tracker)

        # Update the tracker with AI content
        tracker.ai_content = ai_content
        self.db.commit()

        return True

    def analyze_daily_tracker(self, tracker_id: int) -> bool:
        """
        Analyze daily tracker data and generate AI content

        Args:
            tracker_id: ID of the daily tracker to analyze

        Returns:
            bool: True if analysis was successful, False otherwise
        """
        # Get the daily tracker data
        result = self.db.execute(
            select(DailyTracker).where(DailyTracker.id == tracker_id, DailyTracker.deleted_date.is_(None))
        )
        tracker = result.scalars().first()

        if not tracker:
            return False

        # In the future, this will call OpenAI API
        # For now, generate static analysis based on the data
        ai_content = self._generate_daily_tracker_analysis(tracker)

        # Update the tracker with AI content
        tracker.ai_content = ai_content
        self.db.commit()

        return True

    def _generate_body_tracker_analysis(self, tracker: BodyTracker) -> str:
        """
        Generate analysis for body tracker data

        Args:
            tracker: Body tracker object

        Returns:
            str: Generated analysis
        """
        # Basic template for body analysis
        analysis = []

        # Weight analysis
        if tracker.weight:
            analysis.append(f"Your current weight is {tracker.weight} kg.")

        # Measurements analysis
        measurements = []
        if tracker.waist:
            measurements.append(f"waist: {tracker.waist} cm")
        if tracker.chest:
            measurements.append(f"chest: {tracker.chest} cm")
        if tracker.hip:
            measurements.append(f"hip: {tracker.hip} cm")
        if tracker.thigh:
            measurements.append(f"thigh: {tracker.thigh} cm")
        if tracker.arm:
            measurements.append(f"arm: {tracker.arm} cm")

        if measurements:
            analysis.append(f"Your current measurements ({', '.join(measurements)}) indicate a balanced physique.")

        # Add general advice
        analysis.append("Keep tracking your measurements regularly to monitor your progress effectively.")

        # Combine all analysis points
        if not analysis:
            return "Not enough data to provide meaningful analysis."

        return "\n\n".join(analysis)

    def _generate_daily_tracker_analysis(self, tracker: DailyTracker) -> str:
        """
        Generate analysis for daily tracker data

        Args:
            tracker: Daily tracker object

        Returns:
            str: Generated analysis
        """
        # Basic template for daily analysis
        analysis = []

        # Energy and sleep analysis
        if tracker.energy is not None and tracker.sleep is not None:
            if tracker.energy < 5 and tracker.sleep < 5:
                analysis.append(
                    "Your energy and sleep levels are low. Consider improving your sleep quality and duration."
                )
            elif tracker.energy >= 7 and tracker.sleep >= 7:
                analysis.append("Great job! Your energy and sleep levels are optimal.")
            else:
                analysis.append("Your energy and sleep patterns show room for improvement.")

        # Stress analysis
        if tracker.stress is not None:
            if tracker.stress > 7:
                analysis.append(
                    "Your stress levels are high. Consider incorporating stress-reduction techniques like meditation or deep breathing exercises."
                )
            elif tracker.stress <= 3:
                analysis.append("Your stress levels are well-managed. Keep up the good work!")

        # Water intake analysis
        if tracker.water_intake_liters is not None:
            if tracker.water_intake_liters < 2:
                analysis.append(
                    f"You consumed {tracker.water_intake_liters} liters of water. Consider increasing your water intake to at least 2-3 liters per day."
                )
            else:
                analysis.append(f"Great job staying hydrated with {tracker.water_intake_liters} liters of water!")

        # Training and diet compliance
        if tracker.training_quality is not None and tracker.diet_compliance is not None:
            if tracker.training_quality >= 7 and tracker.diet_compliance >= 7:
                analysis.append("You're doing excellent with both your training and diet compliance!")
            elif tracker.training_quality < 5 and tracker.diet_compliance < 5:
                analysis.append(
                    "Your training quality and diet compliance could use some improvement. Consider setting smaller, achievable goals."
                )
            else:
                analysis.append(
                    "Your training and diet habits show a good foundation. Keep building on this consistency."
                )

        # Add general advice
        analysis.append(
            "Continue tracking your daily habits to identify patterns and make informed adjustments to your lifestyle."
        )

        # Combine all analysis points
        if not analysis:
            return "Not enough data to provide meaningful analysis."

        return "\n\n".join(analysis)
