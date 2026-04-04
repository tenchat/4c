-- Migration: Add resume_text field to student_profiles
-- Store extracted text content from resume uploads

ALTER TABLE student_profiles ADD COLUMN resume_text TEXT;