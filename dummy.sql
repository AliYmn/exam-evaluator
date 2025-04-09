-- Dummy data for all services with a single user (aliymn.db@gmail.com)

-- ==================== AUTH SERVICE ====================

-- Users Table (Only one user)
INSERT INTO users (created_date, updated_date, email, password_hash, is_active, is_verified, role, first_name, last_name, date_of_birth, profile_picture, gender, height, weight, bmi, body_tracker_period, language, referral_code, country, city, address, phone_number, timezone, preferences, last_login, reset_token, reset_token_expiry, package_type, subscription_start, subscription_end, billing_period, auto_renew, usage_limit, storage_limit)
VALUES (NOW(), NOW(), 'aliymn.db@gmail.com', '$2b$12$1234567890123456789012uGZGJfxgV7DFgQp3UqytuJrfvmX3Ovu', true, true, 'admin', 'Ali', 'Yaman', '1990-01-01', 'https://randomuser.me/api/portraits/men/1.jpg', 'male', 180, 80, 25, 'weekly', 'en', 'ALI123456', 'Turkey', 'Istanbul', '123 Sample St', '+901234567890', 'Europe/Istanbul', '{"notifications": true, "theme": "dark"}', NOW(), NULL, NULL, 'premium', '2025-01-01', '2026-01-01', 'yearly', true, 1000, 100);

-- ==================== CONTENT SERVICE ====================

-- Blog Categories
INSERT INTO blog_categories (created_date, updated_date, name, description) VALUES
(NOW(), NOW(), 'Nutrition', 'Articles about healthy eating and nutrition'),
(NOW(), NOW(), 'Fitness', 'Workout routines and fitness tips'),
(NOW(), NOW(), 'Wellness', 'Mental health and overall wellness'),
(NOW(), NOW(), 'Fasting', 'Intermittent fasting guides and tips'),
(NOW(), NOW(), 'Recipes', 'Healthy recipes for your diet');

-- Blog Tags
INSERT INTO blog_tags (created_date, updated_date, name) VALUES
(NOW(), NOW(), 'beginner'),
(NOW(), NOW(), 'advanced'),
(NOW(), NOW(), 'keto'),
(NOW(), NOW(), 'vegan'),
(NOW(), NOW(), 'weight-loss'),
(NOW(), NOW(), 'muscle-gain'),
(NOW(), NOW(), 'mental-health'),
(NOW(), NOW(), '16-8-fasting'),
(NOW(), NOW(), 'quick-recipes'),
(NOW(), NOW(), 'meal-prep');

-- Get user_id for the aliymn.db@gmail.com user
DO $$
DECLARE
    user_id_var INTEGER;
