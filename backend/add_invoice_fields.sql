-- Run this once only if your existing database already has the `bills` table.
USE hotel_bar_db;

ALTER TABLE bills
  ADD COLUMN IF NOT EXISTS hotel_phone VARCHAR(20) NULL AFTER hotel_name,
  ADD COLUMN IF NOT EXISTS hotel_address VARCHAR(255) NULL AFTER hotel_phone,
  ADD COLUMN IF NOT EXISTS hotel_gstin VARCHAR(30) NULL AFTER hotel_address,
  ADD COLUMN IF NOT EXISTS hotel_fssai VARCHAR(30) NULL AFTER hotel_gstin;
