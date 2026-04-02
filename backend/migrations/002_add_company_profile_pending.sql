-- Migration: Add company profile pending review system
-- Features: address, email, contact fields + pending update workflow

-- 1. 为 companies 表添加新字段
ALTER TABLE companies ADD COLUMN address TEXT;
ALTER TABLE companies ADD COLUMN email TEXT;
ALTER TABLE companies ADD COLUMN contact TEXT;
ALTER TABLE companies ADD COLUMN contact_phone TEXT;

-- 2. 企业信息待审核表
CREATE TABLE IF NOT EXISTS company_profile_pending (
    pending_id TEXT PRIMARY KEY,
    company_id TEXT NOT NULL,
    address TEXT,
    email TEXT,
    contact TEXT,
    contact_phone TEXT,
    status TEXT NOT NULL DEFAULT 'pending',  -- pending/approved/rejected
    reject_reason TEXT,
    submitted_at TEXT NOT NULL,
    reviewed_at TEXT,
    reviewed_by TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY ("company_id") REFERENCES companies ("company_id") ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_company_profile_pending_company ON company_profile_pending ("company_id");
CREATE INDEX IF NOT EXISTS ix_company_profile_pending_status ON company_profile_pending ("status");