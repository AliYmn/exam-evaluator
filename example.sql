-- Example data for the workout and diet models
-- This file contains raw SQL queries to populate the database with sample data

-- Insert a test user (if not already exists)
INSERT INTO users (username, email, password_hash, is_active, is_verified, role, first_name, last_name)
VALUES ('testuser', 'test@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', true, true, 'user', 'Test', 'User')
ON CONFLICT (username) DO NOTHING
RETURNING id;

-- Get the user ID for reference in other queries
DO $$
DECLARE
    user_id integer;
BEGIN
    SELECT id INTO user_id FROM users WHERE username = 'testuser';

    -- =====================
    -- WORKOUT DATA EXAMPLES
    -- =====================

    -- Insert workout categories
    INSERT INTO workout_categories (name, description, created_date, updated_date)
    VALUES
        ('Strength', 'Exercises focused on building strength and muscle mass', NOW(), NOW()),
        ('Cardio', 'Exercises focused on cardiovascular health and endurance', NOW(), NOW()),
        ('Flexibility', 'Exercises focused on improving flexibility and mobility', NOW(), NOW()),
        ('Calisthenics', 'Bodyweight exercises for strength and mobility', NOW(), NOW()),
        ('HIIT', 'High-intensity interval training workouts', NOW(), NOW());

    -- Insert workouts
    INSERT INTO workouts (name, description, category_id, difficulty_level, equipment_needed, muscle_groups, instructions, user_id, is_custom, created_date, updated_date)
    VALUES
        ('Barbell Bench Press', 'Classic chest exercise for building upper body strength',
         (SELECT id FROM workout_categories WHERE name = 'Strength'),
         'intermediate', 'Barbell, Bench', 'Chest, Triceps, Shoulders',
         'Lie on bench, grip barbell slightly wider than shoulder width, lower to chest, press up to starting position',
         user_id, 0, NOW(), NOW()),

        ('Squat', 'Fundamental lower body exercise',
         (SELECT id FROM workout_categories WHERE name = 'Strength'),
         'intermediate', 'Barbell, Squat Rack', 'Quadriceps, Hamstrings, Glutes, Lower Back',
         'Stand with feet shoulder-width apart, barbell across upper back, bend knees and hips to lower body, then return to standing',
         user_id, 0, NOW(), NOW()),

        ('Pull-up', 'Upper body pulling exercise',
         (SELECT id FROM workout_categories WHERE name = 'Calisthenics'),
         'advanced', 'Pull-up Bar', 'Back, Biceps, Shoulders',
         'Hang from bar with hands slightly wider than shoulders, pull body up until chin clears bar, lower with control',
         user_id, 0, NOW(), NOW()),

        ('Treadmill Running', 'Cardiovascular exercise on treadmill',
         (SELECT id FROM workout_categories WHERE name = 'Cardio'),
         'beginner', 'Treadmill', 'Legs, Cardiovascular System',
         'Start at comfortable pace, maintain good posture, swing arms naturally, breathe rhythmically',
         user_id, 0, NOW(), NOW());

    -- Insert workout sets for the workouts
    INSERT INTO workout_sets (workout_id, set_number, reps, weight, rest_seconds, notes, created_date, updated_date)
    VALUES
        ((SELECT id FROM workouts WHERE name = 'Barbell Bench Press'), 1, 12, 60, 60, 'Warm-up set', NOW(), NOW()),
        ((SELECT id FROM workouts WHERE name = 'Barbell Bench Press'), 2, 10, 80, 90, 'Working set', NOW(), NOW()),
        ((SELECT id FROM workouts WHERE name = 'Barbell Bench Press'), 3, 8, 90, 120, 'Working set', NOW(), NOW()),
        ((SELECT id FROM workouts WHERE name = 'Barbell Bench Press'), 4, 6, 100, 120, 'Final set', NOW(), NOW()),

        ((SELECT id FROM workouts WHERE name = 'Squat'), 1, 12, 80, 60, 'Warm-up set', NOW(), NOW()),
        ((SELECT id FROM workouts WHERE name = 'Squat'), 2, 10, 100, 90, 'Working set', NOW(), NOW()),
        ((SELECT id FROM workouts WHERE name = 'Squat'), 3, 8, 120, 120, 'Working set', NOW(), NOW()),

        ((SELECT id FROM workouts WHERE name = 'Pull-up'), 1, 8, NULL, 60, 'Bodyweight', NOW(), NOW()),
        ((SELECT id FROM workouts WHERE name = 'Pull-up'), 2, 6, NULL, 90, 'Bodyweight', NOW(), NOW()),
        ((SELECT id FROM workouts WHERE name = 'Pull-up'), 3, 4, NULL, 120, 'Bodyweight', NOW(), NOW()),

        ((SELECT id FROM workouts WHERE name = 'Treadmill Running'), 1, NULL, NULL, 0, 'Duration: 20 minutes, Speed: 10 km/h', NOW(), NOW());

    -- Insert workout programs
    INSERT INTO workout_programs (name, description, user_id, group_name, difficulty_level, duration_weeks, goal, is_public, created_date, updated_date)
    VALUES
        ('Beginner Strength Program', 'A beginner-friendly strength training program',
         user_id, 'Strength Training', 'beginner', 8, 'Build basic strength and muscle', 1, NOW(), NOW()),

        ('PPL Split', 'Push, Pull, Legs training split for intermediate lifters',
         user_id, 'Bodybuilding', 'intermediate', 12, 'Muscle hypertrophy and strength', 1, NOW(), NOW());

    -- Insert workout program days
    INSERT INTO workout_program_days (program_id, day_number, name, description, created_date, updated_date)
    VALUES
        ((SELECT id FROM workout_programs WHERE name = 'Beginner Strength Program'), 1, 'Full Body Day 1', 'First full body workout of the week', NOW(), NOW()),
        ((SELECT id FROM workout_programs WHERE name = 'Beginner Strength Program'), 3, 'Full Body Day 2', 'Second full body workout of the week', NOW(), NOW()),
        ((SELECT id FROM workout_programs WHERE name = 'Beginner Strength Program'), 5, 'Full Body Day 3', 'Third full body workout of the week', NOW(), NOW()),

        ((SELECT id FROM workout_programs WHERE name = 'PPL Split'), 1, 'Push Day', 'Chest, shoulders, and triceps', NOW(), NOW()),
        ((SELECT id FROM workout_programs WHERE name = 'PPL Split'), 2, 'Pull Day', 'Back and biceps', NOW(), NOW()),
        ((SELECT id FROM workout_programs WHERE name = 'PPL Split'), 3, 'Leg Day', 'Quadriceps, hamstrings, and calves', NOW(), NOW()),
        ((SELECT id FROM workout_programs WHERE name = 'PPL Split'), 4, 'Push Day', 'Chest, shoulders, and triceps', NOW(), NOW()),
        ((SELECT id FROM workout_programs WHERE name = 'PPL Split'), 5, 'Pull Day', 'Back and biceps', NOW(), NOW()),
        ((SELECT id FROM workout_programs WHERE name = 'PPL Split'), 6, 'Leg Day', 'Quadriceps, hamstrings, and calves', NOW(), NOW());

    -- Associate workouts with program days
    INSERT INTO workout_program_day_workout (workout_program_day_id, workout_id)
    VALUES
        ((SELECT id FROM workout_program_days WHERE name = 'Full Body Day 1' AND program_id = (SELECT id FROM workout_programs WHERE name = 'Beginner Strength Program')),
         (SELECT id FROM workouts WHERE name = 'Barbell Bench Press')),
        ((SELECT id FROM workout_program_days WHERE name = 'Full Body Day 1' AND program_id = (SELECT id FROM workout_programs WHERE name = 'Beginner Strength Program')),
         (SELECT id FROM workouts WHERE name = 'Squat')),

        ((SELECT id FROM workout_program_days WHERE name = 'Full Body Day 2' AND program_id = (SELECT id FROM workout_programs WHERE name = 'Beginner Strength Program')),
         (SELECT id FROM workouts WHERE name = 'Pull-up')),
        ((SELECT id FROM workout_program_days WHERE name = 'Full Body Day 2' AND program_id = (SELECT id FROM workout_programs WHERE name = 'Beginner Strength Program')),
         (SELECT id FROM workouts WHERE name = 'Treadmill Running')),

        ((SELECT id FROM workout_program_days WHERE name = 'Push Day' AND program_id = (SELECT id FROM workout_programs WHERE name = 'PPL Split') LIMIT 1),
         (SELECT id FROM workouts WHERE name = 'Barbell Bench Press')),

        ((SELECT id FROM workout_program_days WHERE name = 'Pull Day' AND program_id = (SELECT id FROM workout_programs WHERE name = 'PPL Split') LIMIT 1),
         (SELECT id FROM workouts WHERE name = 'Pull-up')),

        ((SELECT id FROM workout_program_days WHERE name = 'Leg Day' AND program_id = (SELECT id FROM workout_programs WHERE name = 'PPL Split') LIMIT 1),
         (SELECT id FROM workouts WHERE name = 'Squat'));

    -- =====================
    -- DIET DATA EXAMPLES
    -- =====================

    -- Insert food categories
    INSERT INTO food_categories (name, description, created_date, updated_date)
    VALUES
        ('Protein', 'High-protein food sources', NOW(), NOW()),
        ('Carbohydrates', 'Carbohydrate-rich foods', NOW(), NOW()),
        ('Fats', 'Healthy fat sources', NOW(), NOW()),
        ('Fruits', 'Fresh and dried fruits', NOW(), NOW()),
        ('Vegetables', 'Fresh and cooked vegetables', NOW(), NOW()),
        ('Dairy', 'Milk and dairy products', NOW(), NOW());

    -- Insert foods
    INSERT INTO foods (name, description, category_id, calories, protein, carbs, fat, fiber, sugar, serving_size, serving_unit, user_id, is_custom, created_date, updated_date)
    VALUES
        ('Chicken Breast', 'Lean protein source',
         (SELECT id FROM food_categories WHERE name = 'Protein'),
         165, 31, 0, 3.6, 0, 0, 100, 'g', user_id, 0, NOW(), NOW()),

        ('Brown Rice', 'Whole grain carbohydrate source',
         (SELECT id FROM food_categories WHERE name = 'Carbohydrates'),
         112, 2.6, 23, 0.9, 1.8, 0.4, 100, 'g', user_id, 0, NOW(), NOW()),

        ('Avocado', 'Healthy fat source',
         (SELECT id FROM food_categories WHERE name = 'Fats'),
         160, 2, 8.5, 14.7, 6.7, 0.7, 100, 'g', user_id, 0, NOW(), NOW()),

        ('Broccoli', 'Nutrient-dense vegetable',
         (SELECT id FROM food_categories WHERE name = 'Vegetables'),
         34, 2.8, 6.6, 0.4, 2.6, 1.7, 100, 'g', user_id, 0, NOW(), NOW()),

        ('Greek Yogurt', 'High-protein dairy product',
         (SELECT id FROM food_categories WHERE name = 'Dairy'),
         59, 10, 3.6, 0.4, 0, 3.6, 100, 'g', user_id, 0, NOW(), NOW()),

        ('Banana', 'Energy-rich fruit',
         (SELECT id FROM food_categories WHERE name = 'Fruits'),
         89, 1.1, 22.8, 0.3, 2.6, 12.2, 100, 'g', user_id, 0, NOW(), NOW());

    -- Insert supplement categories
    INSERT INTO supplement_categories (name, description, created_date, updated_date)
    VALUES
        ('Protein', 'Protein supplements', NOW(), NOW()),
        ('Vitamins', 'Vitamin supplements', NOW(), NOW()),
        ('Minerals', 'Mineral supplements', NOW(), NOW()),
        ('Pre-workout', 'Pre-workout supplements', NOW(), NOW()),
        ('Recovery', 'Recovery and post-workout supplements', NOW(), NOW());

    -- Insert supplements
    INSERT INTO supplements (name, description, category_id, brand, recommended_dosage, dosage_unit, benefits, side_effects, user_id, is_custom, created_date, updated_date)
    VALUES
        ('Whey Protein', 'Fast-absorbing protein supplement',
         (SELECT id FROM supplement_categories WHERE name = 'Protein'),
         'OptimumNutrition', 25, 'g', 'Muscle recovery and growth', 'May cause digestive discomfort in some individuals',
         user_id, 0, NOW(), NOW()),

        ('Multivitamin', 'Comprehensive vitamin and mineral supplement',
         (SELECT id FROM supplement_categories WHERE name = 'Vitamins'),
         'NowFoods', 1, 'tablet', 'Fills nutritional gaps, supports overall health', 'May cause nausea if taken on empty stomach',
         user_id, 0, NOW(), NOW()),

        ('Creatine Monohydrate', 'Strength and performance supplement',
         (SELECT id FROM supplement_categories WHERE name = 'Recovery'),
         'Optimum Nutrition', 5, 'g', 'Increases strength, power, and muscle mass', 'May cause water retention',
         user_id, 0, NOW(), NOW()),

        ('Pre-Workout Complex', 'Energy and focus supplement',
         (SELECT id FROM supplement_categories WHERE name = 'Pre-workout'),
         'C4', 1, 'scoop', 'Increases energy, focus, and performance', 'May cause jitters, increased heart rate',
         user_id, 0, NOW(), NOW());

    -- Insert diet plans
    INSERT INTO diet_plans (name, description, user_id, goal, duration_days, daily_calories, protein_target, carbs_target, fat_target, is_public, created_date, updated_date)
    VALUES
        ('Muscle Building Plan', 'High-protein diet for muscle growth',
         user_id, 'muscle gain', 30, 3000, 200, 300, 100, 1, NOW(), NOW()),

        ('Fat Loss Plan', 'Calorie-controlled diet for fat loss',
         user_id, 'weight loss', 30, 2000, 180, 150, 70, 1, NOW(), NOW()),

        ('Maintenance Plan', 'Balanced diet for weight maintenance',
         user_id, 'maintenance', 30, 2500, 180, 250, 80, 1, NOW(), NOW());

    -- Associate foods with diet plans (with meal types and portions)
    INSERT INTO diet_plan_food (diet_plan_id, food_id, meal_type, portion_size, portion_unit, day_number)
    VALUES
        ((SELECT id FROM diet_plans WHERE name = 'Muscle Building Plan'),
         (SELECT id FROM foods WHERE name = 'Chicken Breast'),
         'lunch', 200, 'g', 1),
        ((SELECT id FROM diet_plans WHERE name = 'Muscle Building Plan'),
         (SELECT id FROM foods WHERE name = 'Brown Rice'),
         'lunch', 150, 'g', 1),
        ((SELECT id FROM diet_plans WHERE name = 'Muscle Building Plan'),
         (SELECT id FROM foods WHERE name = 'Broccoli'),
         'lunch', 100, 'g', 1),
        ((SELECT id FROM diet_plans WHERE name = 'Muscle Building Plan'),
         (SELECT id FROM foods WHERE name = 'Greek Yogurt'),
         'breakfast', 200, 'g', 1),
        ((SELECT id FROM diet_plans WHERE name = 'Muscle Building Plan'),
         (SELECT id FROM foods WHERE name = 'Banana'),
         'breakfast', 1, 'piece', 1),

        ((SELECT id FROM diet_plans WHERE name = 'Fat Loss Plan'),
         (SELECT id FROM foods WHERE name = 'Chicken Breast'),
         'lunch', 150, 'g', 1),
        ((SELECT id FROM diet_plans WHERE name = 'Fat Loss Plan'),
         (SELECT id FROM foods WHERE name = 'Broccoli'),
         'lunch', 150, 'g', 1),
        ((SELECT id FROM diet_plans WHERE name = 'Fat Loss Plan'),
         (SELECT id FROM foods WHERE name = 'Greek Yogurt'),
         'breakfast', 150, 'g', 1);

    -- Associate supplements with diet plans
    INSERT INTO diet_plan_supplement (diet_plan_id, supplement_id, dosage, dosage_unit, time_of_day, day_number)
    VALUES
        ((SELECT id FROM diet_plans WHERE name = 'Muscle Building Plan'),
         (SELECT id FROM supplements WHERE name = 'Whey Protein'),
         25, 'g', 'post-workout', 1),
        ((SELECT id FROM diet_plans WHERE name = 'Muscle Building Plan'),
         (SELECT id FROM supplements WHERE name = 'Creatine Monohydrate'),
         5, 'g', 'morning', 1),

        ((SELECT id FROM diet_plans WHERE name = 'Fat Loss Plan'),
         (SELECT id FROM supplements WHERE name = 'Whey Protein'),
         25, 'g', 'post-workout', 1),

        ((SELECT id FROM diet_plans WHERE name = 'Maintenance Plan'),
         (SELECT id FROM supplements WHERE name = 'Multivitamin'),
         1, 'tablet', 'morning', 1);

    -- Insert meal templates
    INSERT INTO meal_templates (name, description, user_id, meal_type, is_favorite, created_date, updated_date)
    VALUES
        ('High Protein Breakfast', 'Protein-rich breakfast option',
         user_id, 'breakfast', true, NOW(), NOW()),

        ('Post-Workout Lunch', 'Balanced post-workout meal',
         user_id, 'lunch', true, NOW(), NOW()),

        ('Light Dinner', 'Light evening meal',
         user_id, 'dinner', false, NOW(), NOW());

    -- Associate foods with meal templates
    INSERT INTO meal_template_foods (meal_template_id, food_id, portion_size, portion_unit, created_date, updated_date)
    VALUES
        ((SELECT id FROM meal_templates WHERE name = 'High Protein Breakfast'),
         (SELECT id FROM foods WHERE name = 'Greek Yogurt'),
         200, 'g', NOW(), NOW()),
        ((SELECT id FROM meal_templates WHERE name = 'High Protein Breakfast'),
         (SELECT id FROM foods WHERE name = 'Banana'),
         1, 'piece', NOW(), NOW()),

        ((SELECT id FROM meal_templates WHERE name = 'Post-Workout Lunch'),
         (SELECT id FROM foods WHERE name = 'Chicken Breast'),
         150, 'g', NOW(), NOW()),
        ((SELECT id FROM meal_templates WHERE name = 'Post-Workout Lunch'),
         (SELECT id FROM foods WHERE name = 'Brown Rice'),
         100, 'g', NOW(), NOW()),
        ((SELECT id FROM meal_templates WHERE name = 'Post-Workout Lunch'),
         (SELECT id FROM foods WHERE name = 'Broccoli'),
         100, 'g', NOW(), NOW()),

        ((SELECT id FROM meal_templates WHERE name = 'Light Dinner'),
         (SELECT id FROM foods WHERE name = 'Chicken Breast'),
         100, 'g', NOW(), NOW()),
        ((SELECT id FROM meal_templates WHERE name = 'Light Dinner'),
         (SELECT id FROM foods WHERE name = 'Avocado'),
         50, 'g', NOW(), NOW()),
        ((SELECT id FROM meal_templates WHERE name = 'Light Dinner'),
         (SELECT id FROM foods WHERE name = 'Broccoli'),
         150, 'g', NOW(), NOW());
END
$$;
