-- 修复 job_applications 表的唯一约束，防止同一学生重复投递同一岗位
-- 1. 删除错误的索引 (student_id 列不存在)
-- 2. 添加正确的唯一约束 (job_id + account_id)

-- 删除错误的索引
DROP INDEX IF EXISTS ix_job_applications_account_job;

-- 添加唯一约束（防止同一学生重复投递同一岗位）
-- 首先检查是否已有重复数据
CREATE UNIQUE INDEX IF NOT EXISTS ix_job_applications_unique ON job_applications (job_id, account_id);
