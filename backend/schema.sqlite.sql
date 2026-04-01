-- SQLite 数据库架构
-- 用于 MySQL to SQLite 迁移

-- 账号表
CREATE TABLE IF NOT EXISTS accounts (
    "account_id" TEXT PRIMARY KEY,
    "username" TEXT NOT NULL UNIQUE,
    "password_hash" TEXT NOT NULL,
    "real_name" TEXT,
    "email" TEXT UNIQUE,
    "phone" TEXT,
    "role" TEXT NOT NULL,
    "status" INTEGER NOT NULL DEFAULT 1,
    "login_attempts" INTEGER DEFAULT 0,
    "locked_until" TEXT,
    "last_login" TEXT,
    "created_at" TEXT NOT NULL,
    "updated_at" TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_accounts_username ON accounts ("username");
CREATE INDEX IF NOT EXISTS ix_accounts_role ON accounts ("role");
CREATE INDEX IF NOT EXISTS ix_accounts_status ON accounts ("status");

-- Refresh Token表
CREATE TABLE IF NOT EXISTS refresh_tokens (
    "token_id" TEXT PRIMARY KEY,
    "account_id" TEXT NOT NULL,
    "token_hash" TEXT NOT NULL,
    "expires_at" TEXT NOT NULL,
    FOREIGN KEY ("account_id") REFERENCES accounts ("account_id") ON DELETE CASCADE
);

-- 大学表
CREATE TABLE IF NOT EXISTS universities (
    "university_id" TEXT PRIMARY KEY,
    "university_name" TEXT NOT NULL,
    "province" TEXT,
    "city" TEXT,
    "description" TEXT,
    "created_at" TEXT NOT NULL,
    "updated_at" TEXT NOT NULL
);

-- 学生档案表
CREATE TABLE IF NOT EXISTS student_profiles (
    "profile_id" TEXT PRIMARY KEY,
    "account_id" TEXT NOT NULL UNIQUE,
    "student_name" TEXT,
    "gender" TEXT,
    "birth_date" TEXT,
    "phone" TEXT,
    "email" TEXT,
    "province" TEXT,
    "city" TEXT,
    "university_id" TEXT,
    "college" TEXT,
    "major" TEXT,
    "degree" TEXT,
    "graduation_year" INTEGER,
    "employment_status" TEXT,
    "annual_salary" INTEGER,
    "company_name" TEXT,
    "job_title" TEXT,
    "industry" TEXT,
    "created_at" TEXT NOT NULL,
    "updated_at" TEXT NOT NULL,
    FOREIGN KEY ("account_id") REFERENCES accounts ("account_id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS ix_student_profiles_account_id ON student_profiles ("account_id");
CREATE INDEX IF NOT EXISTS ix_student_profiles_university_id ON student_profiles ("university_id");

-- 企业表
CREATE TABLE IF NOT EXISTS companies (
    "company_id" TEXT PRIMARY KEY,
    "account_id" TEXT NOT NULL UNIQUE,
    "company_name" TEXT NOT NULL,
    "industry" TEXT,
    "city" TEXT,
    "size" TEXT,
    "description" TEXT,
    "verified" INTEGER NOT NULL DEFAULT 0,
    "created_at" TEXT NOT NULL,
    "updated_at" TEXT NOT NULL,
    FOREIGN KEY ("account_id") REFERENCES accounts ("account_id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS ix_companies_verified ON companies ("verified");

-- 岗位描述表
CREATE TABLE IF NOT EXISTS job_descriptions (
    "job_id" TEXT PRIMARY KEY,
    "company_id" TEXT NOT NULL,
    "job_title" TEXT NOT NULL,
    "job_type" TEXT,
    "salary_min" INTEGER,
    "salary_max" INTEGER,
    "location" TEXT,
    "description" TEXT,
    "requirements" TEXT,
    "benefits" TEXT,
    "contact_email" TEXT,
    "contact_phone" TEXT,
    "status" INTEGER NOT NULL DEFAULT 1,
    "created_at" TEXT NOT NULL,
    "updated_at" TEXT NOT NULL,
    FOREIGN KEY ("company_id") REFERENCES companies ("company_id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS ix_job_descriptions_company_id ON job_descriptions ("company_id");
CREATE INDEX IF NOT EXISTS ix_job_descriptions_status ON job_descriptions ("status");

-- 岗位申请表
CREATE TABLE IF NOT EXISTS job_applications (
    "application_id" TEXT PRIMARY KEY,
    "job_id" TEXT NOT NULL,
    "student_id" TEXT NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'pending',
    "apply_date" TEXT,
    "created_at" TEXT NOT NULL,
    "updated_at" TEXT NOT NULL,
    FOREIGN KEY ("job_id") REFERENCES job_descriptions ("job_id") ON DELETE CASCADE,
    FOREIGN KEY ("student_id") REFERENCES student_profiles ("profile_id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS ix_job_applications_job_id ON job_applications ("job_id");
CREATE INDEX IF NOT EXISTS ix_job_applications_student_id ON job_applications ("student_id");

-- 学院就业表
CREATE TABLE IF NOT EXISTS college_employment (
    "id" TEXT PRIMARY KEY,
    "university_id" TEXT NOT NULL,
    "college" TEXT NOT NULL,
    "major" TEXT,
    "year" INTEGER,
    "total_students" INTEGER,
    "employed_students" INTEGER,
    "employment_rate" REAL,
    "avg_salary" INTEGER,
    "created_at" TEXT NOT NULL,
    "updated_at" TEXT NOT NULL,
    FOREIGN KEY ("university_id") REFERENCES universities ("university_id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS ix_college_employment_university_id ON college_employment ("university_id");

-- 稀缺人才表
CREATE TABLE IF NOT EXISTS scarce_talents (
    "id" TEXT PRIMARY KEY,
    "province" TEXT,
    "job_type" TEXT NOT NULL,
    "industry" TEXT,
    "demand_count" INTEGER,
    "avg_salary" INTEGER,
    "year" INTEGER,
    "created_at" TEXT NOT NULL,
    "updated_at" TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_scarce_talents_province ON scarce_talents ("province");

-- 就业预警表
CREATE TABLE IF NOT EXISTS employment_warnings (
    "warning_id" TEXT PRIMARY KEY,
    "university_id" TEXT NOT NULL,
    "student_name" TEXT NOT NULL,
    "warning_type" TEXT NOT NULL,
    "description" TEXT,
    "status" TEXT NOT NULL DEFAULT 'pending',
    "created_at" TEXT NOT NULL,
    "updated_at" TEXT NOT NULL,
    FOREIGN KEY ("university_id") REFERENCES universities ("university_id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS ix_employment_warnings_university_id ON employment_warnings ("university_id");

-- AI分析记录表
CREATE TABLE IF NOT EXISTS ai_analysis_records (
    "record_id" TEXT PRIMARY KEY,
    "account_id" TEXT NOT NULL,
    "analysis_type" TEXT NOT NULL,
    "input_data" TEXT,
    "result_data" TEXT,
    "created_at" TEXT NOT NULL,
    FOREIGN KEY ("account_id") REFERENCES accounts ("account_id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS ix_ai_analysis_records_account_id ON ai_analysis_records ("account_id");

-- 知识文档表
CREATE TABLE IF NOT EXISTS knowledge_documents (
    "doc_id" TEXT PRIMARY KEY,
    "title" TEXT NOT NULL,
    "content" TEXT,
    "doc_type" TEXT,
    "category" TEXT DEFAULT 'shared',
    "vector_ids" TEXT,
    "created_at" TEXT NOT NULL,
    "updated_at" TEXT NOT NULL
);

-- 为已有数据库添加缺失列（SQLite 不支持 ADD COLUMN IF NOT EXISTS，需手动执行）
-- ALTER TABLE knowledge_documents ADD COLUMN "category" TEXT DEFAULT 'shared';
-- ALTER TABLE knowledge_documents ADD COLUMN "vector_ids" TEXT;

-- 系统配置表
CREATE TABLE IF NOT EXISTS system_configs (
    "config_id" TEXT PRIMARY KEY,
    "config_key" TEXT NOT NULL UNIQUE,
    "config_value" TEXT,
    "description" TEXT,
    "created_at" TEXT NOT NULL,
    "updated_at" TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_system_configs_config_key ON system_configs ("config_key");

-- 操作日志表
CREATE TABLE IF NOT EXISTS operation_logs (
    "log_id" TEXT PRIMARY KEY,
    "account_id" TEXT NOT NULL,
    "action" TEXT NOT NULL,
    "resource" TEXT,
    "details" TEXT,
    "ip_address" TEXT,
    "created_at" TEXT NOT NULL,
    FOREIGN KEY ("account_id") REFERENCES accounts ("account_id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS ix_operation_logs_account_id ON operation_logs ("account_id");
