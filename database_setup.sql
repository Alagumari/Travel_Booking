-- ============================================================
-- TravelX Pro - MySQL Database Setup Script
-- Run this in MySQL before starting the Django project
-- ============================================================

-- 1. Create database
CREATE DATABASE IF NOT EXISTS travelx_pro_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- 2. Create dedicated user (change password!)
CREATE USER IF NOT EXISTS 'travelx_user'@'localhost'
  IDENTIFIED BY 'TravelX@2025!';

-- 3. Grant privileges
GRANT ALL PRIVILEGES ON travelx_pro_db.* TO 'travelx_user'@'localhost';
FLUSH PRIVILEGES;

-- 4. Verify
SHOW DATABASES LIKE 'travelx_pro_db';
SELECT User, Host FROM mysql.user WHERE User = 'travelx_user';

-- ============================================================
-- After running this script, update settings.py:
--   NAME: 'travelx_pro_db'
--   USER: 'travelx_user'
--   PASSWORD: 'TravelX@2025!'
-- Then run: python manage.py migrate
-- ============================================================
