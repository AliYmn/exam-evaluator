from sqlalchemy import select
from sqlalchemy.orm import Session

from libs.models.fasting import FastingMealLog, FastingWorkoutLog


class FastingAnalysisService:
    def __init__(self, db: Session):
        self.db = db

    def analyze_workout_log(self, log_id: int) -> bool:
        """
        Analyze workout log data and generate AI content

        Args:
            log_id: ID of the workout log to analyze

        Returns:
            bool: True if analysis was successful, False otherwise
        """
        # Get the workout log data
        result = self.db.execute(
            select(FastingWorkoutLog).where(FastingWorkoutLog.id == log_id, FastingWorkoutLog.deleted_date.is_(None))
        )
        log = result.scalars().first()

        if not log:
            return False

        # In the future, this will call OpenAI API
        # For now, generate static analysis based on the data
        ai_content = self._generate_workout_analysis(log)

        # Update the log with AI content
        log.ai_content = ai_content
        self.db.commit()

        return True

    def analyze_meal_log(self, log_id: int) -> bool:
        """
        Analyze meal log data and generate AI content

        Args:
            log_id: ID of the meal log to analyze

        Returns:
            bool: True if analysis was successful, False otherwise
        """
        # Get the meal log data
        result = self.db.execute(
            select(FastingMealLog).where(FastingMealLog.id == log_id, FastingMealLog.deleted_date.is_(None))
        )
        log = result.scalars().first()

        if not log:
            return False

        # In the future, this will call OpenAI API
        # For now, generate static analysis based on the data
        ai_content = self._generate_meal_analysis(log)

        # Update the log with AI content
        log.ai_content = ai_content
        self.db.commit()

        return True

    def _generate_workout_analysis(self, log: FastingWorkoutLog) -> str:
        """
        Generate analysis for workout log data

        Args:
            log: Workout log object

        Returns:
            str: Generated analysis
        """
        # Basic template for workout analysis
        analysis = []

        # Workout name analysis
        analysis.append(f"You completed a {log.workout_name} workout.")

        # Duration analysis
        if log.duration_minutes:
            if log.duration_minutes < 30:
                analysis.append(
                    f"Your workout duration was {log.duration_minutes} minutes. "
                    f"Even short workouts are beneficial during fasting periods."
                )
            elif log.duration_minutes >= 30 and log.duration_minutes < 60:
                analysis.append(
                    f"Great job completing a {log.duration_minutes}-minute workout! "
                    f"This is an ideal duration during fasting periods."
                )
            else:
                analysis.append(
                    f"You completed a {log.duration_minutes}-minute workout. "
                    f"Remember to stay hydrated during longer workouts while fasting."
                )

        # Intensity analysis
        if log.intensity:
            if log.intensity.lower() == "low":
                analysis.append(
                    "Low intensity workouts are perfect during fasting periods, "
                    "helping to preserve energy while still providing benefits."
                )
            elif log.intensity.lower() == "medium":
                analysis.append(
                    "Medium intensity workouts provide a good balance of calorie burn "
                    "and energy preservation during fasting."
                )
            elif log.intensity.lower() == "high":
                analysis.append(
                    "High intensity workouts can be challenging during fasting. "
                    "Make sure to schedule these during your eating window when possible."
                )

        # Calories burned analysis
        if log.calories_burned:
            analysis.append(f"You burned approximately {log.calories_burned} calories during this workout.")

        # Add general advice
        analysis.append(
            "Regular exercise during intermittent fasting can enhance fat burning and improve metabolic health."
        )

        # Combine all analysis points
        if not analysis:
            return "Not enough data to provide meaningful analysis."

        return "\n\n".join(analysis)

    def _generate_meal_analysis(self, log: FastingMealLog) -> str:
        """
        Generate analysis for meal log data

        Args:
            log: Meal log object

        Returns:
            str: Generated analysis
        """
        # Basic template for meal analysis
        analysis = []

        # Photo and notes analysis
        if log.photo_url and log.notes:
            analysis.append(
                "You've logged a meal with both a photo and notes. Great job tracking your nutrition in detail!"
            )
        elif log.photo_url:
            analysis.append(
                "You've logged a meal with a photo. Visual tracking helps maintain awareness of portion sizes."
            )
        elif log.notes:
            analysis.append(f'Your meal notes: "{log.notes}"')

        # Nutritional information analysis
        if log.calories is not None:
            if log.calories < 500:
                analysis.append(
                    f"This meal contains {log.calories} calories, which is relatively light. "
                    f"Consider if this provides enough nutrition for your needs."
                )
            elif log.calories >= 500 and log.calories < 800:
                analysis.append(
                    f"This meal contains {log.calories} calories, "
                    f"which is a moderate amount suitable for most eating windows."
                )
            else:
                analysis.append(
                    f"This meal contains {log.calories} calories. "
                    f"Larger meals are fine during your eating window, especially if you're having fewer meals per day."
                )

        # Macronutrient analysis
        if log.protein is not None and log.carbs is not None and log.fat is not None:
            analysis.append(f"Macronutrient breakdown: {log.protein}g protein, {log.carbs}g carbs, {log.fat}g fat.")

            # Protein analysis
            if log.protein >= 30:
                analysis.append(
                    "Your protein intake is good. Adequate protein helps preserve muscle mass during fasting periods."
                )
            elif log.protein < 20:
                analysis.append(
                    "Consider increasing your protein intake to help preserve muscle mass during fasting periods."
                )

            # Carbs analysis
            if log.carbs < 50:
                analysis.append("Your meal is low in carbohydrates, which can help maintain stable blood sugar levels.")
            elif log.carbs > 100:
                analysis.append(
                    "Your meal is higher in carbohydrates. "
                    "Consider the timing of carb-heavy meals in relation to your fasting schedule."
                )

        # Add general advice
        analysis.append(
            "Focus on nutrient-dense foods during your eating window to maximize the benefits of intermittent fasting."
        )

        # Combine all analysis points
        if not analysis:
            return "Not enough data to provide meaningful analysis."

        return "\n\n".join(analysis)
