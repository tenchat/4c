-- Migration: Add new tables for data import
-- Based on: docs/data-analysis-report.md Section 5

-- 1. 城市码映射表
CREATE TABLE IF NOT EXISTS city_mapping (
    city_id INTEGER PRIMARY KEY AUTOINCREMENT,
    city_code TEXT NOT NULL UNIQUE,
    city_name TEXT NOT NULL,
    province TEXT
);
CREATE INDEX IF NOT EXISTS ix_city_mapping_code ON city_mapping ("city_code");
CREATE INDEX IF NOT EXISTS ix_city_mapping_province ON city_mapping ("province");

-- 2. 用户求职意向表
CREATE TABLE IF NOT EXISTS user_job_preference (
    preference_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    desire_city_ids TEXT,
    desire_industry_ids TEXT,
    desire_salary_min INTEGER,
    desire_salary_max INTEGER,
    created_at TEXT NOT NULL,
    FOREIGN KEY ("user_id") REFERENCES student_profiles ("profile_id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS ix_user_job_preference_user ON user_job_preference ("user_id");

-- 3. 用户技能表
CREATE TABLE IF NOT EXISTS user_skills (
    skill_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    skill_name TEXT NOT NULL,
    source TEXT,
    FOREIGN KEY ("user_id") REFERENCES student_profiles ("profile_id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS ix_user_skills_user ON user_skills ("user_id");
CREATE INDEX IF NOT EXISTS ix_user_skills_name ON user_skills ("skill_name");

-- 4. 用户-职位曝光记录表
CREATE TABLE IF NOT EXISTS user_job_exposure (
    exposure_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    job_id TEXT NOT NULL,
    exposure_type TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY ("user_id") REFERENCES student_profiles ("profile_id") ON DELETE CASCADE,
    FOREIGN KEY ("job_id") REFERENCES job_descriptions ("job_id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS ix_user_job_exposure_user ON user_job_exposure ("user_id");
CREATE INDEX IF NOT EXISTS ix_user_job_exposure_job ON user_job_exposure ("job_id");

-- 5. 用户投递满意度表
CREATE TABLE IF NOT EXISTS user_job_satisfaction (
    satisfaction_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    job_id TEXT NOT NULL,
    satisfied INTEGER,
    FOREIGN KEY ("user_id") REFERENCES student_profiles ("profile_id") ON DELETE CASCADE,
    FOREIGN KEY ("job_id") REFERENCES job_descriptions ("job_id") ON DELETE CASCADE,
    UNIQUE("user_id", "job_id")
);
CREATE INDEX IF NOT EXISTS ix_user_job_satisfaction_user ON user_job_satisfaction ("user_id");
CREATE INDEX IF NOT EXISTS ix_user_job_satisfaction_job ON user_job_satisfaction ("job_id");

-- 6. 为 student_profiles 添加新字段
-- SQLite 不支持 DROP COLUMN，但可以添加新列
ALTER TABLE student_profiles ADD COLUMN live_city_id TEXT;
ALTER TABLE student_profiles ADD COLUMN desire_jd_salary_id TEXT;

-- 7. 为 job_descriptions 添加新字段
ALTER TABLE job_descriptions ADD COLUMN jd_sub_type TEXT;
ALTER TABLE job_descriptions ADD COLUMN require_nums INTEGER;
ALTER TABLE job_descriptions ADD COLUMN is_travel INTEGER;
ALTER TABLE job_descriptions ADD COLUMN max_edu_level TEXT;
ALTER TABLE job_descriptions ADD COLUMN resume_language_required TEXT;

-- 8. 添加建议的索引
CREATE INDEX IF NOT EXISTS ix_student_profiles_college ON student_profiles ("college");
CREATE INDEX IF NOT EXISTS ix_student_profiles_major ON student_profiles ("major");
CREATE INDEX IF NOT EXISTS ix_student_profiles_graduation_year ON student_profiles ("graduation_year");
CREATE INDEX IF NOT EXISTS ix_student_profiles_employment_status ON student_profiles ("employment_status");
CREATE INDEX IF NOT EXISTS ix_student_profiles_college_year ON student_profiles ("college", "graduation_year");

CREATE INDEX IF NOT EXISTS ix_job_descriptions_industry ON job_descriptions ("industry");
CREATE INDEX IF NOT EXISTS ix_job_descriptions_location ON job_descriptions ("location");
CREATE INDEX IF NOT EXISTS ix_job_descriptions_industry_location ON job_descriptions ("industry", "location");

CREATE INDEX IF NOT EXISTS ix_job_applications_account_job ON job_applications ("student_id", "job_id");