BEGIN
    SELECT id INTO user_id_var FROM users WHERE email = 'aliymn.db@gmail.com';

    -- ==================== FIT SERVICE ====================

    -- Fasting Plans
    INSERT INTO fasting_plans (created_date, updated_date, user_id, fasting_type, is_active, target_week, target_calories, target_meals, target_water, target_protein, target_carb, target_fat) VALUES
    (NOW(), NOW(), user_id_var, '16:8', true, 12, 2000, 2, 3.0, 150, 200, 70),
    (NOW(), NOW(), user_id_var, '18:6', false, 8, 1800, 2, 3.5, 160, 180, 65),
    (NOW(), NOW(), user_id_var, '20:4', false, 4, 1600, 1, 4.0, 170, 150, 60);

    -- Get the ID of the active fasting plan
    DECLARE
        plan_id_var INTEGER;
    BEGIN
        SELECT id INTO plan_id_var FROM fasting_plans WHERE user_id = user_id_var AND is_active = true LIMIT 1;

        -- Fasting Sessions
        INSERT INTO fasting_sessions (created_date, updated_date, user_id, plan_id, start_time, end_time, status, mood, stage) VALUES
        ('2025-04-01 08:00:00', '2025-04-01 16:00:00', user_id_var, plan_id_var, '08:00:00', '16:00:00', 'completed', 'happy', 'ketosis'),
        ('2025-04-02 08:00:00', '2025-04-02 16:00:00', user_id_var, plan_id_var, '08:00:00', '16:00:00', 'completed', 'energetic', 'ketosis'),
        ('2025-04-03 08:00:00', '2025-04-03 16:00:00', user_id_var, plan_id_var, '08:00:00', '16:00:00', 'completed', 'focused', 'ketosis'),
        ('2025-04-04 08:00:00', '2025-04-04 16:00:00', user_id_var, plan_id_var, '08:00:00', '16:00:00', 'completed', 'tired', 'catabolic'),
        ('2025-04-05 08:00:00', '2025-04-05 16:00:00', user_id_var, plan_id_var, '08:00:00', '16:00:00', 'completed', 'happy', 'ketosis'),
        ('2025-04-06 08:00:00', '2025-04-06 16:00:00', user_id_var, plan_id_var, '08:00:00', '16:00:00', 'completed', 'energetic', 'ketosis'),
        ('2025-04-07 08:00:00', '2025-04-07 16:00:00', user_id_var, plan_id_var, '08:00:00', '16:00:00', 'completed', 'focused', 'ketosis'),
        ('2025-04-08 08:00:00', '2025-04-08 16:00:00', user_id_var, plan_id_var, '08:00:00', '16:00:00', 'completed', 'tired', 'catabolic'),
        ('2025-04-09 08:00:00', NULL, user_id_var, plan_id_var, '08:00:00', NULL, 'active', 'focused', 'anabolic'),
        ('2025-04-10 08:00:00', NULL, user_id_var, plan_id_var, '08:00:00', NULL, 'scheduled', NULL, NULL);

        -- Get session IDs for meal and workout logs
        DECLARE
            session_ids INTEGER[];
            i INTEGER;
        BEGIN
            SELECT array_agg(id ORDER BY created_date) INTO session_ids FROM fasting_sessions WHERE user_id = user_id_var LIMIT 5;

            -- Fasting Meal Logs
            INSERT INTO fasting_meal_logs (created_date, updated_date, user_id, session_id, photo_url, notes, calories, protein, carbs, fat, detailed_macros, ai_content) VALUES
            ('2025-04-01 16:30:00', '2025-04-01 16:30:00', user_id_var, session_ids[1], 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c', 'Healthy salad with grilled chicken', 450, 35, 20, 25, '{"fiber": 8, "sugar": 5, "sodium": 300}', 'This meal provides an excellent balance of protein and healthy fats. The high fiber content will help you feel full longer.'),
            ('2025-04-01 19:30:00', '2025-04-01 19:30:00', user_id_var, session_ids[1], 'https://images.unsplash.com/photo-1432139555190-58524dae6a55', 'Grilled salmon with vegetables', 550, 40, 15, 30, '{"fiber": 6, "sugar": 3, "sodium": 250}', 'Salmon is rich in omega-3 fatty acids which support heart health and reduce inflammation.'),
            ('2025-04-02 16:30:00', '2025-04-02 16:30:00', user_id_var, session_ids[2], 'https://images.unsplash.com/photo-1490645935967-10de6ba17061', 'Quinoa bowl with avocado and eggs', 480, 25, 40, 20, '{"fiber": 12, "sugar": 2, "sodium": 200}', 'This nutrient-dense meal provides sustained energy with complex carbohydrates from quinoa and healthy fats from avocado.'),
            ('2025-04-02 19:30:00', '2025-04-02 19:30:00', user_id_var, session_ids[2], 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd', 'Vegetable stir-fry with tofu', 400, 20, 35, 15, '{"fiber": 10, "sugar": 8, "sodium": 350}', 'This plant-based meal is high in antioxidants and provides complete protein from tofu.'),
            ('2025-04-03 16:30:00', '2025-04-03 16:30:00', user_id_var, session_ids[3], 'https://images.unsplash.com/photo-1504674900247-0877df9cc836', 'Grilled steak with sweet potato', 600, 45, 30, 25, '{"fiber": 5, "sugar": 10, "sodium": 400}', 'This meal provides high-quality protein and complex carbohydrates to support muscle recovery after exercise.');

            -- Fasting Workout Logs
            INSERT INTO fasting_workout_logs (created_date, updated_date, user_id, session_id, workout_name, duration_minutes, calories_burned, intensity, notes) VALUES
            ('2025-04-01 12:00:00', '2025-04-01 12:00:00', user_id_var, session_ids[1], 'Morning Yoga', 30, 150, 'Low', 'Felt great during fasting, increased flexibility'),
            ('2025-04-02 11:30:00', '2025-04-02 11:30:00', user_id_var, session_ids[2], 'Bodyweight Circuit', 45, 300, 'Medium', 'Did push-ups, squats, lunges, and planks'),
            ('2025-04-03 13:00:00', '2025-04-03 13:00:00', user_id_var, session_ids[3], 'Light Cardio', 40, 250, 'Low', 'Brisk walking outdoors, felt energized'),
            ('2025-04-04 12:30:00', '2025-04-04 12:30:00', user_id_var, session_ids[4], 'Strength Training', 60, 400, 'High', 'Upper body focus, felt a bit weak during fasting'),
            ('2025-04-05 11:00:00', '2025-04-05 11:00:00', user_id_var, session_ids[5], 'HIIT Workout', 25, 300, 'High', 'Short but intense session, felt good');
        END;
    END;

    -- ==================== TRACKER SERVICE ====================

    -- Daily Trackers
    INSERT INTO daily_trackers (created_date, updated_date, user_id, energy, sleep, stress, muscle_soreness, fatigue, hunger, water_intake_liters, sleep_hours, mood, bowel_movement, training_quality, diet_compliance, training_compliance, note, ai_content) VALUES
    ('2025-04-01', '2025-04-01', user_id_var, 8, 7, 3, 2, 3, 4, 3.5, 7.5, 'happy', 'normal', 8, 9, 8, 'Felt great today, high energy throughout the day', 'Your energy levels are excellent today. The combination of good sleep and low stress is contributing to your overall well-being. Keep up the good hydration habits!'),
    ('2025-04-02', '2025-04-02', user_id_var, 7, 8, 4, 3, 4, 3, 3.0, 8.0, 'content', 'normal', 7, 8, 7, 'Slightly sore from yesterday''s workout', 'Your sleep quality has improved, which is helping manage your muscle soreness. Consider adding some light stretching to help with recovery.'),
    ('2025-04-03', '2025-04-03', user_id_var, 9, 8, 2, 4, 2, 3, 4.0, 7.5, 'energetic', 'good', 9, 9, 9, 'Very productive day, workout felt amazing', 'Excellent energy levels today! Your consistent hydration is paying off, and your stress levels are decreasing. The high training quality indicates good recovery.'),
    ('2025-04-04', '2025-04-04', user_id_var, 6, 6, 5, 5, 5, 5, 2.5, 6.0, 'tired', 'constipated', 6, 7, 6, 'Didn''t sleep well, felt tired during workout', 'Your sleep quality has decreased, which is affecting your energy and recovery. Try to improve your sleep hygiene and increase water intake to help with digestion.'),
    ('2025-04-05', '2025-04-05', user_id_var, 8, 7, 3, 3, 3, 4, 3.5, 7.0, 'happy', 'normal', 8, 8, 8, 'Weekend rest day, focused on recovery', 'Your recovery is on track. The balanced approach to rest is helping manage muscle soreness while maintaining good energy levels.');

    -- Body Trackers
    INSERT INTO body_trackers (created_date, updated_date, user_id, weight, neck, waist, shoulder, chest, hip, thigh, arm, note, ai_content) VALUES
    ('2025-04-01', '2025-04-01', user_id_var, 80.0, 38.0, 85.0, 120.0, 100.0, 95.0, 60.0, 35.0, 'Initial measurements', 'These baseline measurements will help track your progress over time. Your current proportions indicate a balanced physique.'),
    ('2025-04-08', '2025-04-08', user_id_var, 79.5, 37.8, 84.5, 120.0, 99.5, 94.5, 59.8, 35.2, 'Small improvements after one week', 'You''re showing positive changes in your measurements. The slight reduction in waist circumference suggests fat loss while the maintenance of arm measurements indicates muscle preservation.'),
    ('2025-04-15', '2025-04-15', user_id_var, 79.0, 37.5, 84.0, 120.5, 99.0, 94.0, 59.5, 35.5, 'Continuing to see progress', 'Consistent progress in your measurements indicates your nutrition and training program is effective. The increase in arm and shoulder measurements suggests muscle growth.'),
    ('2025-04-22', '2025-04-22', user_id_var, 78.5, 37.5, 83.5, 121.0, 98.5, 93.5, 59.0, 35.8, 'Steady progress, feeling stronger', 'Your body composition is improving with decreases in waist and hip measurements while shoulders and arms are increasing. This suggests fat loss combined with muscle gain.'),
    ('2025-04-29', '2025-04-29', user_id_var, 78.0, 37.2, 83.0, 121.5, 98.0, 93.0, 58.5, 36.0, 'One month progress, very happy', 'Excellent progress over the first month! You''ve lost 2kg while improving your body composition. The reduction in waist measurement is particularly significant for metabolic health.');
END;
$$;
